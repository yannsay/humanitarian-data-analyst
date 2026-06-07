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
  status: "Layer A implemented; Layers B/C/analysis are stubs"
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
currently covers a limited sector set (see Step 2). If a topic routes to a sector
outside that set, mark it `no` and say so plainly rather than inventing indicator
analysis for it.

---

## STEP 2 — INDICATORS (Layer B)  🚧 stub

For each in-scope sector from Step 1, identify the humanitarian indicators that
answer the question (e.g. FCS, rCSI, JMP service ladder), with their definitions,
thresholds, common implementation errors, and what the instrument must contain to
compute them.

**Not yet implemented in this skill.** The indicator catalog (Layer B) is being
ported in a later session. Until then: after Step 1, state which indicators
*would* be consulted and that the catalog is not yet bundled, then stop — do not
fabricate indicator definitions or thresholds from memory. See
`references/layer_b_indicators.md`.

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
