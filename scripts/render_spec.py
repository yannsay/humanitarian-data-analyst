#!/usr/bin/env python3
"""
render_spec.py — deterministic YAML -> Markdown renderer for the Layer C analysis spec.

The YAML spec is the source of truth. This script ONLY formats what the spec already
contains: no LLM, no catalog lookups, no network. Catalog/instrument certification is
verify_spec.py's job and runs BEFORE this (journal Step 13). render_spec.py assumes a
clean spec and fails loudly on a malformed one.

Usage:
    render_spec.py <spec>.yaml [-o <out>.md]

Reference output: 12_layout_exploration/output/format_examples/format_1_REVISED_analysis_spec.md
"""
import argparse
import sys
import yaml

def cell(text):
    """Make a value safe for a single Markdown table cell.
    Collapses all whitespace (including newlines from YAML block scalars) to single spaces
    and escapes pipes so they don't split the cell.
    """
    if text is None:
        return "—"
    s = str(text)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = " ".join(s.split())        # collapse all whitespace runs (incl. newlines) to single spaces
    s = s.replace("|", "\\|")      # escape pipes so they don't split the cell
    return s or "—"


DIM_LABEL = {
    "sector": "Sector",
    "pillar": "Pillar (2D)",
    "subpillar": "Subpillar (2D)",
    "cross_cutting": "Cross-cutting lens",
}

COLS = (
    "| Indicator | Definition (catalog) | Measurable | Reasons (proves / blocks) "
    "| Variables in the dataset | Indicator name in the analysis |"
)
SEP = "|---|---|---|---|---|---|"


def die(msg):
    sys.stderr.write(f"render_spec.py: {msg}\n")
    sys.exit(1)


def require(spec, key):
    if key not in spec:
        die(f"required key '{key}' missing from spec")
    return spec[key]


def fmt_vars(v):
    return ", ".join(f"`{x}`" for x in v.get("variables", [])) or "—"


def fmt_result_id(result_id, v):
    ids = v.get("result_ids")
    if ids:
        return ", ".join(f"`{i}`" for i in ids)
    return f"`{result_id}`"


def dim_key(dim):
    # "sector::WASH" -> ("sector", "WASH")
    base = dim.split("::", 1)[0]
    return base, dim


def render(spec):
    out = []
    src = spec.get("_source_file", "<spec>.yaml")
    out.append(f"<!-- generated from {src} — do not edit by hand -->")
    out.append("")
    out.append(f"# Analysis Spec — {require(spec, 'dataset')}")
    out.append("")
    out.append(f"**Unit of analysis:** {spec.get('unit_of_analysis', '—')} · "
               f"**Layer B version:** {spec.get('layer_b_version', '—')} · "
               f"**n:** {spec.get('n_total', '—')}")
    route = spec.get("layer_a_route", {})
    if route:
        out.append(f"**Route:** Sector `{route.get('sector','—')}` · "
                   f"Pillar `{route.get('pillar_2d','—')}` · "
                   f"Subpillar `{route.get('subpillar_2d','—')}`"
                   + (f" · Cross-cutting `{route['cross_cutting']}`"
                      if route.get("cross_cutting") else ""))
    out.append("**Status:** ☐ DRAFT → ☐ REVIEWED → ☐ APPROVED → ☐ ANALYSIS RUN")
    out.append("")
    out.append("---")
    out.append("")

    # ---- §1 coverage map, one table per dimension present on the indicators ----
    # Indicators are grouped by their `dimension` (sector::X or cross_cutting::X).
    # The pillar/subpillar route is recorded in the header, NOT as a table: in this
    # catalog every indicator shares one pillar/subpillar anchor, so a pillar table
    # would only duplicate the sector table. There is therefore no inheritance to
    # cross-reference — each indicator simply appears once under its own dimension.
    out.append("## 1. Coverage map — by Layer A dimension")
    out.append("")
    out.append("*One table per dimension that carries indicators (sector, plus any "
               "cross-cutting lens). The pillar/subpillar route is in the header above. "
               "Each indicator appears once.*")
    out.append("")

    indicators = require(spec, "indicators")
    # Group by full dimension string; sort within each group DIRECT→PROXY→NONE then id asc.
    # This makes the rendered MD canonical regardless of YAML insertion order (D13).
    MEASURABLE_RANK = {"DIRECT": 0, "PROXY": 1, "NONE": 2}

    order = []
    by_dim = {}
    for rid, v in indicators.items():
        dim = v.get("dimension", "sector::?")
        _, full = dim_key(dim)
        by_dim.setdefault(full, []).append((rid, v))
        if full not in order:
            order.append(full)

    # Sort each dimension's indicators: DIRECT first, then PROXY, then NONE, then id asc
    for full in order:
        by_dim[full].sort(
            key=lambda rv: (MEASURABLE_RANK.get(rv[1].get("measurable", ""), 9), rv[0])
        )

    for section, full in enumerate(order, start=1):
        base, _ = dim_key(full)
        label = DIM_LABEL.get(base, base)
        out.append(f"### 1.{section} {label} — `{full.split('::', 1)[1]}`")
        out.append("")
        out.append(COLS)
        out.append(SEP)
        for rid, v in by_dim[full]:
            out.append(
                "| " + cell(v.get('label', rid))
                + " | " + cell(v.get('definition', '—'))
                + " | " + cell(v.get('measurable', '—'))
                + " | " + cell(v.get('reasons', '—'))
                + " | " + fmt_vars(v)
                + " | " + fmt_result_id(rid, v) + " |"
            )
        out.append("")

    # ---- §1c uncovered modules ----
    uncovered = spec.get("uncovered_modules")
    if uncovered:
        section_count = len(order) + 1
        out.append(f"### 1.{section_count} Survey modules with no Layer B indicator")
        out.append("")
        out.append("| Module | Variables | Note |")
        out.append("|---|---|---|")
        for entry in uncovered:
            mod = cell(entry.get("module", "—"))
            vars_str = ", ".join(f"`{v}`" for v in entry.get("variables", [])) or "—"
            note = cell(entry.get("note", "no Layer B indicator"))
            out.append(f"| {mod} | {vars_str} | {note} |")
        out.append("")

    # ---- §1b disaggregation ----
    dis = spec.get("disaggregation")
    if dis:
        out.append("---")
        out.append("")
        out.append("## 1b. Disaggregation required")
        out.append("")
        out.append("Report **every indicator row above separately** for:")
        out.append("")
        groups = dis.get("groups", {})
        srcs = ", ".join(f"`{s}`" for s in dis.get("source_variables", []))
        # Only show n column if at least one group has a real count
        has_counts = any(v is not None for v in groups.values())
        if has_counts:
            out.append("| Group | n | Source variable |")
            out.append("|---|---|---|")
            for g, n in groups.items():
                n_val = cell(str(n)) if n is not None else "—"
                out.append(f"| {cell(g)} | {n_val} | {srcs} |")
        else:
            out.append("| Group | Source variable |")
            out.append("|---|---|")
            for g in groups:
                out.append(f"| {cell(g)} | {srcs} |")
        out.append("")
        trig = dis.get("trigger")
        if trig:
            out.append(f"**Trigger:** {cell(trig)}. A single pooled figure per indicator is "
                       f"**not** acceptable — each table must carry every group.")
            out.append("")

    # ---- §2 gates ----
    gates = spec.get("gates", [])
    if gates:
        out.append("---")
        out.append("")
        out.append("## 2. Pass criteria — gates *(all must hold before the report ships)*")
        out.append("")
        out.append("| Gate | Pass condition | ☐ |")
        out.append("|---|---|---|")
        for g in gates:
            out.append(f"| {cell(g.get('id','—'))} | {cell(g.get('assert','—'))} | ☐ |")
        out.append("")

    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    with open(a.spec) as f:
        spec = yaml.safe_load(f)
    if not isinstance(spec, dict):
        die("spec did not parse to a mapping")
    spec["_source_file"] = a.spec.split("/")[-1]
    md = render(spec)
    if a.out:
        with open(a.out, "w") as f:
            f.write(md)
        print(f"wrote {a.out}")
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
