# Layer C — Dataset Binding  🚧 NOT YET IMPLEMENTED

This reference is a **stub**. Layer C is not yet bundled into this skill.

## What Layer C will be

The per-dataset binding the agent builds at runtime from a Kobo/ODK XLS (the
`survey` and `choices` sheets). For every substantive survey question it records:

- the variable name and section
- the Layer A sector/subpillar it serves (from Step 1 routing)
- the Layer B indicator it maps to (if any)
- a **coverage verdict**: `direct` / `partial component` / `absent`
- notes on what the question can and cannot prove

The output is the honest picture of what *this specific instrument* supports —
including the gaps (an indicator the question implies but the survey never measures).

## Until it's implemented

Do not attempt to bind a dataset or assert coverage verdicts. After Step 2, state
that instrument binding is not yet implemented and stop.

## Porting notes (for whoever implements this)

Reference implementation and schema live in the parent project:
`05_layer_c__end_to_end/` (instrument map + gap analysis) and
`06_discipline_prompt/output/layer_c_schema.md` (the reusable schema and the
build procedure the agent follows). Layer C is built fresh per dataset — it is the
thin, project-specific layer — so this ships as *instructions for building it*, not
as static data.
