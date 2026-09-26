# RPMS-PT/BR: agreement data and analyses

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22730156.svg)](https://doi.org/10.5281/zenodo.22730156)
<!-- Badge stays broken until the first Zenodo release. Swap the DOI above once it exists. -->

[🇧🇷 Português](README.md) · 🇺🇸 English (this file) · [🇪🇸 Español](README.es.md)

Reproduction material for the statistical analyses of the cross-cultural
adaptation of the *Refugee Post-Migration Stress Scale* (RPMS) into
Brazilian Portuguese.

Author of the analyses and scripts: **Guilherme Lacerda de Avila**

This repository exists so that anyone can start from the raw data and
reach, on their own, exactly the same coefficients reported in the
article and the poster. You don't need to take our word for it: the
data is here, the scripts are here, and running them takes under a
minute.

## Result you should get

| Panel | Items | Raters | Gwet's AC1 | S-CVI/Ave | S-CVI/UA |
|---|---|---|---|---|---|
| Expert judges | 21 | 4 | 0.895 | 0.952 | 0.810 |
| Target population | 21 | 4 | 0.976 | 0.988 | 0.952 |

Coefficients calculated as a robustness check, which do not go into the
body of the article for the reasons explained further down:

| Panel | Fleiss' Kappa | Krippendorff's Alpha |
|---|---|---|
| Expert judges | −0.050 | −0.046 |
| Target population | −0.012 | −0.008 |

If you run this and get something else, it's a bug: please open an
issue.

## How to run

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11 or higher.
`uv` resolves the dependencies on its own on first run; there's no need
to create a virtual environment or install anything by hand.

```bash
git clone https://github.com/lacerdaguilherme/rpms-ptbr.git
cd rpms-ptbr

# main coefficient, the one reported in the article
uv run estatistica/ac1_epmr.py
uv run estatistica/ac1_rpms.py

# content validity (CVI) alongside AC1
uv run estatistica/cvi_ac1_epmr.py
uv run estatistica/cvi_ac1_rpms.py

# robustness checks
uv run estatistica/fleiss_kappa_epmr.py
uv run estatistica/fleiss_kappa_rpms.py
uv run estatistica/krippendorff_alpha_epmr.py
uv run estatistica/krippendorff_alpha_rpms.py

# text and tables for the Results section, filled with the numbers above
uv run estatistica/gerar_texto_resultados.py

# independent verification of translation/back-translation agreement
# (doesn't need the private spreadsheets, only the public CSV in dados/)
uv run estatistica/verificar_concordancia_traducao.py
uv run estatistica/verificar_concordancia_retrotraducao.py
```

Each script prints the result to the terminal and saves three files
under `estatistica/resultados/`, sharing the same timestamp: a `.txt`
with the full report, a `.png` with the summary table ready for the
article, and an `.html` with the same table as a web page.

To run against a different data file, pass the path as an argument:

```bash
uv run estatistica/ac1_epmr.py path/to/other_data.csv
```

## The data

```
dados/
├── avaliacao_epmr.csv                          expert-judges panel
├── avaliacao_rpms.csv                           target-population panel
├── concordancia_traducao_por_item.csv           % translation agreement, per item
└── concordancia_retrotraducao_por_item.csv      % back-translation agreement, per item
```

One row per response, 84 rows per file (21 items × 4 judges):

| Column | Content |
|---|---|
| `item` | item number on the scale, 1 to 21 |
| `juiz` | sequential rater identifier, 1 to 4 |
| `resposta` | `Sim` or `Não` (Yes/No), exactly as marked in the spreadsheet's binary column |
| `tem_ressalva` | `1` if the rater wrote anything in the justification field |
| `ressalva` | what they wrote, when they wrote anything |

The full data dictionary, with the wording of each item and what was
actually asked of the judges, is in
[`estatistica/CODEBOOK.md`](estatistica/CODEBOOK.md).

### What is not published, and why

The original Excel spreadsheets are **not** in this repository. Each
sheet's name contains the rater's real name, and from row 28 onward
there is full name, age, and country of origin. In the target-population
panel the raters are refugees, which makes that data especially
sensitive. The published CSVs contain everything needed to reproduce the
calculations and nothing that identifies who answered.

The `estatistica/exportar_dados_brutos.py` script documents exactly how
the CSVs were extracted from the spreadsheets. It only runs for whoever
has the original files, i.e., the research team. It is here so the
anonymization procedure is auditable, not to be run by whoever clones
the repository.

## How responses were coded

This is the methodological point that matters most for anyone
reanalyzing the data, and it is open to inspection.

Next to the binary response, the spreadsheet has a free-text field where
the rater could write something. In nine cases in the expert panel and
one in the target-population panel, someone wrote something there. These
notes are not all of the same nature:

- **Suggestion to improve an item the rater approved.** Along the lines
  of "maybe swap 'social status' for 'social conditions'" or "Note:
  mention accent." The rater doesn't contest the item, they propose
  improving it. These count as agreement, because that's what they
  answered.
- **Objection pointing to a flaw in the item as worded.** This happens
  exactly once in the whole study, in item 6 of the target-population
  panel, where the rater noted that the word "deslocamento"
  ("displacement/commute") is not understood by most foreigners. This
  counts as disagreement, because the item did not fulfill its function
  for that respondent.

This decision is declared explicitly at the top of each script, in the
`ITENS_COM_RESSALVA_RECLASSIFICADA` constant, not hidden in the logic:

```python
# in the expert-panel scripts
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset()

# in the target-population scripts
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset({6})
```

**You can test the effect of this choice.** Since the CSVs publish the
`tem_ressalva` column, just change the constant and run again:

| Configuration | Experts | Target population |
|---|---|---|
| `frozenset()` | AC1 = 0.895 | AC1 undefined (unanimity: Pa = 1, Pe = 0) |
| `frozenset({6})` | AC1 = 0.895 | AC1 = 0.976 |
| every objection reclassified | AC1 = 0.735 | AC1 = 0.976 |

The third row is historically relevant: it was the rule in force between
2026-08-21 and 2026-09-11, mistakenly generalized to any filled-in
field. The audit that fixed this is documented in
[`estatistica/EXPLICACAO.md`](estatistica/EXPLICACAO.md), section 16.

## Why Gwet's AC1, and not Fleiss' Kappa

Fleiss' Kappa and Krippendorff's Alpha give **negative** values in both
panels, despite raw agreement being high: in the target-population
panel, only 1 of the 84 responses diverged from the rest.

This is not a calculation error, nor real disagreement among the judges.
It is the **kappa paradox** (Feinstein & Cicchetti, 1990): formulas that
correct agreement for the variance of marginal categories become
unstable when response prevalence is highly imbalanced, which is exactly
the case in a content-validity evaluation, where most items are
approved.

Gwet's AC1 (2008) was built to not have this behavior. The two unstable
coefficients continue to be calculated and published here on purpose:
they are evidence that choosing AC1 was not convenience, but a
consequence of the data's structure. Two mathematically distinct
formulas converging on the same negative value show that the problem
lies in the family of statistics, not in one of them.

The full explanation, with the math, is in
[`estatistica/EXPLICACAO.md`](estatistica/EXPLICACAO.md), sections 9 and
11.

## Repository layout

```
dados/
├── avaliacao_epmr.csv                          raw data, expert panel
├── avaliacao_rpms.csv                           raw data, target-population panel
├── concordancia_traducao_por_item.csv           % translation agreement, per item (no text)
└── concordancia_retrotraducao_por_item.csv      % back-translation agreement, per item (no text)

estatistica/
├── ac1_epmr.py                            standalone Gwet's AC1 (goes in the article)
├── ac1_rpms.py
├── cvi_ac1_epmr.py                        CVI and AC1 side by side
├── cvi_ac1_rpms.py
├── fleiss_kappa_epmr.py                   robustness check
├── fleiss_kappa_rpms.py
├── krippendorff_alpha_epmr.py             robustness check
├── krippendorff_alpha_rpms.py
├── concordancia_traducao.py               % translation agreement (needs the private spreadsheet)
├── concordancia_retrotraducao.py          % back-translation agreement (needs the private spreadsheet)
├── verificar_concordancia_traducao.py     reproduces the % above using only the public CSV
├── verificar_concordancia_retrotraducao.py  reproduces the % above using only the public CSV
├── exportar_dados_brutos.py               generates the CSVs from the spreadsheets
├── gerar_texto_resultados.py               builds the Results section's text
├── CODEBOOK.md                             data dictionary
├── EXPLICACAO.md                           line-by-line explanation of each script
├── RESULTADOS_PARA_ARTIGO.md               text, tables and references
└── resultados/                             output of each run
```

Each script is self-contained and can be read start to finish without
consulting the others. This duplicates some functions across files, and
it's intentional: the goal is that someone unfamiliar with Python can
follow a whole file, not that the code be as short as possible.
`EXPLICACAO.md` walks through that reading line by line.

### The two translation-agreement scripts

`concordancia_traducao.py` and `concordancia_retrotraducao.py` calculate
the percentage of agreement between the translated versions of the
instrument. They read spreadsheets with the full text of the scale in
all three versions, which **are not published here**: the RPMS is Malm
et al.'s (2020) instrument, and redistributing its full text depends on
authorization that has not yet been granted. The scripts stay in the
repository to document the method; running them requires having the
spreadsheets.

What **is** published is the numeric result of the comparison, item by
item (`dados/concordancia_traducao_por_item.csv`,
`dados/concordancia_retrotraducao_por_item.csv`): item label,
identical/different, and % similarity — with no text column at all. A
similarity percentage calculated from the text is our own derived data,
not the text itself, so publishing it does not redistribute Malm et
al.'s instrument. The `verificar_concordancia_traducao.py` and
`verificar_concordancia_retrotraducao.py` scripts read only these CSVs
and reproduce the percentages reported in the article (46.4% and 6.7%)
without depending on the private spreadsheets — this is the intended
path for anyone who wants to audit those two numbers without needing
access to the original instrument.

## Dependencies

Declared in `pyproject.toml` and resolved automatically by `uv`:

| Library | What for |
|---|---|
| `statsmodels` | Fleiss' Kappa calculation |
| `openpyxl` | reading the original Excel spreadsheets |
| `matplotlib` | generating the summary tables as PNG |
| `pandas` | auxiliary tabular manipulation |

Gwet's AC1, the CVI, and Krippendorff's Alpha are implemented directly in
the scripts, from the published formulas, with no third-party library
dependency. `EXPLICACAO.md` shows every step of the calculation.

## References

Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low
kappa: I. The problems of two paradoxes. *Journal of Clinical
Epidemiology, 43*(6), 543–549.

Fleiss, J. L. (1971). Measuring nominal scale agreement among many
raters. *Psychological Bulletin, 76*(5), 378–382.

Gwet, K. L. (2008). Computing inter-rater reliability and its variance in
the presence of high agreement. *British Journal of Mathematical and
Statistical Psychology, 61*(1), 29–48.

Krippendorff, K. (2019). *Content analysis: An introduction to its
methodology* (4th ed.). Sage.

Landis, J. R., & Koch, G. G. (1977). The measurement of observer
agreement for categorical data. *Biometrics, 33*(1), 159–174.

Lynn, M. R. (1986). Determination and quantification of content validity.
*Nursing Research, 35*(6), 382–385.

Malm, A., Tinghög, P., Narusyte, J., & Saboonchi, F. (2020). The refugee
post-migration stress scale (RPMS): Development and validation among
refugees from Syria recently resettled in Sweden. *Conflict and Health,
14*, Article 2.

Polit, D. F., Beck, C. T., & Owen, S. V. (2007). Is the CVI an acceptable
indicator of content validity? Appraisal and recommendations. *Research
in Nursing & Health, 30*(4), 459–467.

## Status and license

Ongoing undergraduate research project. The coefficients here are the
ones reported in the article in preparation and in the poster presented;
the instrument's psychometric steps (internal consistency, factor
structure) have not yet been carried out.

Data usage license not yet formally defined. To reuse the data in
another study, please get in touch first.

## How to cite

This repository is citable via CITATION.cff (GitHub itself shows a
"Cite this repository" button on the repo page) and via the permanent
DOI issued by Zenodo — see the badge at the top of this file.

**APA 7th edition:**

> Avila, G. L. de. (2026). *rpms-ptbr: Dados e rotinas de análise de
> concordância da adaptação transcultural da RPMS para o português
> brasileiro* (Version 1.0.0) [Computer software]. Zenodo.
> https://doi.org/10.5281/zenodo.22730156

**ABNT (NBR 6023):**

> ÁVILA, Guilherme Lacerda de. **rpms-ptbr**: dados e rotinas de análise
> de concordância da adaptação transcultural da RPMS para o português
> brasileiro. Versão 1.0.0. [*S. l.*]: Zenodo, 2026. Disponível em:
> https://doi.org/10.5281/zenodo.22730156. Acesso em: [access date].

Author's ORCID: [0009-0006-3063-4030](https://orcid.org/0009-0006-3063-4030).
