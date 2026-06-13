# Step 3 binding — Analysis Spec Schema

The exact format for what Step 3 produces. It writes a **gated analysis spec**: the reviewable
plan that drives Step 4.

**The `.yaml` is the spec (source of truth); the `.md` is generated from it by
`scripts/render_spec.py` and is never hand-written or hand-edited.** Step 4 reads the
`.yaml`; the analyst signs off on the `.md`. If the YAML changes, re-render — do not
patch the markdown.

Both files go in the analyst's working folder (next to their dataset):
`analysis_spec_<question-slug>.yaml` and `analysis_spec_<question-slug>.md`.

## The YAML contract (canonical — author this first)

One entry per indicator, de-duplicated. Field order per indicator mirrors the rendered
columns: `<result_id>` (map key) · dimension · definition · measurable · reasons ·
variables.

```yaml
dataset: <slug>
unit_of_analysis: <household | key_informant | facility | mixed>
n_total: <int>
disaggregation:                      # its own block — never a per-row column
  by: <variable-derived grouping, e.g. site_type>
  groups: { <group>: <n>, ... }
  source_variables: [<var>, ...]
  trigger: <phrase in the question that required it, or "analyst-specified">
step1_framework_route:               # from Step 1 (the analytical framework)
  sector: <ID>
  pillar_2d: <ID>
  subpillar_2d: <ID>
  cross_cutting: <ID or null>
step2_catalog_version: <catalog date>

indicators:
  <result_id>:                       # the indicator id as it appears in the analysis
    dimension: <sector::X | cross_cutting::X>   # see "Dimensions" below
    definition: "<verbatim from the indicator catalog (Step 2)>"
    measurable: <MEASURABLE | PROXY | NOT_MEASURABLE>
    reasons: "<what the binding proves / blocks>"
    variables: [<dataset var>, ...]  # variable names from the instrument
    # optional, when useful to the analysis:
    result_ids: [<id>, ...]          # if one binding yields several catalog ids
    max_output: <the most the data legitimately supports>
    forbid: [<claim the analysis must not make>, ...]
    caveat_field: <catalog field to quote under the rendered table>
    rules: { <key>: <value>, ... }   # classification rules a gate enforces,
                                      # e.g. tanker_truck: improved  (enforced by G1)

gates:                               # pass-criteria; all must hold before Step 4 ships
  - id: G1
    assert: "<machine-checkable condition>"
  - ...
```

## Dimensions — what groups the §1 tables

Group by **sector**, plus any **cross-cutting lens**. **There is no pillar/subpillar
table.** In the indicator catalog every indicator shares the same 2D anchor
(`humanitarian_conditions / living_standards`, except `rcsi` which is
`…_coping_mechanisms`), so a "by pillar" table would only duplicate the sector table.
The pillar/subpillar route is recorded in the spec **header** (`step1_framework_route`), not as
a grouping.

So `dimension` takes the form `sector::<SECTOR>` (e.g. `sector::WASH`) or
`cross_cutting::<LENS>` (e.g. `cross_cutting::CCCM`). Each indicator appears **once**,
under its own dimension. There is no inherit-and-cross-reference case.

## The `measurable` verdict rules

The surfaced column is named **Measurable** — it answers *can this catalog
indicator be measured from this instrument?* The internal YAML values map to display
labels as: `MEASURABLE` → Measurable, `PROXY` → Proxy, `NOT_MEASURABLE` → Not measurable.

**`MEASURABLE`** — use only when ALL hold:
- collects the exact construct the indicator requires (correct unit, recall period, response format);
- at the correct unit of analysis (household for household indicators, site for community indicators);
- answer options map to the indicator's required categories without transformation.

**`PROXY`** — use when:
- same construct, different format (ordinal band vs measured quantity; presence/absence vs frequency); OR
- different unit of analysis (KI community estimate for a household indicator); OR
- one or more required criteria missing (e.g. source type present but collection time absent).

**`NOT_MEASURABLE`** — the question maps to no catalog indicator, or the indicator is requested
but the instrument cannot compute it. A `NOT_MEASURABLE` indicator is recorded (it is a documented
blind spot) but **Step 4 must never report it as a finding**.

The `reasons` field is where "what this binding proves / blocks" goes — every entry,
including `MEASURABLE`, must say what it *cannot* prove. That is the field that forces honest
scoping.

**`result_ids` constraint:** list only the outputs the binding can actually produce given
its `measurable` verdict and `max_output`. A `PROXY` that yields a source-type prevalence
or an ordinal estimate lists the **proxy** result id, not the full ladder of rung ids it
explicitly cannot compute. If `reasons`/`max_output` say a rung distribution is
impossible, its rung ids must **not** appear in `result_ids`. `NOT_MEASURABLE` rows list no
`result_ids`.

## The rendered markdown (generated by `render_spec.py` — do not author by hand)

The renderer emits exactly these sections, and nothing else:

- **Header** — title (`# Analysis Spec — <dataset>`), the status line
  (unit_of_analysis · step2_catalog_version · n), the **Route** line
  (Sector · Pillar · Subpillar · Cross-cutting — this is where pillar/subpillar live),
  and `☐ DRAFT → ☐ REVIEWED → ☐ APPROVED → ☐ ANALYSIS RUN`.
- **§1 Coverage map** — one table per dimension that carries indicators (one per sector;
  plus one per cross-cutting lens). Columns:
  **Indicator | Definition (catalog) | Measurable | Reasons (proves / blocks) |
  Variables in the dataset | Indicator name in the analysis**.
- **§1b Disaggregation** — its own section: the groups table, source variables, the
  trigger line, and the "pooled figure not acceptable" rule.
- **§2 Pass criteria — gates** — one `☐` row per `gates[]` entry.

> The renderer does **not** emit prose "errors pre-empted" or "WILL / WILL NOT"
> sections. Those existed in an early hand-written mock-up but are not generated; if
> wanted later they must be driven from YAML fields first (a top-level `errors:` list and
> per-indicator `max_output`/`forbid`) and the renderer extended. Treat that as a
> separate, optional enhancement.

A worked example lives in
`12_layout_exploration/output/format_examples/format_1_REVISED_contract.yaml` (the spec)
and `…/format_1_REVISED_analysis_spec.md` (its rendered view).
