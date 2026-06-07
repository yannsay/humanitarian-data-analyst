# Contributing

## Repo layout

This repository **is** the skill — `SKILL.md` sits at the root, per the
[Agent Skills spec](https://agentskills.io/specification). The skill activates when
an agent's task matches the `description` in `SKILL.md`'s frontmatter.

## The ontology is generated, not hand-edited

`ontology/` (the `index.yaml` + per-node files + `_axis.yaml`) is produced by
`scripts/build_layer_a.py` from the upstream per-node draft YAMLs. **Do not edit
`ontology/` files by hand** — change the source drafts and regenerate:

```bash
python3 scripts/build_layer_a.py <path-to>/ontology_drafts ontology
```

Requires Python 3 with `pyyaml`.

## Validate before you push

Use the agentskills reference validator to check the frontmatter and conventions:

```bash
skills-ref validate .
```

CI runs this on every push and PR (see `.github/workflows/validate.yml`).

## Adding a layer (B / C / analysis)

The pipeline steps in `SKILL.md` for Layers B, C, and analysis are stubs. To
implement one:

1. Replace the relevant `references/layer_*.md` stub with the real guide.
2. For data-bearing layers (B), mirror the Layer A pattern: a compact
   `<layer>/index.yaml` routing surface + per-item files loaded on demand. Keep
   `SKILL.md` thin — it conducts; the heavy material lives in resource files loaded
   only when that step runs.
3. Flip the step's status marker in `SKILL.md` from 🚧 to ✅.

## Provenance

Cite sources for any data you add. Layer A cites HumSet — see `references/SOURCES.md`.
