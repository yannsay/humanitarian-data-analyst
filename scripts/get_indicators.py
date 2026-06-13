#!/usr/bin/env python3
"""
get_indicators.py — sliced catalog accessor for Step 2/3.

Given a list of indicator ids, returns ONLY those catalog entries and ONLY the
fields needed for binding. This is the context fix: instead of the agent reading
whole cluster YAML files (wash.yaml = 85 KB, cccm.yaml = 65 KB), it calls this
script and gets a targeted ~1–3 KB slice per indicator.

The agent MUST use this script to access catalog content during Steps 2 and 3.
It MUST NOT read whole catalog/*.yaml cluster files directly.

Usage:
    python3 scripts/get_indicators.py \\
        --ids rcsi jmp_water_basic jmp_water_safely_managed \\
        [--fields definition,formula,thresholds,common_implementation_errors,ki_assessment_note]

Output JSON (keyed by id):
    {
      "rcsi": {
        "id": "rcsi",
        "label": "Reduced Coping Strategies Index",
        "cluster": "food_security",
        "definition": "...",          # verbatim from catalog
        "common_implementation_errors": [...],
        "ki_assessment_note": "...",
        ...
      },
      ...
    }

If an id is not found in any cluster, it appears in "not_found" list in the response.

Default --fields: definition, formula, thresholds, common_implementation_errors,
                  ki_assessment_note, components_note
(Omits: provenance, synonyms, step1_framework_anchor, full components detail — fields that
 add bulk without helping the binding decision.)
"""
import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("get_indicators.py requires pyyaml: pip3 install pyyaml --break-system-packages")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
CATALOG_DIR = os.path.join(SKILL_DIR, "catalog")
INDEX_PATH = os.path.join(CATALOG_DIR, "index.yaml")

CLUSTER_FILES = {
    "food_security": "food_security.yaml",
    "wash":          "wash.yaml",
    "cccm":          "cccm.yaml",
}

DEFAULT_FIELDS = [
    "definition",
    "formula",
    "thresholds",
    "common_implementation_errors",
    "ki_assessment_note",
    "components_note",
]


def load_index() -> dict:
    """Return {id: {label, cluster, priority}} from index.yaml."""
    with open(INDEX_PATH, encoding="utf-8") as f:
        entries = yaml.safe_load(f)
    if not entries:
        sys.exit(f"get_indicators.py: {INDEX_PATH} is empty")
    return {
        e["id"]: {
            "label": e.get("label", e["id"]),
            "cluster": e.get("cluster", ""),
            "priority": bool(e.get("priority", False)),
        }
        for e in entries if isinstance(e, dict) and "id" in e
    }


def load_cluster(cluster: str) -> dict:
    """Return {id: full_entry} for one cluster YAML."""
    fname = CLUSTER_FILES.get(cluster)
    if not fname:
        return {}
    path = os.path.join(CATALOG_DIR, fname)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        entries = yaml.safe_load(f)
    if not entries:
        return {}
    return {e["id"]: e for e in entries if isinstance(e, dict) and "id" in e}


def project(entry: dict, fields: list) -> dict:
    """Return only the requested fields from an entry (plus id and label always)."""
    out = {"id": entry["id"], "label": entry.get("label", entry["id"])}
    for f in fields:
        if f in entry:
            out[f] = entry[f]
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Return projected catalog entries for a list of indicator ids."
    )
    ap.add_argument("--ids", nargs="+", required=True,
                    help="Indicator ids to fetch, e.g. rcsi jmp_water_basic")
    ap.add_argument("--fields", default=",".join(DEFAULT_FIELDS),
                    help=f"Comma-separated field names to include. Default: {','.join(DEFAULT_FIELDS)}")
    ap.add_argument("-o", "--out", default=None,
                    help="Write JSON to this path (also prints to stdout)")
    a = ap.parse_args()

    fields = [f.strip() for f in a.fields.split(",") if f.strip()]
    requested_ids = a.ids

    index = load_index()

    # Determine which clusters we need and load only those
    clusters_needed = set()
    for iid in requested_ids:
        if iid in index:
            clusters_needed.add(index[iid]["cluster"])

    loaded_clusters: dict[str, dict] = {}
    for c in clusters_needed:
        loaded_clusters[c] = load_cluster(c)

    result = {}
    not_found = []

    for iid in requested_ids:
        if iid not in index:
            not_found.append(iid)
            continue
        cluster = index[iid]["cluster"]
        cluster_data = loaded_clusters.get(cluster, {})
        if iid not in cluster_data:
            not_found.append(iid)
            continue
        entry = cluster_data[iid]
        # Always include cluster and priority from index (may not be in cluster YAML)
        entry_with_meta = dict(entry)
        entry_with_meta.setdefault("label", index[iid]["label"])
        projected = project(entry_with_meta, fields)
        projected["cluster"] = cluster
        projected["priority"] = index[iid]["priority"]
        result[iid] = projected

    output = {"indicators": result}
    if not_found:
        output["not_found"] = not_found

    out_str = json.dumps(output, ensure_ascii=False, indent=2) + "\n"

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"wrote {a.out}", file=sys.stderr)

    sys.stdout.write(out_str)


if __name__ == "__main__":
    main()
