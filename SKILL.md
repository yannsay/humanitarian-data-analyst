---
name: humanitarian-data-analyst
description: >-
  Disciplined analysis of humanitarian needs-assessment data (Kobo/ODK surveys,
  RNA/MSNA/HNO datasets). Runs a four-step pipeline — route questions to the
  HumSet/DEEP analytical framework (Step 1), identify the relevant indicators in
  the catalog (Step 2), bind them to the actual dataset and surface coverage gaps
  (Step 3), then produce grounded analysis. Use when an analyst asks a question about a
  humanitarian survey, assessment, or needs dataset, or mentions RNA, MSNA,
  HNO, Kobo, ODK, sectors like WASH / Food Security / Protection, or humanitarian
  indicators such as FCS, rCSI, JMP water ladder, or Sphere thresholds.
license: see LICENSE
metadata:
  author: Yann Say
  version: "0.4.0"
  framework: HumSet/DEEP
  status: "Steps 1–3 implemented (deterministic selection, sliced catalog, per-indicator bind loop); analysis step is a stub"
---

# Humanitarian Data Analyst

A worked example of a disciplined pipeline for rigorous analysis of humanitarian
needs-assessment data — one reference method, not the only way to do this. It
sits between an analyst's free-text question and a raw survey, and walks four
steps in order. Each step narrows from "what is this question about" down to
"what can this specific dataset actually prove."

The pipeline exists because generic LLM analysis of humanitarian data makes
**attention and instruction errors** — it knows the correct methodology but skips
it under the pressure of answering. This skill's job is to **force the consult
step**: the analytical framework and indicator definitions only help if the agent
is made to read them before writing. Do not answer from memory. Walk the steps.

## When to use this skill

Activate when the analyst's request involves humanitarian assessment data, e.g.:

- "What are the main water access challenges in this dataset?"
- "Build me a food-security analysis from this Kobo export."
- "Which questions in this survey measure shelter adequacy?"
- Any mention of RNA/MSNA/HNO, Kobo/ODK, or humanitarian indicators.

If the request is not about humanitarian needs data, do not use this skill.

## The four-step pipeline

Run these **in order**. Do not skip ahead.

```
Analyst question + dataset (Kobo/ODK XLS)
      │
  STEP 1 — Understanding the question       → sectors / pillars / subpillars  [LLM]
      │
  STEP 2 — Searching the validated          → run select_indicators.py → fixed id list  [SCRIPT]
            indicator catalog               → run get_indicators.py → sliced definitions  [SCRIPT]
      │
  STEP 3 — Mapping indicators to            → per-indicator loop: query dataset → verdict  [LLM+SCRIPT]
            the dataset                     ← HARD STOP: present spec, wait for explicit approval
      │
  STEP 4 — Analysis                         → grounded answer, caveated by coverage  [LLM]
```

**Steps 1–3 run without stopping for the analyst.** They are internal pipeline
stages. Do not ask the analyst to confirm or pause between them. The single review
gate is after Step 3, when the finished spec is presented.

Each step emits **one compact trace line** to chat (see output contracts below);
the full detail lives in the spec and in the on-disk checklist. The per-step
detail tables are not printed in chat unless the analyst asks.

---

## Context discipline — never read whole large files

**This rule applies to every step. Large files must be reached only through scripts.**

| File | Size | How to access |
|------|------|---------------|
| `catalog/*.yaml` cluster files | 30–85 KB each | `get_indicators.py --ids …` only |
| `kobo_<slug>.json` cache | ~50–100 KB | `read_kobo.py --summary` then `--names …` |
| rendered `analysis_spec_*.md` | ~30 KB | do not re-Read after writing |
| `catalog/index.yaml` | ~25 KB | `select_indicators.py` reads it internally |

Do **not** `Read` a whole `catalog/*.yaml`, the whole `kobo_*.json`, or re-`Read`
a spec you just wrote. A run that compacts context mid-pipeline has failed its
context budget — the scripts exist precisely to prevent that.

---

## Before you start: build the checklist

This skill **opens by writing a checklist to disk and mirroring it as a task list**,
then iterates through it. Do this before any routing — it makes a run re-enterable
after `/clear` and stops the pipeline from skipping a step.

**On the first turn of a new analysis:**

1. Pick a short kebab `<question-slug>` from the analyst's question.
2. Copy `templates/checklist.md` into the **analyst's working folder** (next to their
   dataset — not the skill directory, which may be read-only) as
   `analysis_<question-slug>_checklist.md`. Fill in the header (verbatim question,
   dataset path, date).
3. Create an in-session task list with **one task per pipeline step**, using these
   names in order: "Understanding the question", "Searching the validated indicator
   catalog", "Mapping indicators to the dataset", "Analysis".
4. Begin Step 1 immediately — no pause.

**On every later turn (including after `/clear`):**

1. Look for an `analysis_*_checklist.md` in the working folder. If one exists, read
   it, find the first unchecked `[ ]` line, and report: *"Resuming `<slug>` — next
   step: **<step>**."* Rebuild the task list accordingly.
2. If none exists, treat it as a new analysis (above).

Keep exactly one step `in_progress`; when a step's checklist boxes are all `[x]`,
mark its task `completed` and move on. The checklist on disk is authoritative.

---

## STEP 1 — Understanding the question  ✅ implemented

Map the analyst's question to the HumSet/DEEP analytical framework. This step's
only job is to **classify the question** into sector / pillar / subpillar using the
ontology. It does **not** open the dataset and does **not** decide indicator
relevance — those are Steps 2 and 3.

Read `ontology/index.yaml` (66 nodes, each with a `gist` and `synonyms`), match the
question's topics to candidate nodes, then **open each candidate's file and read its
`distinguish_from` before committing** — sibling confusion (`Living Standards` vs
`Physical And Mental Well Being` vs `Impact On People`) is the most common routing
error. The 1D and 2D axes are orthogonal; a question can carry both.

**Read `references/step_1_understanding_the_question.md` before routing.** Do not route from memory.

### Output contract — Step 1 trace (one line)

```
Step 1 — Understanding the question: in scope → <sectors>; out of scope → <sectors or "none">.
```

The indicator catalog (Step 2) covers **WASH, Food Security, and Shelter (CCCM)** only.
Sectors outside this set are marked out of scope. Write full routing detail to the checklist;
do not print it to chat unless asked.

---

## STEP 2 — Searching the validated indicator catalog  ✅ implemented

**The indicator set is determined by a script, not by LLM judgment.** This is the
change that makes the pipeline stable: the same route always produces the same
indicator list, because the script's sector-intersection logic is deterministic.

**Procedure:**

1. **Run `select_indicators.py`** with the sectors and subpillars from Step 1:
   ```
   python3 scripts/select_indicators.py \
       --sectors <sector1> "<sector2>" ... \
       [--subpillars <subpillar_id> ...]
   ```
   Read the JSON output. The `selected` array is the **complete, fixed candidate
   indicator id list** for this run. Carry it forward verbatim — do not add,
   remove, or reorder indicators. Subpillars are used for ordering only, never
   for filtering.

2. **Run `get_indicators.py`** to fetch the binding-relevant fields for those ids:
   ```
   python3 scripts/get_indicators.py --ids <id1> <id2> ...
   ```
   This returns `definition`, `formula`, `thresholds`, `common_implementation_errors`,
   and `ki_assessment_note` — the fields Step 3 needs — **without** loading whole
   cluster YAML files into context. **Reading `common_implementation_errors` is the
   non-negotiable step**: the documented RNA errors (rCSI, JMP water ladder, Sphere,
   FCS absence) were all in that list and were missed by analyses that didn't consult it.

3. Do **not** `Read` `catalog/index.yaml` or any `catalog/*.yaml` cluster file directly.
   The catalog enters context only through the two scripts above.

**Read `references/step_2_indicator_catalog.md`** for the catalog structure and scope boundary.

### Output contract — Step 2 trace (one line)

```
Step 2 — Searching the validated indicator catalog: <N> indicators found (<n1> <Sector1>, <n2> <Sector2>, ...); definitions + known errors read.
```

Write the full indicator list (id, label, cluster, errors to avoid) to the checklist;
do not print it to chat unless asked.

---

## STEP 3 — Mapping indicators to the dataset  ✅ implemented

Produce the **analysis spec**: the gated, reviewable plan that drives Step 4, bound to
*this specific survey* and the catalog indicators from Step 2. The binding is **generated
at runtime** from the analyst's Kobo/ODK file — it is the audit trail of what this
dataset can and cannot prove, and the contract Step 4 executes against.

**YAML-first.** Author the spec as `.yaml` (source of truth), then render `.md` with
a script. Never hand-write the `.md`. The analyst signs off on the `.md`; Step 4 reads
the `.yaml`.

**Procedure:**

**3a. Parse the instrument (once only).**

- **Phase 1 — inspect:** `python3 scripts/read_kobo.py <dataset>.xlsx --list-sheets`
  → prints sheet names. Identify survey, choices, and (if present) data sheet.
- **Phase 2 — parse:** `python3 scripts/read_kobo.py <dataset>.xlsx --slug <slug>
  [--survey-sheet "<name>"] [--choices-sheet "<name>"] [--data-sheet "<name>"]`
  → writes `kobo_<slug>.json` (structural rows excluded by default). **Do not call
  `load_workbook` / `read_excel` inline again — one parse per run.**
- If no dataset was provided, stop and ask for it.

**3b. Per-indicator bind loop.** For each indicator id in the Step-2 `selected` list,
bind it to the survey in this order:

1. **Fetch this indicator's candidate variables.** Use the kobo cache via query mode —
   not by reading the whole file:
   - First (once per run, after parse): `read_kobo.py --cache kobo_<slug>.json --summary`
     to get an orientation map of all question names. This is the only allowed whole-cache
     read, and it is cheap (~200 bytes output).
   - Per indicator: `read_kobo.py --cache kobo_<slug>.json --names <q1>,<q2>,...`
     to retrieve just the variables relevant to this indicator plus their choice lists.
2. **Decide the binding verdict** (`Measurable` / `Proxy` / `Not measurable`) using the indicator's
   `definition`, `common_implementation_errors`, and `ki_assessment_note` from Step 2,
   plus the actual question text and choices from the kobo query. Apply the rules in
   `bindings/schema.md`.
3. **Write the `reasons` field** (what the data proves / what it cannot prove) and the
   `result_ids` (proxy result ids for Proxy; empty for Not measurable). `result_ids` must
   match the verdict: if `reasons` says a rung distribution is impossible, those rung ids
   must not appear.
4. **Pull the `definition` verbatim from the catalog** (it was fetched in Step 2 by
   `get_indicators.py`). Never paraphrase.

After the loop, emit one progress line per indicator *as each verdict is decided* —
use the indicator's human label and the bound variable(s):

```
Step 3 — Mapping indicators to the dataset:
  JMP Water Safely Managed → main_water_source_now … Proxy
  JMP Water Basic → main_water_source_now … Proxy
  Food Consumption Score → (no dietary-recall question) … Not measurable
  Reduced Coping Strategies Index → food_access_cope … Proxy
  …
```

Format: `  <label> → <comma-joined variables, or "(no <reason>)" when Not measurable> … <verdict>`

**Errors to pre-empt (from `common_implementation_errors`):**
- Every indicator id must be an id present in `catalog/index.yaml`. If a survey module
  has no matching catalog indicator, record it under `uncovered_modules:` — do not invent
  a new id.
- In the YAML spec, use the internal values `MEASURABLE`, `PROXY`, `NOT_MEASURABLE` for the
  `measurable` field (render_spec.py converts them to the display labels Measurable / Proxy /
  Not measurable automatically).

**3c. Write the YAML spec.** Save `analysis_spec_<slug>.yaml` into the analyst's working
folder, following `templates/analysis_spec.yaml`. Group by `dimension` (`sector::X` or
`cross_cutting::X`); record uncovered modules, disaggregation block, and gates.

**3d. Render the MD.** Run:
```
python3 scripts/render_spec.py analysis_spec_<slug>.yaml -o analysis_spec_<slug>.md
```
`render_spec.py` sorts each sector's rows MEASURABLE→PROXY→NOT_MEASURABLE then id-ascending, so the
rendered MD is canonical regardless of YAML insertion order. Do not hand-edit the MD.

**3e. Present and STOP.** Show the rendered spec and end your turn. Do **not** begin
Step 4. Step 4 runs **only** after the analyst gives an explicit affirmative approval
("approved", "looks good, go ahead"). Silence, a thumbs-up, an unrelated follow-up, or
a request for a change do **not** count. On any change: edit the YAML, re-render, present
again, stop again.

See `references/step_3_mapping_to_dataset.md` for the full build guide and `bindings/schema.md`
for the YAML contract, verdict rules, and `dimension` rule.

### Output contract — Step 3 trace + spec

After the per-indicator progress lines, emit one summary trace line, then the rendered MD:

```
Step 3 — Mapping indicators to the dataset: wrote analysis_spec_<slug>.yaml + .md  ·  <N> mapped  ·  Not measurable: <list>  ·  uncovered modules: <list or "none">
```

Then present the full `.md`. Then end your turn and wait for explicit approval.

---

## STEP 4 — Analysis  🚧 stub

**Gate:** Do not run Step 4 without explicit analyst approval of the Step 3 spec.

When built, Step 4 reads `analysis_spec_<slug>.yaml` (not the markdown), runs only
Measurable and Proxy indicators, never computes a Not measurable indicator, cites
catalog definitions for any threshold, and checks every gate before emitting.
See `references/analysis.md`.

---

## Scope boundary

Does not invent indicator definitions, does not assert thresholds from memory, and
does not produce analysis the bound dataset cannot support. When a step is not yet
implemented, say so and stop at the last good step.

## Provenance

The Step 1 analytical framework is derived from the HumSet/DEEP analytical framework
(Data Friendly Space / The DEEP), built from saturation sampling over ~150K human-tagged
humanitarian excerpts. Each node carries `excerpt_count` and `saturation_batches` for audit.
