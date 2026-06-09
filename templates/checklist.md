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

## Step 3 — Bind (Layer C)
- [ ] Read the Kobo/ODK survey + choices sheets
- [ ] Wrote one entry per substantive question (per bindings/schema.md)
- [ ] Assigned a coverage verdict (DIRECT/PROXY/NONE) + "cannot prove" for each
- [ ] Listed the two blind-spot sets
- [ ] Saved layer_c_<survey>_<date>.md to the working folder

## Step 4 — Analyse
- [ ] (stub — not yet implemented; stop here and report)
