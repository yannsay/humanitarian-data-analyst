#!/usr/bin/env python3
"""
read_kobo.py — parse a Kobo/ODK XLSForm and write a normalised JSON cache.

Sheet names and formats vary across deployments. The script therefore works in
two phases:

  Phase 1 (--list-sheets):  Read and print the workbook's sheet names as JSON.
                             Pass the output to the LLM so it can identify which
                             sheet is the survey, which is choices, and (optionally)
                             which is a data/response sheet.

  Phase 2 (default):        Read the sheets the LLM identified and write the cache.
                             Pass --survey-sheet and --choices-sheet to override the
                             defaults ('survey' / 'choices').

Usage:
    # Phase 1 — inspect sheets, then decide which to pass to Phase 2
    python3 scripts/read_kobo.py <dataset>.xlsx --list-sheets

    # Phase 2 — parse with explicit sheet names
    python3 scripts/read_kobo.py <dataset>.xlsx --slug <slug> \\
        --survey-sheet "Survey" --choices-sheet "Choices"

    # Phase 2 — with optional data sheet for n_total (omit if no data sheet)
    python3 scripts/read_kobo.py <dataset>.xlsx --slug <slug> \\
        --survey-sheet "Survey" --choices-sheet "Choices" \\
        --data-sheet "Clean Dataset"

Output (Phase 2): kobo_<slug>.json in the same folder as the input file (or -o path).

JSON shape:
  {
    "source_file": "<filename>",
    "sheet_names": [...],          # all sheets in the workbook
    "survey_sheet": "Survey",      # the sheet actually read
    "choices_sheet": "Choices",
    "n_total": 133,                # null if no data sheet specified or no data rows
    "skipped_rows": 0,
    "survey": [
      {"type": "select_one foo", "name": "var_name", "label": "Question text",
       "relevant": "...", "list_name": "foo", "is_structural": false}
    ],
    "choices": {
      "list_name": [{"name": "opt", "label": "Option label"}, ...]
    }
  }
"""
import argparse
import json
import os
import re
import sys

try:
    import openpyxl
except ImportError:
    sys.exit("read_kobo.py requires openpyxl: pip3 install openpyxl --break-system-packages")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_sheet(wb, name):
    """Return sheet by exact name (case-insensitive). Raises KeyError if absent."""
    lower_map = {s.lower(): s for s in wb.sheetnames}
    key = name.lower()
    if key not in lower_map:
        available = ", ".join(f"'{s}'" for s in wb.sheetnames)
        sys.exit(f"read_kobo.py: sheet '{name}' not found. Available: {available}")
    return wb[lower_map[key]]


def _header_map(ws):
    """Return {col_index: header_text} from the first non-empty row."""
    for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
        if any(c is not None for c in row):
            return {i: (str(c).strip() if c is not None else "") for i, c in enumerate(row)}
    return {}


def _find_col(headers, *candidates):
    """First header index matching any candidate (case-insensitive)."""
    lower = {v.lower(): k for k, v in headers.items()}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None


def _label_col(headers):
    """Detect the English label column: 'label', 'label::English*', or first 'label*'."""
    for idx, h in headers.items():
        if h.lower() == "label":
            return idx
    for idx, h in headers.items():
        if re.match(r"label::english", h.lower()):
            return idx
    for idx, h in headers.items():
        if h.lower().startswith("label"):
            return idx
    return None


# ---------------------------------------------------------------------------
# Phase 1 — list sheets
# ---------------------------------------------------------------------------

def list_sheets(xlsx_path):
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    result = {
        "source_file": os.path.basename(xlsx_path),
        "sheet_names": wb.sheetnames,
        "instruction": (
            "Pass --survey-sheet and --choices-sheet to read_kobo.py, "
            "optionally --data-sheet for n_total. "
            "Omit --data-sheet if no response dataset is present."
        )
    }
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Phase 2 — parse
# ---------------------------------------------------------------------------

def parse_kobo(xlsx_path, slug, survey_sheet_name, choices_sheet_name, data_sheet_name):
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    sheet_names = wb.sheetnames

    # ---- survey sheet ----
    survey_ws = _get_sheet(wb, survey_sheet_name)
    rows = list(survey_ws.iter_rows(values_only=True))
    if not rows:
        sys.exit("read_kobo.py: survey sheet is empty")

    headers = _header_map(survey_ws)
    type_col  = _find_col(headers, "type")
    name_col  = _find_col(headers, "name")
    label_col = _label_col(headers)
    rel_col   = _find_col(headers, "relevant")

    if type_col is None or name_col is None:
        sys.exit(f"read_kobo.py: survey sheet '{survey_sheet_name}' missing 'type' or 'name' column. "
                 f"Columns found: {list(headers.values())}")

    STRUCTURAL = {"begin_group", "end_group", "begin_repeat", "end_repeat",
                  "note", "calculate", "hidden", "start", "end", "deviceid",
                  "simserial", "phonenumber", "username", "audit"}

    survey_rows = []
    skipped = 0
    for row in rows[1:]:
        try:
            type_val = str(row[type_col]).strip() if row[type_col] is not None else ""
            name_val = str(row[name_col]).strip() if row[name_col] is not None else ""
            if not type_val and not name_val:
                continue  # blank row

            label_val = ""
            if label_col is not None and label_col < len(row) and row[label_col] is not None:
                label_val = str(row[label_col]).strip()
            relevant_val = ""
            if rel_col is not None and rel_col < len(row) and row[rel_col] is not None:
                relevant_val = str(row[rel_col]).strip()

            list_name = None
            m = re.match(r"select_(one|multiple)\s+(\S+)", type_val, re.IGNORECASE)
            if m:
                list_name = m.group(2)

            base_type = type_val.split()[0].lower() if type_val else ""
            is_structural = base_type in STRUCTURAL

            entry = {
                "type": type_val,
                "name": name_val,
                "label": label_val,
                "relevant": relevant_val,
                "is_structural": is_structural,
            }
            if list_name:
                entry["list_name"] = list_name
            survey_rows.append(entry)
        except Exception:
            skipped += 1

    # ---- choices sheet ----
    choices = {}
    if choices_sheet_name:
        choices_ws = _get_sheet(wb, choices_sheet_name)
        ch_rows = list(choices_ws.iter_rows(values_only=True))
        if ch_rows:
            ch_headers = _header_map(choices_ws)
            ln_col = _find_col(ch_headers, "list_name", "list name")
            cn_col = _find_col(ch_headers, "name")
            cl_col = _label_col(ch_headers)

            if ln_col is not None and cn_col is not None:
                for row in ch_rows[1:]:
                    try:
                        ln  = str(row[ln_col]).strip() if row[ln_col]  is not None else ""
                        cn  = str(row[cn_col]).strip() if row[cn_col]  is not None else ""
                        clv = ""
                        if cl_col is not None and cl_col < len(row) and row[cl_col] is not None:
                            clv = str(row[cl_col]).strip()
                        if ln and cn:
                            choices.setdefault(ln, []).append({"name": cn, "label": clv})
                    except Exception:
                        pass

    # ---- data/response sheet — count rows (optional) ----
    n_total = None
    if data_sheet_name:
        data_ws = _get_sheet(wb, data_sheet_name)
        data_rows = list(data_ws.iter_rows(values_only=True))
        if len(data_rows) > 1:
            n_total = sum(1 for r in data_rows[1:] if any(c is not None for c in r))
        else:
            n_total = 0

    result = {
        "source_file": os.path.basename(xlsx_path),
        "sheet_names": sheet_names,
        "survey_sheet": survey_sheet_name,
        "choices_sheet": choices_sheet_name,
        "n_total": n_total,
        "skipped_rows": skipped,
        "survey": survey_rows,
        "choices": choices,
    }
    if slug:
        result["slug"] = slug
    return result


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=(
            "Phase 1: --list-sheets to inspect sheet names. "
            "Phase 2: parse with explicit --survey-sheet / --choices-sheet."
        )
    )
    ap.add_argument("xlsx", help="Path to the Kobo/ODK .xlsx file")
    ap.add_argument("--list-sheets", action="store_true",
                    help="Phase 1: print sheet names as JSON and exit")
    ap.add_argument("--slug", default=None,
                    help="Short identifier (used in output filename)")
    ap.add_argument("--survey-sheet", default="survey",
                    help="Name of the survey sheet (default: 'survey')")
    ap.add_argument("--choices-sheet", default="choices",
                    help="Name of the choices sheet (default: 'choices')")
    ap.add_argument("--data-sheet", default=None,
                    help="Name of the response/data sheet for n_total (omit if absent)")
    ap.add_argument("-o", "--out", default=None,
                    help="Output JSON path (default: kobo_<slug>.json beside the xlsx)")
    a = ap.parse_args()

    if a.list_sheets:
        list_sheets(a.xlsx)
        return

    slug = a.slug or os.path.splitext(os.path.basename(a.xlsx))[0]
    out_path = a.out or os.path.join(
        os.path.dirname(os.path.abspath(a.xlsx)), f"kobo_{slug}.json"
    )

    data = parse_kobo(
        a.xlsx, slug,
        survey_sheet_name=a.survey_sheet,
        choices_sheet_name=a.choices_sheet,
        data_sheet_name=a.data_sheet,
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    n_survey = sum(1 for r in data["survey"] if not r["is_structural"])
    print(f"wrote {out_path}")
    print(f"  n_total={data['n_total']}  survey_questions={n_survey}  "
          f"choice_lists={len(data['choices'])}  skipped_rows={data['skipped_rows']}")


if __name__ == "__main__":
    main()
