# Layer B — Indicator Catalog  🚧 NOT YET IMPLEMENTED

This reference is a **stub**. The Layer B indicator catalog is not yet bundled into
this skill.

## What Layer B will be

A catalog of humanitarian indicators (drafted from authoritative sources — JMP, the
FSL Handbook, CAMP-EN, Sphere, IPC, INEE, the IASC Humanitarian Indicators Registry)
with, per indicator:

- `definition` and computation formula
- `unit`, disaggregations
- `thresholds` (e.g. Sphere minimums, IPC phase cutoffs, JMP service ladder rungs)
- `common_implementation_errors` — the mistakes assessments actually make
- `ki_assessment_note` — what a key-informant survey can and cannot establish for it

Example indicators: FCS, rCSI, HHS, HDDS (food security); JMP water/sanitation
service ladders (WASH); habitable-shelter and NFI criteria (shelter).

## Until it's implemented

After Step 1 routes a question to an in-scope sector, **name** the indicators that
would be consulted (e.g. "this would draw on FCS and rCSI from Layer B"), state that
the catalog is not yet bundled, and **stop**. Do not state indicator definitions,
formulas, or thresholds from memory — fabricated thresholds are exactly the error
class this skill exists to prevent.

## Porting notes (for whoever implements this)

Source material lives in the parent project:
`02_layer_b__indicator_extraction/output/catalog/` (index.yaml + per-sector files:
wash.yaml, food_security.yaml, cccm.yaml). Current real coverage is WASH, Food
Security, and CCCM — that defines the "in scope" set the Step 1 routing table flags.
Mirror the Layer A pattern: a compact `catalog/index.yaml` routing surface plus
per-indicator files loaded on demand.
