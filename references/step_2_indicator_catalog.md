# Step 2 — Indicator Catalog Guide

Detailed reference for **Step 2 — Searching the validated indicator catalog**. Read it when you need more than the
procedure in `SKILL.md`.

## What the catalog is

A catalog of 41 humanitarian indicators across three clusters, drafted from
authoritative sources (JMP, the FSL Handbook, Sphere, the Collective Centers /
CAMP-EN standards). Each indicator carries its definition, formula, thresholds,
component questions, sources, and — most important for this skill — its
`common_implementation_errors`.

The catalog answers: *given what this question is about (from the Step 1 framework), which
indicators answer it, and how must they be computed correctly?*

## File layout

```
catalog/
├── index.yaml          # routing surface — all 41 indicators (id, label, cluster, synonyms, step1_framework_anchor)
├── food_security.yaml  # 9 indicators
├── wash.yaml           # 17 indicators
└── cccm.yaml           # 15 indicators (Shelter / camp management)
```

## Scope boundary

The catalog covers **WASH, Food Security, and Shelter (CCCM)** only. The `cccm` cluster
indicators anchor to the **Shelter** sector in the Step 1 framework (HumSet/DEEP has no
separate CCCM sector). A question that routed in Step 1 to Protection, Health, Education,
Nutrition, Livelihoods, Agriculture, Logistics, or Cross is **out of catalog scope**
— say so and stop; do not fabricate indicators for it.

## How selection works: `select_indicators.py`

**Do not select indicators manually.** Run the script with the sectors from Step 1:

```
python3 scripts/select_indicators.py --sectors WASH "Food Security" Shelter
```

The script reads `index.yaml`, keeps every indicator whose `step1_framework_anchor.sectors`
intersects the requested sectors, and returns a sorted JSON list of ids. The result
is deterministic — same route → same list every time. Subpillars can be passed via
`--subpillars` for ordering, but never filter on them (the anchoring is too coarse).

The underlying join logic: every indicator in `index.yaml` has a `step1_framework_anchor`, e.g.:

```yaml
- id: rcsi
  label: "Reduced Coping Strategies Index"
  cluster: food_security
  step1_framework_anchor:
    sectors: [food_security]
    subpillars_2d: [humanitarian_conditions_coping_mechanisms]
  priority: true
```

These anchor IDs match the Step 1 framework ontology IDs exactly.

> Provenance note: anchors were reconciled to the 66-node Step 1 framework. Historical anchors
> were remapped — `living_standards` → `humanitarian_conditions_living_standards`,
> `coping_mechanisms` → `humanitarian_conditions_coping_mechanisms`, the old
> `food_security_and_nutrition` and `access_to_services` subpillars collapsed, and
> `cccm` sector → `shelter`.

## How to read indicator definitions: `get_indicators.py`

**Do not open cluster YAML files directly.** Run:

```
python3 scripts/get_indicators.py --ids rcsi jmp_water_basic fcs ...
```

This returns only the fields needed for binding — `definition`, `formula`, `thresholds`,
`common_implementation_errors`, `ki_assessment_note` — for exactly the requested ids.
Reading a whole cluster file (wash.yaml = 85 KB, cccm.yaml = 65 KB) for a handful of
indicators wastes context budget and is unnecessary.

## The non-negotiable step: read `common_implementation_errors`

The catalog's value is not the definition — the model often knows that. It is the
**error list**. For every selected indicator, read `common_implementation_errors` before
binding. The four documented RNA errors (rCSI, JMP water ladder, Sphere thresholds, FCS
absence) were all in this list — and were missed because the analysis didn't consult it.

## What to carry forward

Each selected indicator's `id` is the key Step 3 uses to bind survey questions. The
`select_indicators.py` output is the authoritative id list — carry it forward verbatim.

## Where the indicators come from (provenance)

The catalog is not invented — every indicator is drafted from an authoritative
humanitarian standard, and the citation travels with the entry:

- **Per-cluster header** — the top comment of each `catalog/<cluster>.yaml` names the
  documents it was drafted from (e.g. WASH ← JMP 2018 + Sphere 2018; CCCM ← CAMP-EN 2021
  + Ukraine CC 2022 + Sphere 2018; Food Security ← WFP/FAO/FANTA methodologies).
- **Per-indicator `source:` block** — most entries carry `source.primary` (document,
  table, page), `source.secondary` (e.g. the SDG indicator), and a `source.note`.
  Thresholds and code lists are cited inline in `formula` / `thresholds` /
  `classification_rules` / `common_implementation_errors`.

So when you pull a `definition` verbatim into the Step-3 spec, its source is one field
away in the same entry — quote it under the rendered table (`caveat_field`) or in
`reasons` when the provenance matters to the analyst. **The per-indicator `source:` block
is the source of truth** if it ever disagrees with the index label (a few index labels
were corrected post-drafting — see the `# CORRECTED` notes in `catalog/index.yaml`).

Full provenance summary and citation guidance: `references/SOURCES.md`. The drafting +
sanity-check protocol is in the parent project's `02_layer_b__indicator_extraction/` and
`03_layer_b__catalog_eda_iteration/`.
