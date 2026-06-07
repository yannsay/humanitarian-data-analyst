# Step 4 — Analysis  🚧 NOT YET IMPLEMENTED

This reference is a **stub**. The analysis layer is not yet bundled.

## What Step 4 will be

The grounded answer to the analyst's original question, produced only after Layers
A–C have run. Its defining property is **discipline under coverage**: every claim is
caveated by the Layer C verdict that supports it.

- Report what the bound dataset supports, with the relevant numbers.
- Flag explicitly what the data cannot prove (the Layer C `absent` / `partial` gaps).
- Cite the Layer B definition and threshold for any indicator or cutoff used —
  never assert a threshold without its source.
- Commit to one coherent analytical angle grounded in what the instrument supports,
  rather than offering the analyst a menu of options to choose from.

## Until it's implemented

Stop after the last implemented step and tell the analyst what the full pipeline
would do next.

## Porting notes (for whoever implements this)

The discipline prompt and analytical-spec approach live in the parent project:
`06_discipline_prompt/output/discipline_prompt.md` and
`07_step07_analysis_pipeline/` (where the agent writes its own analysis spec before
running numbers). The core finding to preserve: the agent must be *forced* to
consult the lower layers — passive context does not change generative behaviour.
