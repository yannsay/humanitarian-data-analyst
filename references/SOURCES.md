# Sources & Provenance

## Layer A — HumSet / DEEP analytical framework

The Layer A ontology (`ontology/`) is derived from the **HumSet** dataset and the
DEEP humanitarian analytical framework (Data Friendly Space / The DEEP). The 66
nodes across 5 axes, their descriptions, synonyms, and `distinguish_from` fields
were drafted from saturation sampling over the HumSet English corpus
(see the parent project's `09_full_layer_a_implementation/`).

If you use this skill or its ontology in academic or published work, please cite
HumSet:

```bibtex
@inproceedings{fekih-etal-2022-humset,
    title = "{H}um{S}et: Dataset of Multilingual Information Extraction and Classification for Humanitarian Crises Response",
    author = "Fekih, Selim  and
      Tamagnone, Nicolo{'}  and
      Minixhofer, Benjamin  and
      Shrestha, Ranjan  and
      Contla, Ximena  and
      Oglethorpe, Ewan  and
      Rekabsaz, Navid",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2022",
    month = dec,
    year = "2022",
    address = "Abu Dhabi, United Arab Emirates",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.findings-emnlp.321",
    pages = "4379--4389",
}
```

**Dataset:** `nlp-thedeep/humset` on Hugging Face.
**Paper:** <https://aclanthology.org/2022.findings-emnlp.321>

Consult the HumSet dataset terms for any restrictions on the underlying taxonomy and
excerpts before redistribution.

## Layer B — indicator catalog sources

The indicator catalog (`catalog/`, version 2026-05-20) holds 41 indicators across three
clusters, each drafted from authoritative humanitarian standards. **Provenance lives in
the catalog itself**, at two levels:

- **Per-cluster header** — each cluster file names the documents it was drafted from
  (top-of-file comment).
- **Per-indicator `source:` block** — most entries carry `source.primary` (the document,
  table, and page the definition/threshold comes from), `source.secondary` (related
  standards, e.g. the SDG indicator), and a `source.note`. Thresholds are also cited
  inline in `formula` / `thresholds` / `common_implementation_errors`.

The standards drawn on, by cluster:

| Cluster | Primary sources |
|---|---|
| **WASH** (17) | JMP *Core Questions for Household Surveys*, 2018 update (WHO/UNICEF) — service ladders for water, sanitation, hygiene; Sphere Handbook 2018 (water quantity 15 L/p/d, sanitation 1:20). |
| **Food Security** (9) | FSL/Food Security cluster standard indicators — rCSI, FCS, HDDS, HHS, HFIAS, expenditure shares, terms of trade, HEA survival deficit (WFP/FAO/FANTA methodologies). |
| **CCCM / Shelter** (15) | CAMP-EN 2021 (Camp Management standards); *Collective Centres Standards Ukraine 2022* (CCCM Cluster), which cross-references the Sphere Handbook 2018; Sphere shelter floor-area standard (3.5 m²/person). |

To trace any single indicator's source, open its entry in `catalog/<cluster>.yaml` and
read its `source:` block — that is the authoritative citation. `references/layer_b_indicators.md`
explains how to read the catalog. The catalog draft + sanity-check protocol is in the
parent project's `02_layer_b__indicator_extraction/` and `03_layer_b__catalog_eda_iteration/`;
the Step-13 plan adds per-threshold source hardening (document, section/page, verbatim
quote, access date) and a per-indicator `review_status` field.

> Caution: a few index-level labels were corrected after drafting (e.g. the Ukraine CC
> corner-room heating threshold and SMS staffing ratio — see the `# CORRECTED` notes in
> `catalog/index.yaml`). The per-indicator YAML `source:` block is the source of truth
> where the index and an entry disagree.

If you use the catalog in published work, cite the underlying standards directly (JMP
2018, Sphere 2018, CAMP-EN 2021, Ukraine CC 2022, and the relevant WFP/FAO food-security
methodologies) rather than this skill.
