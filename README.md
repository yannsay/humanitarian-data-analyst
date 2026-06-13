# humanitarian-data-analyst

An [Agent Skill](https://agentskills.io) for disciplined analysis of humanitarian
needs-assessment data (Kobo/ODK surveys, RNA/MSNA/HNO datasets).

It is **one worked example** of a disciplined-analysis method — a reference pipeline,
not the only way to do this. It runs four steps between an analyst's free-text question
and a raw survey:

1. **Route** (Step 1) — map the question to the HumSet/DEEP analytical framework.
2. **Indicators** (Step 2) — identify the catalog indicators that answer it.
3. **Bind** (Step 3) — map the survey's questions to indicators; surface gaps.
4. **Analyse** (Step 4) — produce a grounded answer caveated by what the data can prove. *(stub)*

The point of the pipeline is to **force the consult step**. Generic LLM analysis of
humanitarian data knows the right methodology but skips it under the pressure of
answering; this skill makes the framework and indicator definitions a required input,
not passive context.

## Status

| Step | Status |
|-------|--------|
| 1 — Framework routing (66 nodes, 5 axes, HumSet/DEEP) | ✅ implemented |
| 2 — Indicator catalog (41 indicators: WASH, Food Security, Shelter/CCCM) | ✅ implemented |
| 3 — Dataset binding (built per dataset from the Kobo/ODK instrument) | ✅ implemented |
| 4 — Analysis | 🚧 stub |

The skill opens by writing a checklist to disk (in the analyst's working folder) and
mirroring it as a task list, then iterates Route → Indicators → Bind → Analyse —
re-enterable after `/clear`.

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
│   ├── step_1_understanding_the_question.md   # routing guide + worked examples
│   ├── step_2_indicator_catalog.md            # catalog guide + how to use the scripts
│   ├── step_3_mapping_to_dataset.md           # binding guide + kobo query modes
│   └── analysis.md               # stub
├── ontology/                     # Step 1 framework data
│   ├── index.yaml                # compact routing surface — all 66 nodes
│   ├── sectors/                  # 11 nodes
│   ├── pillars_1d/               # 6 nodes
│   ├── subpillars_1d/            # 27 nodes
│   ├── pillars_2d/               # 6 nodes
│   └── subpillars_2d/            # 16 nodes
├── catalog/                      # Step 2 indicator catalog data
│   ├── index.yaml                # routing surface — all 41 indicators + step1_framework_anchor
│   ├── food_security.yaml        # 9 indicators
│   ├── wash.yaml                 # 17 indicators
│   └── cccm.yaml                 # 15 indicators (Shelter)
├── bindings/
│   └── schema.md                 # Step 3 binding spec format (built per dataset)
├── templates/
│   └── checklist.md              # disk-persisted run checklist (copied per analysis)
├── LICENSE
└── package.json
```

## How Step 1 framework routing works (progressive disclosure)

The agent never loads the whole 180 KB ontology. On a question it reads
`ontology/index.yaml` (a compact gist+synonyms line per node), matches the topic,
then opens only the handful of node files it needs to read their `distinguish_from`
fields before committing to a routing. This keeps the context footprint small while
preserving the full framework detail on demand.

## Provenance & citation

This skill stands on work by others, and credit is due to them.

**The Step 1 framework** is derived from the **HumSet** dataset and the DEEP humanitarian
analytical framework (Data Friendly Space / The DEEP). Each node carries `excerpt_count` /
`saturation_batches` fields for audit.

**The Step 2 indicator catalog** is drafted from authoritative humanitarian standards,
authored by:

- **WHO/UNICEF Joint Monitoring Programme (JMP)** — *Core Questions for Household
  Surveys*, 2018 update — WASH service-ladder indicators.
- **Sphere Association** — *The Sphere Handbook*, 2018 — water-quantity (15 L/p/d),
  sanitation (1:20) and shelter floor-area (3.5 m²/person) standards.
- **Global CCCM Cluster** — *Collective Centres Standards, Ukraine 2022* and *Minimum
  Standards for Camp Management (CAMP-EN), 2021* — site-management indicators.
- **WFP, the FSL cluster, and FANTA** — *FSL Indicator Handbook (2020)*, *WFP CARI
  Guidelines (2021)*, and *FANTA HDDS Guidance* — food-security indicators (rCSI, FCS,
  HDDS, and related).

Per-indicator citations (document, table, page) live in each entry's `source:` block in
`catalog/<cluster>.yaml`; see [`references/SOURCES.md`](references/SOURCES.md) for the
full provenance summary.

If you use this skill or its data in published work, please credit these source authors
and cite the underlying standards directly, plus HumSet (Fekih et al., 2022) for the
framework. The repo ships a [`CITATION.cff`](CITATION.cff) listing all of them, so GitHub
renders a "Cite this repository" button.

> Fekih, S., Tamagnone, N., Minixhofer, B., Shrestha, R., Contla, X., Oglethorpe, E.,
> & Rekabsaz, N. (2022). *HumSet: Dataset of Multilingual Information Extraction and
> Classification for Humanitarian Crises Response.* Findings of the ACL: EMNLP 2022,
> 4379–4389. <https://aclanthology.org/2022.findings-emnlp.321>

## License

MIT — see [`LICENSE`](LICENSE). Note: the underlying HumSet taxonomy/excerpts carry
their own dataset terms; consult them before redistributing the ontology.
