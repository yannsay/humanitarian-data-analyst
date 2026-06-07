# humanitarian-data-analyst

An [Agent Skill](https://agentskills.io) for disciplined analysis of humanitarian
needs-assessment data (Kobo/ODK surveys, RNA/MSNA/HNO datasets).

It runs a four-step pipeline between an analyst's free-text question and a raw
survey:

1. **Route** (Layer A) — map the question to the HumSet/DEEP analytical framework.
2. **Indicators** (Layer B) — identify the indicators that answer it. *(stub)*
3. **Bind** (Layer C) — map the survey's questions to indicators; surface gaps. *(stub)*
4. **Analyse** — produce a grounded answer caveated by what the data can prove. *(stub)*

The point of the pipeline is to **force the consult step**. Generic LLM analysis of
humanitarian data knows the right methodology but skips it under the pressure of
answering; this skill makes the framework and indicator definitions a required input,
not passive context.

## Status

| Layer | Status |
|-------|--------|
| A — Framework routing (66 nodes, 5 axes, HumSet/DEEP) | ✅ implemented |
| B — Indicator catalog | 🚧 stub — ported in a later release |
| C — Dataset binding | 🚧 stub |
| Analysis | 🚧 stub |

## Install

```bash
npx @agentskills/cli install yannsay/humanitarian-data-analyst
```

Or copy the `humanitarian-data-analyst/` directory into your agent's skills folder
(e.g. `.claude/skills/` for Claude Code). The skill activates automatically when a
request involves humanitarian assessment data.

## Layout

```
humanitarian-data-analyst/
├── SKILL.md                      # the pipeline conductor (loaded on activation)
├── references/
│   ├── layer_a_routing.md        # full routing guide + worked examples
│   ├── layer_b_indicators.md     # stub
│   ├── layer_c_binding.md        # stub
│   └── analysis.md               # stub
├── ontology/                     # Layer A data
│   ├── index.yaml                # compact routing surface — all 66 nodes
│   ├── sectors/                  # 11 nodes
│   ├── pillars_1d/               # 6 nodes
│   ├── subpillars_1d/            # 27 nodes
│   ├── pillars_2d/               # 6 nodes
│   └── subpillars_2d/            # 16 nodes
├── LICENSE
└── package.json
```

## How Layer A works (progressive disclosure)

The agent never loads the whole 180 KB ontology. On a question it reads
`ontology/index.yaml` (a compact gist+synonyms line per node), matches the topic,
then opens only the handful of node files it needs to read their `distinguish_from`
fields before committing to a routing. This keeps the context footprint small while
preserving the full framework detail on demand.

## Provenance & citation

Layer A is derived from the **HumSet** dataset and the DEEP humanitarian analytical
framework (Data Friendly Space / The DEEP). Each node carries `excerpt_count` /
`saturation_batches` fields for audit.

If you use this skill or its ontology in published work, please cite HumSet
(Fekih et al., 2022). Full BibTeX is in [`references/SOURCES.md`](references/SOURCES.md),
and the repo ships a [`CITATION.cff`](CITATION.cff) so GitHub renders a
"Cite this repository" button.

> Fekih, S., Tamagnone, N., Minixhofer, B., Shrestha, R., Contla, X., Oglethorpe, E.,
> & Rekabsaz, N. (2022). *HumSet: Dataset of Multilingual Information Extraction and
> Classification for Humanitarian Crises Response.* Findings of the ACL: EMNLP 2022,
> 4379–4389. <https://aclanthology.org/2022.findings-emnlp.321>

## License

MIT — see [`LICENSE`](LICENSE). Note: the underlying HumSet taxonomy/excerpts carry
their own dataset terms; consult them before redistributing the ontology.
