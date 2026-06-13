#!/usr/bin/env python3
"""
select_indicators.py — deterministic indicator selection for Step 2.

Given a Step-1 route (sectors + optional subpillars), returns the fixed set of
catalog indicator ids. No LLM, no judgment — same args → byte-identical output.

The LLM MUST use this script instead of choosing indicators from memory. This is
the single change that removes run-to-run variance in indicator sets.

Usage:
    python3 scripts/select_indicators.py \\
        --sectors WASH "Food Security" Shelter \\
        [--subpillars humanitarian_conditions_living_standards humanitarian_conditions_coping_mechanisms] \\
        [-o selected_indicators_<slug>.json]

Sector matching rules:
    - Case-insensitive; normalised to lowercase with underscores internally.
    - Aliases accepted: "food security" → food_security, "wash" → wash,
      "shelter" → shelter (cccm cluster uses sectors: [shelter]).
    - Inclusion criterion: indicator's step1_framework_anchor.sectors intersects --sectors.
    - Subpillars (optional): used ONLY for ordering/grouping, never to drop indicators.

Output JSON:
    {
      "route": {"sectors": [...], "subpillars": [...]},
      "selected": [
        {"id": "...", "label": "...", "cluster": "...", "priority": true/false},
        ...
      ],
      "count_by_sector": {"WASH": 17, "Food Security": 9, "Shelter": 15}
    }

Determinism contract: output ordering is stable — sort by (sector order as given in
--sectors, then priority desc, then id asc). Two invocations with identical args
produce byte-identical JSON.

Self-test (run with --test):
    Asserts two invocations with the same args produce identical bytes.
"""
import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("select_indicators.py requires pyyaml: pip3 install pyyaml --break-system-packages")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
INDEX_PATH = os.path.join(SKILL_DIR, "catalog", "index.yaml")

# Canonical sector name → normalised key for matching
SECTOR_ALIASES = {
    "food_security":     "food_security",
    "food security":     "food_security",
    "foodsecurity":      "food_security",
    "wash":              "wash",
    "water, sanitation and hygiene": "wash",
    "shelter":           "shelter",
    "shelter/cccm":      "shelter",
    "cccm":              "shelter",
}

# Canonical display name for each normalised sector key
SECTOR_DISPLAY = {
    "food_security": "Food Security",
    "wash":          "WASH",
    "shelter":       "Shelter",
}


def normalise_sector(s: str) -> str:
    """Return the canonical normalised key or the lower-stripped input."""
    key = s.strip().lower()
    return SECTOR_ALIASES.get(key, key)


def load_index() -> list:
    with open(INDEX_PATH, encoding="utf-8") as f:
        entries = yaml.safe_load(f)
    # Filter out comment-only entries (pyyaml returns None for pure-comment docs)
    if entries is None:
        sys.exit(f"select_indicators.py: {INDEX_PATH} parsed as empty")
    return [e for e in entries if isinstance(e, dict) and "id" in e]


def select(sectors_norm: list, subpillars: list, index: list):
    """
    Return list of matching indicator dicts, ordered by:
      (sector_order_index asc, priority desc, id asc)

    sectors_norm: list of normalised sector keys in the order the analyst gave them.
    subpillars: list of subpillar id strings — used for ordering only, never filtering.
    """
    sector_order = {s: i for i, s in enumerate(sectors_norm)}

    matched = []
    for entry in index:
        anchor_sectors = entry.get("step1_framework_anchor", {}).get("sectors", [])
        # normalise anchor sectors for matching
        anchor_norm = [normalise_sector(s) for s in anchor_sectors]
        # check intersection
        if not any(s in sector_order for s in anchor_norm):
            continue
        # pick the first matching sector for ordering
        order_idx = min(
            sector_order[s] for s in anchor_norm if s in sector_order
        )
        matched.append({
            "id": entry["id"],
            "label": entry.get("label", entry["id"]),
            "cluster": entry.get("cluster", ""),
            "priority": bool(entry.get("priority", False)),
            "_order_idx": order_idx,
        })

    # Sort: sector order asc, priority desc (True=1 → negate), id asc
    matched.sort(key=lambda e: (e["_order_idx"], not e["priority"], e["id"]))

    # Strip internal sort key
    selected = [
        {"id": e["id"], "label": e["label"], "cluster": e["cluster"], "priority": e["priority"]}
        for e in matched
    ]
    return selected


def count_by_sector(selected: list, sectors_norm: list) -> dict:
    """Return display-name keyed counts in sector order."""
    counts = {}
    for s in sectors_norm:
        display = SECTOR_DISPLAY.get(s, s)
        counts[display] = sum(
            1 for e in selected
            if normalise_sector(e.get("cluster", "")) == s
            or (s == "shelter" and e.get("cluster") == "cccm")
            or (s == "food_security" and e.get("cluster") == "food_security")
            or (s == "wash" and e.get("cluster") == "wash")
        )
    return counts


def build_result(sectors_raw: list, subpillars: list) -> dict:
    sectors_norm = [normalise_sector(s) for s in sectors_raw]
    index = load_index()
    selected = select(sectors_norm, subpillars, index)
    counts = count_by_sector(selected, sectors_norm)
    return {
        "route": {
            "sectors": sectors_raw,
            "subpillars": subpillars or [],
        },
        "selected": selected,
        "count_by_sector": counts,
    }


def to_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Deterministic indicator selection from Step-1 route."
    )
    ap.add_argument("--sectors", nargs="+", required=True,
                    help="Sectors from Step 1, e.g. WASH 'Food Security' Shelter")
    ap.add_argument("--subpillars", nargs="*", default=[],
                    help="Subpillar ids from Step 1 (ordering only, never filtering)")
    ap.add_argument("-o", "--out", default=None,
                    help="Write JSON to this path (also prints to stdout)")
    ap.add_argument("--test", action="store_true",
                    help="Self-test: assert two runs produce identical bytes, then exit 0")
    a = ap.parse_args()

    if a.test:
        result1 = to_json(build_result(a.sectors, a.subpillars or []))
        result2 = to_json(build_result(a.sectors, a.subpillars or []))
        if result1 != result2:
            sys.exit("FAIL: two invocations produced different output")
        print("PASS: determinism check (two invocations → identical bytes)")
        print(f"  {len(json.loads(result1)['selected'])} indicators selected")
        return

    result = build_result(a.sectors, a.subpillars or [])
    output = to_json(result)

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"wrote {a.out}", file=sys.stderr)

    sys.stdout.write(output)


if __name__ == "__main__":
    main()
