# Contributing

## Repo layout

This repository **is** the skill — `SKILL.md` sits at the root, per the
[Agent Skills spec](https://agentskills.io/specification). The skill activates when
an agent's task matches the `description` in `SKILL.md`'s frontmatter.

## The ontology is generated, not hand-edited

`ontology/` (the `index.yaml` + per-node files + `_axis.yaml`) was generated from
the upstream per-node draft YAMLs in `09_full_layer_a_implementation/`. **Do not
edit `ontology/` files by hand** — update the source drafts and regenerate using the
build script in that folder.

## Validate before you push

Use the agentskills reference validator to check the frontmatter and conventions.
Run it from the **parent** directory and pass the skill's folder name — not `.`,
which resolves to an empty basename and fails the directory-name check:

```bash
cd ..
skills-ref validate humanitarian-data-analyst
```

CI runs this on every push and PR (see `.github/workflows/validate.yml`).

## Implementing a step (currently Step 4 — Analysis is a stub)

Steps 1–3 are implemented; Step 4 (Analysis) is a stub. To implement it (or to
extend an earlier step):

1. Replace the relevant `references/step_*.md` stub (e.g. `references/analysis.md`)
   with the real guide.
2. For a data-bearing step (like the Step 2 catalog), mirror the Step 1 framework
   pattern: a compact `index.yaml` routing surface + per-item files loaded on demand.
   Keep `SKILL.md` thin — it conducts; the heavy material lives in resource files
   loaded only when that step runs.
3. Flip the step's status marker in `SKILL.md` from 🚧 to ✅.

## Provenance

Cite sources for any data you add. The Step 1 framework cites HumSet — see
`references/SOURCES.md`.
