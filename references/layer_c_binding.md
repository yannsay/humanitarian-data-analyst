# Layer C — Dataset Binding Guide

Detailed reference for **Step 3 — Bind**. Read it when you need more than the
procedure in `SKILL.md`. The exact output format is in `bindings/schema.md`.

## What Layer C is — and why it's different from A and B

Layers A and B are **static data shipped with the skill**. Layer C is **generated
at runtime**, fresh for every dataset, because it depends on the specific Kobo/ODK
instrument the analyst brings. There is nothing to "look up" — you *build* it.

Layer C answers three questions about the instrument:
1. What can this instrument actually prove, per Layer B indicator?
2. Where would a naive analyst overclaim?
3. What did the instrument collect that no Layer B indicator can interpret?

It is the audit trail. **Save it to disk before answering anything** (Step 4 reads
it). Filename: `layer_c_<survey>_<YYYY-MM-DD>.md` in the analyst's working folder.

## Reading a Kobo/ODK XLS

A Kobo XLSForm has two sheets that matter:
- **`survey`** — one row per question: `type`, `name` (the variable), `label`,
  and `relevant` (skip logic). Types like `calculate`, `note`, `begin_group`,
  `end_group` are structural — skip them unless they carry analytical content.
- **`choices`** — answer options, grouped by `list_name`; a `select_one foo`
  question in `survey` draws its options from the `foo` list here.

Join them: for each substantive `survey` row, pull its options from `choices` by
list name. (You can read the sheets directly, or use pandas — `pd.read_excel(path,
sheet_name=["survey","choices"])` — whichever is available.)

## The binding: questions → Step-2 indicators

For each question, decide which Layer B indicator(s) from Step 2 it serves, and the
**coverage verdict** (`DIRECT` / `PROXY` / `NONE`). The verdict rules are in
`bindings/schema.md` — apply them strictly. The most common real-world case in KI
community surveys is `PROXY`: the instrument asks a key informant for a community
estimate where the indicator is defined at household level. That is a PROXY, not a
DIRECT — saying otherwise is exactly the overclaim Layer C exists to catch.

## Always state "what this cannot prove"

Every entry, including `DIRECT` ones, must complete the "What this cannot prove"
line. This is not boilerplate — it is the field that forces honest scoping. A
DIRECT FCS question still cannot prove *why* consumption is low, or trends over
time from a single round.

## The two gap lists are the deliverable

End the file with the two blind-spot lists (schema has the format):
1. Survey questions that map to no Layer B indicator — collected but uninterpretable.
2. Step-2 indicators the instrument cannot compute — requested but unanswerable.

Step 4 must treat list 2 as a hard boundary: an indicator that cannot be computed
cannot be reported as a finding, no matter how relevant to the analyst's question.

## Worked reference

`05_layer_c__end_to_end/` in the parent research project contains a full instrument
map for the Aleppo RNA (133-interview KI community survey) built to this schema —
use it as a model for structure and verdict calls.
