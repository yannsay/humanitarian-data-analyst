# Analysis Checklist — <question-slug>

Analyst question: <verbatim>
Dataset: <path to Kobo/ODK XLS, or "none provided">
Started: <YYYY-MM-DD>

Mark `[x]` when complete. On resume, find the first `[ ]` line — that is the next
step. This file is the durable record; the in-session task list mirrors it.

## Step 1 — Route (Layer A)
- [ ] Read ontology/index.yaml
- [ ] Matched each question topic to candidate nodes
- [ ] Read distinguish_from for ambiguous siblings before committing
- [ ] Emitted the routing table (topic → sector → pillar → subpillar)
- [ ] Flagged out-of-scope sectors

## Step 2 — Indicators (Layer B)
- [ ] Opened catalog/index.yaml
- [ ] Selected indicators by layer_a_anchor overlap with Step 1 IDs
- [ ] Read definition/formula/thresholds/common_implementation_errors in the cluster file
- [ ] Emitted the indicator list, carrying indicator ids forward

## Step 3 — Bind (Layer C) — emit the analysis spec
- [ ] Ran read_kobo.py once; reading kobo_<slug>.json for all instrument lookups
- [ ] Proposed each Step-2 indicator's binding: variable(s), measurable verdict
      (DIRECT/PROXY/NONE), reasons, definition verbatim from the catalog
- [ ] Every indicator id verified against catalog/index.yaml (no invented ids)
- [ ] result_ids consistent with measurable verdict and max_output (no rung fan-out for PROXY/NONE)
- [ ] variables list matches the variable(s) named in reasons (cross-checked against kobo json)
- [ ] Uncovered modules recorded under uncovered_modules: (not as invented indicators)
- [ ] Wrote analysis_spec_<slug>.yaml (one entry per indicator; disaggregation block; uncovered_modules; gates)
- [ ] Rendered analysis_spec_<slug>.md via scripts/render_spec.py (did NOT hand-edit it)
- [ ] Presented the .md and STOPPED for sign-off (edits go to the .yaml, then re-render)
- [ ] Analyst gave EXPLICIT approval before any Step 4 work

## Step 4 — Analyse
- [ ] (stub — not yet implemented; stop here and report)
