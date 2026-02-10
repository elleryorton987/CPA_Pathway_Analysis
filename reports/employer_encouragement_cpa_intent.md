# Employer encouragement and CPA pursuit intent

Dataset: `Alternative CPA Pathways Survey_December 31, 2025_09.45.csv`.

## Selected survey questions
- Employer encouragement: **Has your current or future employer emphasized that they require or strongly encourage a graduate degree in order to maintain a job offer or gain promotion?** (column Q49).
- CPA pursuit intent: **How likely are you to pursue a CPA license? If you aren't sure, select "Neither likely nor unlikely"** (column Q29).

## Recoding summary
- Employer encouragement: Yes/Agree/Strongly agree/Encouraged/Required → 1; No/Disagree/Strongly disagree → 0; neutral/unclear → missing.
- CPA pursuit intent: Very likely/Somewhat likely → 1; Very unlikely/Somewhat unlikely → 0; Neither likely nor unlikely → missing.

## Analysis sample
- Total rows in file (after metadata rows): **206**.
- Missing employer encouragement: **152**.
- Missing CPA intent: **27**.
- Included in analysis (non-missing both): **51**.

## CPA pursuit rates by employer encouragement

| Employer encouragement | Pursue CPA (n) | Not pursue CPA (n) | Total (n) | Pursue rate |
| --- | ---: | ---: | ---: | ---: |
| Yes | 13 | 1 | 14 | 92.9% |
| No | 35 | 2 | 37 | 94.6% |

## Association test
- Chi-square test of independence (df=1): **χ² = 0.055**, **p = 0.8140**.
- Effect size (phi): **-0.033**.
- Odds ratio (Haldane-Anscombe correction if needed): **0.743**.

## Interpretation (plain language)
Respondents whose employers encouraged or required a graduate degree showed a CPA pursuit rate of 92.9%, compared to 94.6% among those without employer encouragement. The chi-square test and effect sizes summarize whether this difference is statistically meaningful in this sample.

## Visualization
![CPA intent by employer encouragement](outputs/cpa_intent_by_employer.svg)