# Analysis Checklist — <question-slug>

Analyst question: <verbatim>
Dataset: <path to Kobo/ODK XLS, or "none provided">
Started: <YYYY-MM-DD>

Mark `[x]` when complete. On resume, find the first `[ ]` line — that is the next
step. This file is the durable record; the in-session task list mirrors it.

## Step 1 — Understanding the question
- [ ] Read ontology/index.yaml
- [ ] Matched each question topic to candidate nodes
- [ ] Read distinguish_from for ambiguous siblings before committing
- [ ] Emitted the routing table (topic → sector → pillar → subpillar)
- [ ] Flagged out-of-scope sectors

## Step 2 — Searching the validated indicator catalog
- [ ] Ran select_indicators.py with routed sectors; carried selected ids forward verbatim
- [ ] Ran get_indicators.py to fetch definitions + common_implementation_errors for selected ids
- [ ] common_implementation_errors read for every selected indicator (non-negotiable)

## Step 3 — Mapping indicators to the dataset
- [ ] Ran read_kobo.py once; using --summary and --names slices for all lookups (no whole-file reads)
- [ ] Per-indicator bind loop: variable(s), verdict (Measurable/Proxy/Not measurable), reasons, verbatim definition
- [ ] Every indicator id verified against catalog/index.yaml (no invented ids)
- [ ] result_ids consistent with verdict (empty for Not measurable rows)
- [ ] variables list matches the variable(s) named in reasons (cross-checked against kobo json)
- [ ] Uncovered modules recorded under uncovered_modules: (not as invented indicators)
- [ ] Wrote analysis_spec_<slug>.yaml (one entry per indicator; disaggregation block; uncovered_modules; gates)
- [ ] Rendered analysis_spec_<slug>.md via scripts/render_spec.py (did NOT hand-edit it)
- [ ] Presented the .md and STOPPED for sign-off (edits go to the .yaml, then re-render)
- [ ] Analyst gave EXPLICIT approval before any Step 4 work

## Step 4 — Analysis
- [ ] (stub — not yet implemented; stop here and report)
