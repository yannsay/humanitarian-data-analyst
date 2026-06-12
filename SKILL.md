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
  version: "0.2.0"
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
**classification and scope-gating** step — it decides what the question is about and
whether the rest of the pipeline can serve it. It is not where analysis happens.

In short: read `ontology/index.yaml` (the routing surface — 66 nodes, each with a
`gist` and `synonyms`), match the question's topics to candidate nodes, then **open each
candidate's file and read its `distinguish_from` before committing** — sibling confusion
(e.g. `Living Standards` vs `Physical And Mental Well Being` vs `Impact On People`) is
the most common routing error. A question usually lands on one sector plus one or more
subpillars; the 1D and 2D axes are orthogonal, so one question can carry both.

**Read `references/layer_a_routing.md` before routing** — it has the full procedure, the
axis definitions, the 1D/2D orthogonality rule, the `distinguish_from` confusions, and a
worked example. Do not route from memory of the framework.

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

For each in-scope sector from Step 1, identify the humanitarian indicators that answer
the question and read their full definitions **from the catalog** — never from memory.

Layer B covers three sectors only: **WASH, Food Security, and Shelter (CCCM)** — 41
indicators total. A topic that routed to any other sector in Step 1 is out of scope; say
so and do not invent indicator analysis for it.

In short: open `catalog/index.yaml` (all 41 indicators with `id`, `cluster`, and a
`layer_a_anchor`), select indicators whose `layer_a_anchor.sectors` overlap the Step-1
route (use `subpillars_2d` to sharpen), then open each selected indicator's cluster file
and read its `definition`, `formula`, `thresholds`, `components`, and especially
`common_implementation_errors`. **Reading `common_implementation_errors` is the
non-negotiable step** — the four documented RNA errors were all in that list and were
missed because the analysis didn't consult it. Carry each indicator's `id` forward; Step
3 binds survey questions to these IDs.

**Read `references/layer_b_indicators.md`** for the catalog structure, the A→B anchor
wire, and the scope boundary.

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

1. **Read the instrument.** Open the Kobo/ODK XLS — the `survey` sheet (questions, types,
   skip logic) and the `choices` sheet (answer options). If no dataset was provided,
   stop and ask for it; Layer C cannot be built without the instrument.
2. **Propose each binding.** For each Step-2 indicator, identify its dataset variable(s),
   assign a `measurable` verdict (`DIRECT` / `PROXY` / `NONE` per the rules in
   `bindings/schema.md`), write `reasons` (what it proves / blocks — always include what
   it *cannot* prove), and pull its `definition` **verbatim from the catalog** (never
   paraphrase).
3. **Write the `.yaml` first.** Save `analysis_spec_<question-slug>.yaml` into the
   analyst's working folder, following `templates/analysis_spec.yaml`. One entry per
   indicator (de-duplicated). Group by `dimension` — `sector::X` or `cross_cutting::X`;
   the pillar/subpillar goes in the `layer_a_route` header, not as a grouping. Record
   `disaggregation` as its own block and the `gates` that must hold before Step 4 ships.
4. **Render the `.md` from the `.yaml`.** Run
   `python scripts/render_spec.py analysis_spec_<slug>.yaml -o analysis_spec_<slug>.md`.
   Do not hand-write or hand-edit this file — it carries a `generated — do not edit`
   header.
5. **Present the `.md`** to the analyst for review/sign-off. On any change, edit the
   `.yaml` and re-render — never patch the markdown.

See `references/layer_c_binding.md` for the full build guide and `bindings/schema.md`
for the YAML contract, the `dimension` rule, and the verdict rules.

### Output contract — the analysis spec (saved files + short in-chat summary)

Step 3 writes two files to the working folder: `analysis_spec_<slug>.yaml` (the spec)
and `analysis_spec_<slug>.md` (its rendered view). **The `.yaml` is the spec; the `.md`
is generated from it. Step 4 reads the `.yaml`.** The rendered §1 uses the six-column
layout — Indicator | Definition (catalog) | Measurable | Reasons (proves / blocks) |
Variables in the dataset | Indicator name in the analysis — one table per dimension,
plus the §1b disaggregation block and the §2 gates checklist. In chat, show only a
compact summary:

```
STEP 3 — BIND (Layer C)  →  wrote analysis_spec_<slug>.yaml + .md

| Indicator (from Step 2) | Measurable | Binding variables    |
|-------------------------|------------|----------------------|
| rcsi                    | PROXY      | coping_freq_q90      |
| jmp_water_safely_managed| NONE       | —                    |

Gates: G1..Gn  ·  NONE indicators (blind spots Step 4 must not report): <list>
```

---

## STEP 4 — ANALYSE  🚧 stub

Produce the grounded answer, explicitly caveated by the spec. **Not yet implemented.**
When built, Step 4 **reads `analysis_spec_<slug>.yaml`** (not the markdown): it runs only
what `measurable: DIRECT`/`PROXY` permits, **never computes a `NONE` indicator**, respects
every `forbid`, cites the catalog definition for any threshold used, and checks every
`gate` before emitting. The markdown is for humans; the analysis binds to the YAML. See
`references/analysis.md`.

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
