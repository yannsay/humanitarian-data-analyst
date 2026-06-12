---
name: humanitarian-data-analyst
description: >-
  Disciplined analysis of humanitarian needs-assessment data (Kobo/ODK surveys,
  RNA/MSNA/HNO datasets). Runs a four-step pipeline — route questions to the
  HumSet/DEEP analytical framework (Layer A), identify the relevant indicators
  (Layer B), bind them to the actual dataset and surface coverage gaps (Layer C),
  then produce grounded analysis. Use when an analyst asks a question about a
  humanitarian survey, assessment, or needs dataset, or mentions REACH, RNA, MSNA,
  HNO, Kobo, ODK, sectors like WASH / Food Security / Protection, or humanitarian
  indicators such as FCS, rCSI, JMP water ladder, or Sphere thresholds.
license: see LICENSE
metadata:
  author: yann
  version: "0.3.0"
  framework: HumSet/DEEP
  status: "Layers A, B, C implemented (Layer C emits a YAML-first analysis spec); analysis step is a stub"
---

# Humanitarian Data Analyst

A pipeline skill for rigorous analysis of humanitarian needs-assessment data. It
sits between an analyst's free-text question and a raw survey, and walks four
layers in order. Each layer narrows from "what is this question about" down to
"what can this specific dataset actually prove."

The pipeline exists because generic LLM analysis of humanitarian data makes
**attention and instruction errors** — it knows the correct methodology but skips
it under the pressure of answering. This skill's job is to **force the consult
step**: the analytical framework and indicator definitions only help if the agent
is made to read them before writing. Do not answer from memory. Walk the layers.

## When to use this skill

Activate when the analyst's request involves humanitarian assessment data, e.g.:

- "What are the main water access challenges in this dataset?"
- "Build me a food-security analysis from this Kobo export."
- "Which questions in this survey measure shelter adequacy?"
- Any mention of REACH/RNA/MSNA/HNO, Kobo/ODK, or humanitarian indicators.

If the request is not about humanitarian needs data, do not use this skill.

## The four-step pipeline

Run these **in order**. Do not skip ahead.

```
Analyst question + dataset (Kobo/ODK XLS)
      │
  STEP 1 — ROUTE        (Layer A)  → which sectors / pillars / subpillars?
      │
  STEP 2 — INDICATORS   (Layer B)  → which indicators answer it?
      │
  STEP 3 — BIND         (Layer C)  → map survey questions → indicators; gaps
      │                             ← HARD STOP: present spec, wait for explicit approval
  STEP 4 — ANALYSE                 → grounded answer, caveated by coverage
```

**Steps 1–3 run without stopping for the analyst.** They are internal pipeline
stages — routing, catalog selection, and binding. Do not ask the analyst to
confirm or pause between them. The single review gate is after Step 3, when the
finished spec is presented.

Each step emits **one compact trace line** to chat (see output contracts below);
the full detail lives in the spec and in the on-disk checklist. The per-step
detail tables are not printed in chat. If the analyst asks to see the routing or
indicator breakdown, render it on request.

---

## Before you start: build the checklist

This skill **opens by writing a checklist to disk and mirroring it as a task list**,
then iterates through it. Do this before any routing — it is what makes a run
re-enterable after `/clear` and what stops the pipeline from skipping a step.

**On the first turn of a new analysis:**

1. Pick a short kebab `<question-slug>` from the analyst's question.
2. Copy `templates/checklist.md` into the **analyst's working folder** (next to their
   dataset — not the skill directory, which may be read-only) as
   `analysis_<question-slug>_checklist.md`. Fill in the header (verbatim question,
   dataset path, date).
3. Create an in-session task list with **one task per pipeline step** (Route,
   Indicators, Bind, Analyse), in order. This mirrors the checklist.
4. Then begin Step 1 immediately — no pause.

**On every later turn (including after `/clear`):**

1. Look for an `analysis_*_checklist.md` in the working folder. If one exists, read
   it, find the first unchecked `[ ]` line, and report: *"Resuming `<slug>` — next
   step: **<step>**."* Rebuild the task list from the checklist (steps with all
   boxes `[x]` → completed; first step with an unchecked box → in_progress).
2. If none exists, treat it as a new analysis (above).

**As you work:** keep exactly one step `in_progress`; when a step's checklist boxes
are all `[x]`, mark its task `completed` and move on. The checklist on disk is
authoritative — the task list is its human-visible mirror, never a replacement. Do
not invoke a step's work before its checklist entry exists.

---

## STEP 1 — ROUTE (Layer A)  ✅ implemented

Map the analyst's question to the HumSet/DEEP analytical framework. This step's
only job is to **classify the question** into sector / pillar / subpillar using the
ontology. It does **not** open the dataset and does **not** decide indicator
relevance — those are Step 2 and Step 3's jobs.

In short: read `ontology/index.yaml` (the routing surface — 66 nodes, each with a
`gist` and `synonyms`), match the question's topics to candidate nodes, then **open
each candidate's file and read its `distinguish_from` before committing** — sibling
confusion (e.g. `Living Standards` vs `Physical And Mental Well Being` vs `Impact On
People`) is the most common routing error. A question usually lands on one sector plus
one or more subpillars; the 1D and 2D axes are orthogonal, so one question can carry
both.

**Read `references/layer_a_routing.md` before routing** — it has the full procedure,
the axis definitions, the 1D/2D orthogonality rule, the `distinguish_from` confusions,
and a worked example. Do not route from memory of the framework.

### Output contract — Step 1 trace (one line)

Emit exactly one line to chat, then proceed immediately to Step 2:

```
Step 1 — Route: in scope → <sectors>; out of scope → <sectors or "none">.
```

Example:
```
Step 1 — Route: in scope → WASH, Food Security, Shelter; out of scope → Health, Protection, Education, Nutrition, Logistics, Displacement, Casualties.
```

Layer B covers **WASH, Food Security, and Shelter (CCCM)** only. If a topic routes
to any other sector, mark it out of scope here and do not invent indicator analysis
for it in Step 2.

Write the full routing detail (topic → sector → pillar → subpillar for each topic)
to the checklist on disk; do not print it to chat unless the analyst asks.

---

## STEP 2 — INDICATORS (Layer B)  ✅ implemented

For each in-scope sector from Step 1, identify the humanitarian indicators that answer
the question and read their full definitions **from the catalog** — never from memory.

Layer B covers three sectors only: **WASH, Food Security, and Shelter (CCCM)** — 41
indicators total. A topic that routed to any other sector in Step 1 is out of scope.

In short: open `catalog/index.yaml` (all 41 indicators with `id`, `cluster`, and a
`layer_a_anchor`), select indicators whose `layer_a_anchor.sectors` overlap the Step-1
route (use `subpillars_2d` to sharpen), then open each selected indicator's cluster
file and read its `definition`, `formula`, `thresholds`, `components`, and especially
`common_implementation_errors`. **Reading `common_implementation_errors` is the
non-negotiable step** — the four documented RNA errors were all in that list and were
missed because the analysis didn't consult it. Carry each indicator's `id` forward;
Step 3 binds survey questions to these IDs. Do **not** look at the dataset here.

**Read `references/layer_b_indicators.md`** for the catalog structure, the A→B anchor
wire, and the scope boundary.

### Output contract — Step 2 trace (one line)

Emit exactly one line to chat, then proceed immediately to Step 3:

```
Step 2 — Indicators: <N> catalog indicators selected (<n1> <Sector1>, <n2> <Sector2>, ...); definitions + common_implementation_errors read.
```

Example:
```
Step 2 — Indicators: 16 catalog indicators selected (9 WASH, 5 Food Security, 2 Shelter); definitions + common_implementation_errors read.
```

Write the full indicator list (id, label, cluster, errors to avoid) to the checklist
on disk; do not print it to chat unless the analyst asks.

---

## STEP 3 — BIND (Layer C)  ✅ implemented

Produce the **analysis spec**: the gated, reviewable plan that drives Step 4, bound to
*this specific survey* and the Layer B indicators from Step 2. Unlike Layers A and B,
Layer C is **not shipped data — you generate it at runtime** from the analyst's Kobo/ODK
file. It is both the audit trail (what this dataset can and cannot prove) and the
contract Step 4 executes against.

**YAML-first — this is the core of the step.** Author the spec as a `.yaml` (the source
of truth), then render the human-readable `.md` from it with a script. Never hand-write
or hand-edit the `.md`. This is what will let `verify_spec.py` (planned) certify the spec
against the catalog before any number is computed; authoring prose first would force
parsing prose back into structure. The analyst signs off on the `.md`; Step 4 reads the
`.yaml`.

**Procedure — follow exactly:**

1. **Parse the instrument once — two phases.** Sheet names and formats vary across
   deployments, so always start with Phase 1:
   - **Phase 1 — inspect:** Run `python3 scripts/read_kobo.py <dataset>.xlsx --list-sheets`.
     This prints the workbook's sheet names as JSON. Read the output to identify which
     sheet is the survey form, which is the choices list, and — only if present — which is
     the response/data sheet. Many instrument-only files have no response data; that is fine.
   - **Phase 2 — parse:** Run `python3 scripts/read_kobo.py <dataset>.xlsx --slug <slug>
     --survey-sheet "<name>" --choices-sheet "<name>"`. Add `--data-sheet "<name>"` only
     if a response sheet was found in Phase 1. This writes `kobo_<slug>.json` next to the
     dataset. Read that JSON for **all** subsequent instrument lookups. Do not call
     `load_workbook` / `read_excel` inline again — one parse per run.
   - If no dataset was provided at all, stop and ask for it; Layer C cannot be built
     without the instrument.
2. **Propose each binding.** For each Step-2 indicator, identify its dataset variable(s)
   from `kobo_<slug>.json`, assign a `measurable` verdict (`DIRECT` / `PROXY` / `NONE`
   per the rules in `bindings/schema.md`), write `reasons` (what it proves / blocks —
   always include what it *cannot* prove), and pull its `definition` **verbatim from the
   catalog** (never paraphrase). **Every indicator id must be an id present in
   `catalog/index.yaml`.** If a survey module has no matching catalog indicator, record it
   in `uncovered_modules:` (see below) — do **not** invent a new indicator id or write a
   definition not copied verbatim from the catalog. That is a hard error.
3. **`result_ids` must match the binding verdict.** A PROXY that yields a source-type
   prevalence or an ordinal estimate lists the **proxy result id**, not the full ladder of
   rung ids it explicitly cannot compute. If `reasons`/`max_output` say a rung distribution
   is impossible, those rung ids must **not** appear in `result_ids`. `NONE` rows list no
   `result_ids`.
4. **Verify internal consistency.** The variable(s) named in `reasons` must equal the
   `variables` list — cross-check against `kobo_<slug>.json` before writing the row.
5. **Write the `.yaml` first.** Save `analysis_spec_<question-slug>.yaml` into the
   analyst's working folder, following `templates/analysis_spec.yaml`. One entry per
   indicator (de-duplicated). Group by `dimension` — `sector::X` or `cross_cutting::X`;
   the pillar/subpillar goes in the `layer_a_route` header, not as a grouping. Record
   uncovered modules under `uncovered_modules:`. Record `disaggregation` as its own block
   and the `gates` that must hold before Step 4 ships.
6. **Render the `.md` from the `.yaml`.** Run
   `python3 scripts/render_spec.py analysis_spec_<slug>.yaml -o analysis_spec_<slug>.md`.
   Do not hand-write or hand-edit this file — it carries a `generated — do not edit`
   header.
7. **Present the `.md` and STOP.** Show the rendered spec to the analyst and end your
   turn. Do **not** begin Step 4. Step 4 runs **only** after the analyst gives an explicit
   affirmative approval (e.g. "approved", "looks good, go ahead"). Silence, a thumbs-up
   with no text, an unrelated follow-up, or a request for a *change* do **not** count as
   approval. On any requested change: edit the `.yaml`, re-render, present again, and STOP
   again. Re-present and wait for explicit approval each time.

See `references/layer_c_binding.md` for the full build guide and `bindings/schema.md`
for the YAML contract, the `dimension` rule, and the verdict rules.

### Output contract — Step 3 trace + spec presentation

Emit one trace line, then present the rendered `.md`:

```
Step 3 — Bind: wrote analysis_spec_<slug>.yaml + .md  ·  <N> indicators bound  ·  NONE blind spots: <list>  ·  uncovered modules: <list or "none">
```

Then show the full rendered `.md`. Then end your turn and wait for explicit approval.

---

## STEP 4 — ANALYSE  🚧 stub

**Gate:** Do not run Step 4 unless the analyst has explicitly approved the spec from
Step 3 in a prior message. If approval is absent, return to the Step 3 sign-off.

Produce the grounded answer, explicitly caveated by the spec. **Not yet implemented.**
When built, Step 4 **reads `analysis_spec_<slug>.yaml`** (not the markdown): it runs
only what `measurable: DIRECT`/`PROXY` permits, **never computes a `NONE` indicator**,
respects every `forbid`, cites the catalog definition for any threshold used, and checks
every `gate` before emitting. The markdown is for humans; the analysis binds to the YAML.
See `references/analysis.md`.

---

## Scope boundary

This skill analyses humanitarian needs data through the HumSet/DEEP framework. It
does not invent indicator definitions, does not assert thresholds from memory, and
does not produce analysis the bound dataset cannot support. When a step is not yet
implemented, say so and stop at the last good step rather than guessing.

## Provenance

Layer A is derived from the HumSet/DEEP analytical framework (Data Friendly Space /
The DEEP), built from saturation sampling over ~150K human-tagged humanitarian
excerpts. Each node carries `excerpt_count` and `saturation_batches` for audit.
