#!/usr/bin/env python3
"""
Self-contained integrity check for the Layer A ontology. Runs in CI without needing
the upstream source drafts. Validates:
  - every index entry resolves to a real file
  - the key in each index entry matches the key inside its node file
  - index node_count == number of entries == number of node files
  - every node file and _axis.yaml parses as YAML
  - each of the 5 axis folders has an _axis.yaml
Exit code 0 = all good, 1 = problems found.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ONT = ROOT / "ontology"
AXES = ["sectors", "pillars_1d", "subpillars_1d", "pillars_2d", "subpillars_2d"]

errors = []


def main():
    if not (ONT / "index.yaml").exists():
        print("FATAL: ontology/index.yaml not found", file=sys.stderr)
        return 1

    idx = yaml.safe_load((ONT / "index.yaml").read_text())

    node_files = [
        p for p in ONT.rglob("*.yaml")
        if p.name not in ("index.yaml", "_axis.yaml")
    ]

    # parse every node file + capture its key
    file_keys = {}
    for p in node_files:
        try:
            d = yaml.safe_load(p.read_text())
        except yaml.YAMLError as e:
            errors.append(f"YAML parse error in {p.relative_to(ROOT)}: {e}")
            continue
        file_keys[p] = set(d.keys())

    # axis files parse + present
    for axis in AXES:
        ax = ONT / axis / "_axis.yaml"
        if not ax.exists():
            errors.append(f"missing _axis.yaml in {axis}/")
        else:
            try:
                yaml.safe_load(ax.read_text())
            except yaml.YAMLError as e:
                errors.append(f"YAML parse error in {axis}/_axis.yaml: {e}")

    # counts
    n_entries = len(idx.get("nodes", []))
    if idx.get("node_count") != n_entries:
        errors.append(f"index node_count ({idx.get('node_count')}) != entries ({n_entries})")
    if n_entries != len(node_files):
        errors.append(f"index entries ({n_entries}) != node files ({len(node_files)})")

    # each entry resolves + key matches
    for n in idx.get("nodes", []):
        f = ROOT / n["file"]
        if not f.exists():
            errors.append(f"index file does not exist: {n['file']}")
            continue
        if n["key"] not in file_keys.get(f, set()):
            errors.append(f"index key {n['key']!r} not found inside {n['file']}")

    if errors:
        print(f"{len(errors)} ISSUE(S):")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK — {n_entries} nodes, all index entries resolve, all YAML parses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
