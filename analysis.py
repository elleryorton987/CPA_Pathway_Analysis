import csv
import math
from pathlib import Path

DATA_PATH = Path('Alternative CPA Pathways Survey_December 31, 2025_09.45.csv')
REPORT_PATH = Path('reports/employer_encouragement_cpa_intent.md')
CHART_PATH = Path('outputs/cpa_intent_by_employer.svg')

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
CHART_PATH.parent.mkdir(parents=True, exist_ok=True)


def normalize(value: str) -> str:
    return value.strip().lower()


def recode_employer(value: str):
    if value is None:
        return None
    val = normalize(value)
    if not val:
        return None
    supportive = {
        'yes',
        'agree',
        'strongly agree',
        'encouraged',
        'supportive',
        'required',
        'strongly encourage',
        'encourage',
        'support',
    }
    unsupportive = {
        'no',
        'disagree',
        'strongly disagree',
        'not encouraged',
        'unsupportive',
    }
    if val in supportive:
        return 1
    if val in unsupportive:
        return 0
    return None


def recode_cpa_intent(value: str):
    if value is None:
        return None
    val = normalize(value)
    if not val:
        return None
    likely = {'very likely', 'somewhat likely'}
    unlikely = {'very unlikely', 'somewhat unlikely'}
    if val in likely:
        return 1
    if val in unlikely:
        return 0
    return None


def chi_square_2x2(a, b, c, d):
    n = a + b + c + d
    row1 = a + b
    row0 = c + d
    col1 = a + c
    col0 = b + d
    expected = [
        row1 * col1 / n,
        row1 * col0 / n,
        row0 * col1 / n,
        row0 * col0 / n,
    ]
    observed = [a, b, c, d]
    chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e)
    p_value = math.erfc(math.sqrt(chi2 / 2))
    return chi2, p_value


def phi_coefficient(a, b, c, d):
    numerator = (a * d) - (b * c)
    denominator = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    if denominator == 0:
        return 0.0
    return numerator / denominator


def odds_ratio(a, b, c, d):
    adj_a, adj_b, adj_c, adj_d = a, b, c, d
    if min(a, b, c, d) == 0:
        adj_a += 0.5
        adj_b += 0.5
        adj_c += 0.5
        adj_d += 0.5
    return (adj_a * adj_d) / (adj_b * adj_c)


with DATA_PATH.open(newline='', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    headers = next(reader)
    labels = next(reader)
    _ = next(reader)  # import IDs

    q49_index = headers.index('Q49')
    q29_index = headers.index('Q29')

    rows = list(reader)

employer_label = labels[q49_index]
cpa_label = labels[q29_index]

counts = {
    1: {1: 0, 0: 0},
    0: {1: 0, 0: 0},
}

n_missing_employer = 0
n_missing_cpa = 0
n_total = 0

for row in rows:
    n_total += 1
    employer_raw = row[q49_index]
    cpa_raw = row[q29_index]
    employer = recode_employer(employer_raw)
    cpa_intent = recode_cpa_intent(cpa_raw)
    if employer is None:
        n_missing_employer += 1
    if cpa_intent is None:
        n_missing_cpa += 1
    if employer is None or cpa_intent is None:
        continue
    counts[employer][cpa_intent] += 1


a = counts[1][1]
b = counts[1][0]
c = counts[0][1]
d = counts[0][0]

n_analysis = a + b + c + d

chi2, p_value = chi_square_2x2(a, b, c, d)
phi = phi_coefficient(a, b, c, d)
or_value = odds_ratio(a, b, c, d)


def rate_text(yes, total):
    if total == 0:
        return 'n/a'
    return f"{yes / total:.1%}"

employer_yes_total = a + b
employer_no_total = c + d

employer_yes_rate = rate_text(a, employer_yes_total)
employer_no_rate = rate_text(c, employer_no_total)

chart_width = 440
chart_height = 260
bar_width = 120
bar_gap = 80
max_height = 160

rates = [
    ('Employer encouragement: Yes', a / employer_yes_total if employer_yes_total else 0),
    ('Employer encouragement: No', c / employer_no_total if employer_no_total else 0),
]

svg_parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" viewBox="0 0 {chart_width} {chart_height}">',
    '<rect width="100%" height="100%" fill="#ffffff"/>',
    '<text x="10" y="20" font-family="Arial" font-size="14" fill="#111">CPA intent by employer encouragement</text>',
    '<line x1="40" y1="220" x2="420" y2="220" stroke="#333" stroke-width="1" />',
]

for i, (label, rate) in enumerate(rates):
    height = max_height * rate
    x = 60 + i * (bar_width + bar_gap)
    y = 220 - height
    svg_parts.append(f'<rect x="{x}" y="{y}" width="{bar_width}" height="{height}" fill="#4c78a8"/>')
    svg_parts.append(f'<text x="{x}" y="240" font-family="Arial" font-size="12" fill="#111">{label}</text>')
    svg_parts.append(f'<text x="{x + 10}" y="{y - 8}" font-family="Arial" font-size="12" fill="#111">{rate:.0%}</text>')

svg_parts.append('</svg>')
CHART_PATH.write_text('\n'.join(svg_parts), encoding='utf-8')

report_lines = [
    '# Employer encouragement and CPA pursuit intent',
    '',
    f'Dataset: `{DATA_PATH.as_posix()}`.',
    '',
    '## Selected survey questions',
    f'- Employer encouragement: **{employer_label}** (column Q49).',
    f'- CPA pursuit intent: **{cpa_label}** (column Q29).',
    '',
    '## Recoding summary',
    '- Employer encouragement: Yes/Agree/Strongly agree/Encouraged/Required → 1; No/Disagree/Strongly disagree → 0; neutral/unclear → missing.',
    '- CPA pursuit intent: Very likely/Somewhat likely → 1; Very unlikely/Somewhat unlikely → 0; Neither likely nor unlikely → missing.',
    '',
    '## Analysis sample',
    f'- Total rows in file (after metadata rows): **{n_total}**.',
    f'- Missing employer encouragement: **{n_missing_employer}**.',
    f'- Missing CPA intent: **{n_missing_cpa}**.',
    f'- Included in analysis (non-missing both): **{n_analysis}**.',
    '',
    '## CPA pursuit rates by employer encouragement',
    '',
    '| Employer encouragement | Pursue CPA (n) | Not pursue CPA (n) | Total (n) | Pursue rate |',
    '| --- | ---: | ---: | ---: | ---: |',
    f'| Yes | {a} | {b} | {employer_yes_total} | {employer_yes_rate} |',
    f'| No | {c} | {d} | {employer_no_total} | {employer_no_rate} |',
    '',
    '## Association test',
    f'- Chi-square test of independence (df=1): **χ² = {chi2:.3f}**, **p = {p_value:.4f}**.',
    f'- Effect size (phi): **{phi:.3f}**.',
    f'- Odds ratio (Haldane-Anscombe correction if needed): **{or_value:.3f}**.',
    '',
    '## Interpretation (plain language)',
    f'Respondents whose employers encouraged or required a graduate degree showed a CPA pursuit rate of {employer_yes_rate}, compared to {employer_no_rate} among those without employer encouragement. The chi-square test and effect sizes summarize whether this difference is statistically meaningful in this sample.',
    '',
    '## Visualization',
    f'![CPA intent by employer encouragement]({CHART_PATH.as_posix()})',
]

REPORT_PATH.write_text('\n'.join(report_lines), encoding='utf-8')

print('Report written to', REPORT_PATH)
print('Chart written to', CHART_PATH)
print('Counts (encouraged yes/no by CPA intent yes/no):', counts)
print('Chi-square:', chi2, 'p=', p_value)
