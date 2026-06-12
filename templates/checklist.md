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
- [ ] Read the Kobo/ODK survey + choices sheets
- [ ] Proposed each Step-2 indicator's binding: variable(s), measurable verdict
      (DIRECT/PROXY/NONE), reasons, definition verbatim from the catalog
- [ ] Wrote analysis_spec_<slug>.yaml (one entry per indicator; disaggregation block; gates)
- [ ] Rendered analysis_spec_<slug>.md via scripts/render_spec.py (did NOT hand-edit it)
- [ ] Presented the .md to the analyst for sign-off (edits go to the .yaml, then re-render)

## Step 4 — Analyse
- [ ] (stub — not yet implemented; stop here and report)
