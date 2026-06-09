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
  version: "0.1.0"
  framework: HumSet/DEEP
  status: "Layers A, B, C implemented; analysis step is a stub"
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

Run these **in order**. Do not skip ahead. Each step writes a short, visible
output before the next begins.

```
Analyst question + dataset (Kobo/ODK XLS)
      │
  STEP 1 — ROUTE        (Layer A)  → which sectors / pillars / subpillars?
      │
  STEP 2 — INDICATORS   (Layer B)  → which indicators answer it? prerequisites?
      │
  STEP 3 — BIND         (Layer C)  → map survey questions → indicators; gaps
      │
  STEP 4 — ANALYSE                 → grounded answer, caveated by coverage
```

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
4. Then begin Step 1.

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

Map the analyst's question to the HumSet/DEEP analytical framework. This is a
**classification and scope-gating** step — it decides what the question is about
and whether the rest of the pipeline can serve it. It is not where analysis
happens.

**Procedure — follow exactly:**

1. **Read the index.** Open `ontology/index.yaml`. It lists all 66 nodes across 5
   axes with a one-line `gist` and `synonyms`. This is your routing surface.
2. **Match.** For each distinct topic in the question, find candidate nodes by
   matching against `gist` and `synonyms`. A question usually lands on **one
   sector** plus **one or more subpillars** (the 1D and 2D axes are orthogonal —
   the same question can carry both a "type of information" and an "analytical
   lens" tag).
3. **Disambiguate — do not skip.** Before committing to a node, open its full
   file (the `file:` path in the index) and read its `distinguish_from` field.
   Sibling confusion (e.g. `Living Standards` vs `Physical And Mental Well Being`
   vs `Impact On People`) is the most common routing error. `distinguish_from`
   exists to resolve exactly these.
4. **Emit the routing table** (see contract below).

See `references/layer_a_routing.md` for the full routing guide, axis definitions,
the 1D/2D orthogonality rule, and worked examples.

### Output contract — the routing table

Render Step 1 as a compact table and nothing more analytical than this:

```
STEP 1 — ROUTE (Layer A)

| Topic (from question)        | Sector        | Pillar                  | Subpillar              | In Layer B scope? |
|------------------------------|---------------|-------------------------|------------------------|-------------------|
| water access in IDP camps    | WASH          | Humanitarian Conditions | Living Standards       | yes               |
| ...                          | ...           | ...                     | ...                    | yes/partial/no    |

Out-of-scope sectors: <list any sectors the pipeline can't serve, or "none">
```

`In Layer B scope?` flags whether Step 2 can proceed for that topic. Layer B
currently covers three sectors — **WASH, Food Security, and Shelter (CCCM)**. If a
topic routes to any other sector, mark it `no` and say so plainly rather than
inventing indicator analysis for it.

---

## STEP 2 — INDICATORS (Layer B)  ✅ implemented

For each in-scope sector from Step 1, identify the humanitarian indicators that
answer the question and read their full definitions **from the catalog** — never
from memory.

Layer B covers three sectors: **WASH, Food Security, and Shelter (CCCM)** — 41
indicators total. A topic that routed to any other sector in Step 1 is out of Layer
B scope; say so and do not invent indicator analysis for it.

**Procedure — follow exactly:**

1. **Open `catalog/index.yaml`.** It lists all 41 indicators with `id`, `label`,
   `cluster`, `synonyms`, and a `layer_a_anchor` (the sector / pillar / subpillar
   IDs that tie each indicator back to Layer A).
2. **Select by anchor.** Keep the indicators whose `layer_a_anchor.sectors` (and,
   where it sharpens the match, `subpillars_2d`) overlap the IDs you routed to in
   Step 1. This is the A→B wire: the routed Layer A IDs select the indicators.
3. **Read the full entry — do not skip.** For each selected indicator, open its
   cluster file (`catalog/<cluster>.yaml`, where `<cluster>` is `food_security`,
   `wash`, or `cccm`) and read its `definition`, `formula`, `thresholds`,
   `components`, and especially `common_implementation_errors` **before** you use
   the indicator in any later step. Quoting a threshold without reading its catalog
   entry is the exact failure this skill exists to prevent.
4. **Emit the indicator list** (see contract below), carrying each indicator's `id`
   forward — Step 3 binds survey questions to these IDs.

See `references/layer_b_indicators.md` for the catalog structure, the anchor-matching
rules, and the scope boundary.

### Output contract — the indicator list

```
STEP 2 — INDICATORS (Layer B)

| Indicator (id) | Label                         | Cluster        | Answers (link to question) | Prerequisites to compute            |
|----------------|-------------------------------|----------------|----------------------------|-------------------------------------|
| rcsi           | Reduced Coping Strategies Idx | food_security  | how families cope w/ food  | 5 standard rCSI coping-freq questions |
| ...            | ...                           | ...            | ...                        | ...                                 |

Errors to avoid (from catalog common_implementation_errors): <pull the relevant ones verbatim>
```

---

## STEP 3 — BIND (Layer C)  ✅ implemented

Build the **instrument map**: the binding between *this specific survey* and the
Layer B indicators from Step 2. Unlike Layers A and B, Layer C is **not shipped
data — you generate it at runtime** from the analyst's Kobo/ODK file. It is the
audit trail that says what this dataset can and cannot prove, and it must be saved
to disk before Step 4 runs.

**Procedure — follow exactly:**

1. **Read the instrument.** Open the Kobo/ODK XLS the analyst provided — the
   `survey` sheet (questions, types, skip logic) and the `choices` sheet (answer
   options). If no dataset was provided, stop and ask for it; Layer C cannot be
   built without the instrument.
2. **Walk every substantive question.** Skip pure admin fields (`calculate`,
   `note`, `begin_group`/`end_group`) unless they carry analytical content. For
   each substantive question, write one entry using the schema in
   `bindings/schema.md`.
3. **Bind to Layer B.** For each question, record the Layer B indicator `id`(s)
   from Step 2 it serves (or `NONE`), and assign a **coverage verdict**:
   - `DIRECT` — collects the exact construct the indicator needs (right unit,
     recall period, response format), at the right unit of analysis.
   - `PROXY` — same construct but different format/unit, or missing one required
     criterion (e.g. KI community estimate standing in for a household measure).
   - `NONE` — does not map to any Layer B indicator.
   Every entry — even `DIRECT` — must state **what it cannot prove**.
4. **Surface the two gap lists.** (a) survey questions no Layer B indicator can
   interpret; (b) Layer B indicators (from Step 2) the instrument cannot compute.
   These are the analytical blind spots Step 4 must respect.
5. **Save it.** Write the map to the analyst's working folder as
   `layer_c_<survey>_<YYYY-MM-DD>.md`. This file is required before Step 4.

See `references/layer_c_binding.md` for the full build guide and `bindings/schema.md`
for the exact per-question entry format and the verdict rules.

### Output contract — the instrument map (saved file + short in-chat summary)

The saved file follows `bindings/schema.md`. In chat, show only a compact summary:

```
STEP 3 — BIND (Layer C)  →  saved: layer_c_<survey>_<date>.md

| Indicator (from Step 2) | Computable here? | Binding questions | Verdict |
|-------------------------|------------------|-------------------|---------|
| rcsi                    | yes (proxy)      | Q90 coping freq   | PROXY   |
| jmp_water_basic         | no               | —                 | NONE    |

Blind spots: <indicators that can't be computed; survey questions with no indicator>
```

---

## STEP 4 — ANALYSE  🚧 stub

Produce the grounded answer, explicitly caveated by the Layer C coverage verdicts:
report what the data supports, flag what it cannot, and cite indicator definitions
for any threshold used. **Not yet implemented.** See `references/analysis.md`.

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
