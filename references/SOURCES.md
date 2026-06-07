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

## Layer B — indicator sources (when implemented)

The indicator catalog (Layer B, not yet bundled) will draw on authoritative
humanitarian standards: JMP service ladders, the FSL Handbook, Sphere Standards,
IPC/CH, INEE Minimum Standards, CAMP-EN, and the IASC Humanitarian Indicators
Registry. Each indicator will carry its own source citation.
