# Layer C — Instrument Map Schema

The exact format for the file Step 3 produces. Layer C is generated per dataset and
saved as `layer_c_<survey>_<YYYY-MM-DD>.md` in the analyst's working folder.

## Header block (required)

```
# Layer C — Instrument Map
Survey: <full survey name and version if known>
Source file: <filename of the Kobo/ODK XLS>
Assessment type: <KI community survey / household survey / facility survey / mixed>
Built: <YYYY-MM-DD>
Layer B version: <date of the catalog used — see catalog/index.yaml header>
```

## Per-question entry

One entry per substantive question. Skip pure admin fields (`calculate`, `note`,
`begin_group`/`end_group`) unless they carry analytical content.

```
### <VARIABLE_NAME>

Question: <full label text from the survey sheet>
Type: <select_one / select_multiple / integer / decimal / text / geopoint / date>
Module: <survey group/module name>
Skip logic: <relevant condition verbatim, or "always asked">

Answer options:
| Code | Label |
|------|-------|
| <code> | <label> |
(or: N/A for free-text and numeric types)

Layer B indicator(s): <comma-separated indicator ids from Step 2, or NONE>
Coverage verdict: <DIRECT / PROXY / NONE>
What this can prove: <one sentence>
What this cannot prove: <one sentence — ALWAYS complete, even for DIRECT>
```

## Coverage verdict rules

**`DIRECT`** — use only when ALL hold:
- collects the exact construct the indicator requires (correct unit, recall period, response format);
- at the correct unit of analysis (household for household indicators, site for community indicators);
- answer options map to the indicator's required categories without transformation.

**`PROXY`** — use when:
- same construct, different format (ordinal band vs measured quantity; presence/absence vs frequency); OR
- different unit of analysis (KI community estimate for a household indicator); OR
- one or more required criteria missing (e.g. source type present but collection time absent).

**`NONE`** — the question maps to no Layer B indicator.

## Two gap lists (required, at the end)

```
## Blind spots

### Questions with no Layer B indicator
- <variable>: <one line — what it collected, why no indicator covers it>

### Step-2 indicators this instrument cannot compute
- <indicator id>: <one line — what is missing from the instrument>
```

These two lists are the whole point of Layer C: they are the constraints Step 4's
analysis must respect. An indicator that lands here cannot be reported as a finding.
