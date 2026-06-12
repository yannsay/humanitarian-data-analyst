# Layer B — Indicator Catalog Guide

Detailed reference for **Step 2 — Indicators**. Read it when you need more than the
procedure in `SKILL.md`.

## What Layer B is

A catalog of 41 humanitarian indicators across three clusters, drafted from
authoritative sources (JMP, the FSL Handbook, Sphere, the Collective Centers /
CAMP-EN standards). Each indicator carries its definition, formula, thresholds,
component questions, sources, and — most important for this skill — its
`common_implementation_errors`.

Layer B answers: *given what this question is about (from Layer A), which indicators
answer it, and how must they be computed correctly?*

## File layout

```
catalog/
├── index.yaml          # routing surface — all 41 indicators (id, label, cluster, synonyms, layer_a_anchor)
├── food_security.yaml  # 9 indicators
├── wash.yaml           # 17 indicators
└── cccm.yaml           # 15 indicators (Shelter / camp management)
```

## Scope boundary

Layer B covers **WASH, Food Security, and Shelter (CCCM)** only. The `cccm` cluster
indicators anchor to the **Shelter** sector in Layer A (HumSet/DEEP has no separate
CCCM sector). A question that routed in Step 1 to Protection, Health, Education,
Nutrition, Livelihoods, Agriculture, Logistics, or Cross is **out of Layer B scope**
— say so and stop; do not fabricate indicators for it.

## The A→B wire: `layer_a_anchor`

Every indicator in `index.yaml` has a `layer_a_anchor`, e.g.:

```yaml
- id: rcsi
  label: "Reduced Coping Strategies Index"
  cluster: food_security
  layer_a_anchor:
    sectors: [food_security]
    pillars_2d: [humanitarian_conditions]
    subpillars_2d: [humanitarian_conditions_coping_mechanisms]
  synonyms: [rCSI, reduced coping strategy index, food coping score]
  priority: true
```

These anchor IDs are the **same IDs Layer A's index uses**. So Step 2 selection is a
join: keep indicators whose `layer_a_anchor.sectors` overlaps the sectors you routed
to in Step 1. Use `subpillars_2d` to disambiguate when a sector has many indicators
(e.g. within Food Security, `humanitarian_conditions_coping_mechanisms` selects
rCSI/HHS while `humanitarian_conditions_living_standards` selects FCS/HDDS).

> Provenance note: the anchors were reconciled to the 66-node Layer A. Historical
> anchors were remapped — `living_standards` → `humanitarian_conditions_living_standards`,
> `coping_mechanisms` → `humanitarian_conditions_coping_mechanisms`, the old
> `food_security_and_nutrition` and `access_to_services` subpillars collapsed to
> `humanitarian_conditions_living_standards`, and the `cccm` sector → `shelter`.

## The non-negotiable step: read `common_implementation_errors`

The catalog's value is not the definition — the model often knows that. It is the
**error list**. Before using any indicator (computing it, quoting a threshold,
asserting a cutoff), open its cluster-file entry and read `common_implementation_errors`
and `thresholds`. The four documented RNA errors this project was built around (rCSI,
JMP water ladder, Sphere thresholds, FCS) were all in this list — and were missed
because the analysis didn't consult it. Consulting it is the whole point.

## What to carry forward

Each selected indicator's `id` is the key Step 3 (Layer C) uses to bind survey
questions. Keep the ids in the Step 2 output so the pipeline stays joined.

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
