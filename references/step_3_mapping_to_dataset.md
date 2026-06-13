# Step 3 — Analysis Spec Build Guide

Detailed reference for **Step 3 — Mapping indicators to the dataset**. Read it when you need more than the procedure
in `SKILL.md`. The exact output format (the YAML contract, the `dimension` rule, the
verdict rules) is in `bindings/schema.md`.

## What the Step 3 binding is — and why it's different from Steps 1 and 2

The Step 1 framework and the Step 2 catalog are **static data shipped with the skill**.
The Step 3 binding is **generated at runtime**, fresh for every dataset, because it depends
on the specific Kobo/ODK instrument the analyst brings. There is nothing to "look up" — you
*build* it.

The binding is the **analysis spec**: the gated plan that says, before any number is
computed, exactly what the analysis will and will not produce. It answers three
questions about the instrument:

1. What can this instrument actually prove, per catalog indicator? (`measurable` verdict)
2. Where would a naive analyst overclaim? (`reasons` / `forbid` / `caveat_field`)
3. What did the instrument collect that no catalog indicator can interpret? (`uncovered_modules`)

## The one principle: YAML is the spec, markdown is its view

Author the spec **as YAML first** (`analysis_spec_<slug>.yaml`), then generate the
markdown from it with `scripts/render_spec.py`. The markdown is **never** hand-written
or hand-edited. This is what will let `verify_spec.py` (planned) certify the spec
against the catalog before any computation.

```
propose bindings  →  analysis_spec_<slug>.yaml   (the spec — source of truth)
        │
   render_spec.py →  analysis_spec_<slug>.md      (human view — generated, do not edit)
        │
   analyst reviews the .md, signs off
        │
   Step 4 reads the .yaml                          (never the .md)
```

If the analyst asks for a change, edit the `.yaml` and re-render. Never patch the `.md`.

## Reading a Kobo/ODK XLS — use the cache script and query modes

Sheet names vary across deployments. Always run two phases, then query by slice:

**Phase 1 — inspect sheets:**
```
python3 scripts/read_kobo.py <dataset>.xlsx --list-sheets
```

**Phase 2 — parse (once per run):**
```
python3 scripts/read_kobo.py <dataset>.xlsx --slug <slug> \
    [--survey-sheet "<name>"] [--choices-sheet "<name>"]
```
Structural rows (begin_group, note, calculate…) are excluded by default. This writes
`kobo_<slug>.json` next to the dataset. Do not call `load_workbook` inline — one parse
per run.

**Phase 3 — query by slice (per indicator):**
```
# Orientation — cheap, run once after parse:
python3 scripts/read_kobo.py --cache kobo_<slug>.json --summary

# Fetch specific variables + their choice lists:
python3 scripts/read_kobo.py --cache kobo_<slug>.json --names q85,q87,q88
```

**Never read the whole `kobo_<slug>.json` into context.** Use `--summary` for
orientation (returns all question names, ~200 bytes), then `--names` for the specific
variables each indicator needs. Reading the full cache (~50–100 KB) for a handful of
lookups wastes context budget unnecessarily.

The underlying XLSForm structure: `survey` sheet has `type`, `name` (variable),
`label`, `relevant` (skip logic). `choices` sheet groups options by `list_name`.
`select_one foo` draws from the `foo` list.

## The binding: indicators → dataset variables

Work indicator-first (not question-first): for each indicator id from Step 2, find the
survey variable(s) that feed it and assign the **`measurable` verdict**:

| Verdict (YAML) | Display label | Meaning |
|---|---|---|
| `MEASURABLE` | Measurable | Instrument directly measures this indicator at the required unit of analysis |
| `PROXY` | Proxy | Instrument provides a community-level or ordinal estimate, not the full indicator |
| `NOT_MEASURABLE` | Not measurable | Indicator cannot be derived from this instrument in any form |

The verdict rules are in `bindings/schema.md`. The most common real-world case in KI
community surveys is `PROXY`: the instrument asks a key informant for a community
estimate where the indicator is defined at household level. That is Proxy, not
Measurable — saying otherwise is exactly the overclaim the Step 3 binding exists to catch.

Note: use `MEASURABLE`/`PROXY`/`NOT_MEASURABLE` in the YAML spec. `render_spec.py` converts
them to display labels automatically.

Pull each indicator's `definition` **verbatim from the catalog** (fetched in Step 2 via
`get_indicators.py`) — never paraphrase.

**Every indicator id in the spec must be an id present in `catalog/index.yaml`.** If a
survey module has no matching catalog indicator, record it in `uncovered_modules:` rather
than inventing an id.

**`result_ids` must match the verdict.** A Proxy row lists only the proxy result id(s)
consistent with its `max_output` — not the full ladder of rung ids it cannot compute.
Not measurable rows list no `result_ids` (and the rendered cell is blank).

**Variables named in `reasons` must equal the `variables` list.** Cross-check against
the kobo cache before writing the row.

## Always state what the binding cannot prove

The `reasons` field must say what the binding *blocks*, not only what it proves — for
every indicator, including Measurable ones. A Measurable FCS question still cannot prove
*why* consumption is low, or trends over time from a single round.

## §1 grouping: one table per dimension — NO pillar table

Group by `dimension`: `sector::X`, plus any `cross_cutting::X` lens. Do not create a
pillar/subpillar table. The pillar/subpillar route is recorded in the `step1_framework_route`
header. Each indicator appears once. Within each table, rows are sorted
Measurable → Proxy → Not measurable (by `render_spec.py` automatically).

## Disaggregation is its own block

A top-level `disaggregation:` block — groups, `source_variables`, and the `trigger`
phrase. The rendered §1b states a pooled figure is not acceptable.

## Gates are the pass criteria

The `gates:` list is what must hold before Step 4 ships (e.g. "tanker_truck never
classified unimproved", "no Sphere compliance claim", "every indicator reported by
group"). Each renders as a `☐` row in §2.

## Not measurable indicators are the hard boundary

An indicator with `measurable: NOT_MEASURABLE` is a documented blind spot — recorded so the gap
is visible, but **Step 4 must never report it as a finding**.

## Worked reference

`12_layout_exploration/output/format_examples/format_1_REVISED_contract.yaml` is a full
spec for the Aleppo RNA (133-interview KI community WASH case);
`…/format_1_REVISED_analysis_spec.md` is its rendered view.
`05_layer_c__end_to_end/` in the parent project has the original instrument-level
binding analysis for the same dataset.
