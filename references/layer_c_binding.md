# Layer C — Analysis Spec Build Guide

Detailed reference for **Step 3 — Bind**. Read it when you need more than the procedure
in `SKILL.md`. The exact output format (the YAML contract, the `dimension` rule, the
verdict rules) is in `bindings/schema.md`.

## What Layer C is — and why it's different from A and B

Layers A and B are **static data shipped with the skill**. Layer C is **generated at
runtime**, fresh for every dataset, because it depends on the specific Kobo/ODK
instrument the analyst brings. There is nothing to "look up" — you *build* it.

Layer C is no longer a passive instrument inventory. It is the **analysis spec**: the
gated plan that says, before any number is computed, exactly what the analysis will and
will not produce. It answers three questions about the instrument:

1. What can this instrument actually prove, per Layer B indicator? (`measurable` verdict)
2. Where would a naive analyst overclaim? (`reasons` / `forbid` / `caveat_field`)
3. What did the instrument collect that no Layer B indicator can interpret? (`NONE`)

## The one principle: YAML is the spec, markdown is its view

Author the spec **as YAML first** (`analysis_spec_<slug>.yaml`), then generate the
markdown from it with `scripts/render_spec.py`. The markdown is **never** hand-written
or hand-edited. This is not cosmetic: it is what will let `verify_spec.py` (planned)
certify the spec against the catalog before any computation — if the prose were authored
first, certification would mean parsing LLM prose back into structure, the exact
fragility the verifier exists to remove.

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
The analyst does not need to understand the split — they just sign off on the rendered
markdown.

## Reading a Kobo/ODK XLS — use the cache script

Sheet names and formats vary across deployments. Always run two phases:

**Phase 1 — inspect sheets:**
```
python3 scripts/read_kobo.py <dataset>.xlsx --list-sheets
```
This prints the workbook's sheet names as JSON. Read the output to identify the survey
sheet, choices sheet, and (if present) a response/data sheet. Many instrument-only
files have no response sheet — `n_total` will be null, which is fine.

**Phase 2 — parse:**
```
python3 scripts/read_kobo.py <dataset>.xlsx --slug <slug> \
    --survey-sheet "<name>" --choices-sheet "<name>"
    [--data-sheet "<name>"]   # only if a response sheet exists
```
This writes `kobo_<slug>.json` next to the dataset. Read that JSON for **all**
subsequent instrument lookups. Do not call `load_workbook` / `read_excel` inline again —
one parse per run is the contract.

The JSON contains `survey` (one entry per row, including structural rows tagged
`is_structural: true`), `choices` (keyed by `list_name`), `n_total` (null if no data
sheet), and `sheet_names`. See `scripts/read_kobo.py` docstring for the full shape.

The underlying XLSForm structure for reference: the `survey` sheet has `type`,
`name` (variable), `label`, and `relevant` (skip logic). The `choices` sheet groups
options by `list_name`. `select_one foo` draws its options from the `foo` list.

## The binding: indicators → dataset variables

Work indicator-first (not question-first): for each Step-2 indicator, find the survey
variable(s) that feed it and assign the **`measurable` verdict** (`DIRECT` / `PROXY` /
`NONE`). The verdict rules are in `bindings/schema.md` — apply them strictly. The most
common real-world case in KI community surveys is `PROXY`: the instrument asks a key
informant for a community estimate where the indicator is defined at household level.
That is a PROXY, not a DIRECT — saying otherwise is exactly the overclaim Layer C exists
to catch.

Pull each indicator's `definition` **verbatim from the catalog** — never paraphrase. The
definition is what the analyst signs off against and what `verify_spec.py` string-matches.

**Every indicator id in the spec must be an id present in `catalog/index.yaml`.** If a
survey module has no matching catalog indicator, record it in the spec's
`uncovered_modules:` block (module name + variables + "no Layer B indicator") rather than
inventing a new id. Inventing an indicator id or writing a definition not copied verbatim
from the catalog is a hard error.

**`result_ids` must match the binding verdict.** A PROXY row lists only the proxy
result id(s) consistent with its stated `max_output`, not the full ladder of rung ids it
explicitly cannot compute. If `reasons`/`max_output` say a rung distribution is
impossible, those rung ids must not appear in `result_ids`. `NONE` rows list no
`result_ids`.

**Variables named in `reasons` must equal the `variables` list.** Cross-check against
`kobo_<slug>.json` before writing the row. If the prose in `reasons` describes question X
but `variables` lists question Y, resolve the discrepancy — the binding's prose and the
bound variable must agree.

## Always state what the binding cannot prove

The `reasons` field must say what the binding *blocks*, not only what it proves — for
every indicator, including `DIRECT` ones. This is not boilerplate; it is the field that
forces honest scoping. A DIRECT FCS question still cannot prove *why* consumption is low,
or trends over time from a single round.

## §1 grouping: one table per dimension — NO pillar table

Group indicators by `dimension`: `sector::X`, plus any `cross_cutting::X` lens. **Do not
create a pillar/subpillar table.** In the catalog every indicator shares the same 2D
anchor (`humanitarian_conditions / living_standards`, except `rcsi`), so grouping by
pillar would only duplicate the sector table. The pillar/subpillar route is recorded in
the `layer_a_route` header. Each indicator appears **once**, under its own dimension —
there is no inherit-and-cross-reference case. (See journal Step 14 for why.)

## Disaggregation is its own block

Disaggregation (e.g. by site type, by displacement status) is a top-level
`disaggregation:` block, **not** a per-indicator column — its groups, `source_variables`,
and the `trigger` phrase from the question. The rendered §1b states that a single pooled
figure per indicator is not acceptable; every table must carry every group.

## Gates are the pass criteria

The `gates:` list is what must hold before Step 4 ships a report (e.g. "tanker_truck
never classified unimproved", "no Sphere compliance claim", "every indicator reported by
group"). Each renders as a `☐` row in §2. They generalise the Step-07 S1–S5 checks and
are what `verify_spec.py` will eventually enforce.

## NONE indicators are the hard boundary

An indicator with `measurable: NONE` is a documented blind spot: it is recorded in the
spec so the gap is visible, but **Step 4 must never report it as a finding**, no matter
how relevant to the analyst's question.

## Worked reference

`12_layout_exploration/output/format_examples/format_1_REVISED_contract.yaml` is a full
spec for the Aleppo RNA (133-interview KI community WASH-in-displacement-sites case);
`…/format_1_REVISED_analysis_spec.md` is its rendered view. Use them as the model for
structure, the `dimension` convention, and verdict calls.
`05_layer_c__end_to_end/` in the parent project has the original instrument-level
binding analysis for the same dataset.
