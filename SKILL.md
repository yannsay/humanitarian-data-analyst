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
  status: "Layers A and B implemented; Layer C and analysis are stubs"
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

## STEP 3 — BIND (Layer C)  🚧 stub

Build the instrument map: walk every substantive question in the survey, map it to
a Layer B indicator, and record a coverage verdict (direct / partial / absent).
The output is the honest picture of what this specific dataset can and cannot
prove. **Not yet implemented.** See `references/layer_c_binding.md`.

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
