import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations

# Analyse status-specific rating differences and effect sizes.
df = pd.read_excel('qualitative_mapped.xlsx')
# TODO generalize
df_study = pd.read_excel('/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/qualitative_eval/Studienaufbau kopie.xlsx')

status_map = dict(zip(df_study['Case order google form'], df_study['Status']))
df['status'] = df['case_order'].map(status_map)
df['overall'] = df[['correctness', 'completeness', 'comprehensibility', 'applicability']].mean(axis=1)

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability', 'overall']
systems = ['Referenz', 'LLM', 'RAG', 'GraphRAG']


# Cliff's delta for ordinal score differences.
def cliffs_delta(x, y):
    """
    Positive values indicate that x tends to have higher scores than y.
    Common thresholds: <0.147 negligible, <0.33 small, <0.474 medium, otherwise large.
    """
    x, y = np.array(x), np.array(y)
    more = sum(1 for xi in x for yi in y if xi > yi)
    less = sum(1 for xi in x for yi in y if xi < yi)
    return (more - less) / (len(x) * len(y))


def interpret_delta(d):
    d = abs(d)
    if d < 0.147:
        return "negligible"
    elif d < 0.33:
        return "small"
    elif d < 0.474:
        return "medium"
    else:
        return "large"


# Compare confirmed diagnosis and suspected cases within each system.
print("=" * 60)
print("MANN-WHITNEY U – Diagnose vs Verdacht (within each system)")
print("=" * 60)

mw_results = []

for system in systems:
    df_sys = df[df['system'] == system]
    diag = df_sys[df_sys['status'] == 'Diagnose']
    verd = df_sys[df_sys['status'] == 'Verdacht']

    print(f"\n  --- {system} (Diagnose n={len(diag)}, Verdacht n={len(verd)}) ---")

    for dim in dimensions:
        x = diag[dim].dropna()
        y = verd[dim].dropna()

        u, p = stats.mannwhitneyu(x, y, alternative='two-sided')

        n = len(x) + len(y)
        z = stats.norm.isf(p / 2)
        r = z / np.sqrt(n)

        diff = x.mean() - y.mean()
        direction = "Diagnose > Verdacht" if diff > 0 else "Verdacht > Diagnose"

        sig = "*" if p < 0.05 else "ns"

        print(f"    {dim:20s}: U = {u:.1f}, p = {p:.4f}, r = {r:.3f} [{sig}] ({direction})")

        mw_results.append({
            'system': system,
            'dimension': dim,
            'U': round(u, 1),
            'p': round(p, 4),
            'r': round(r, 3),
            'significant': p < 0.05,
            'mean_diagnose': round(x.mean(), 3),
            'mean_verdacht': round(y.mean(), 3),
            'direction': direction
        })


# Effect size for GraphRAG against the reference, split by case status.
print(f"\n{'=' * 60}")
print("CLIFF'S DELTA – GraphRAG vs Referenz (per status)")
print(f"{'=' * 60}")

delta_results = []

for status in ['Diagnose', 'Verdacht']:
    df_sub = df[df['status'] == status]

    print(f"\n  --- {status} ---")

    for dim in dimensions:
        graphrag = df_sub[df_sub['system'] == 'GraphRAG'][dim].dropna().values
        referenz = df_sub[df_sub['system'] == 'Referenz'][dim].dropna().values

        d = cliffs_delta(graphrag, referenz)
        interp = interpret_delta(d)

        print(f"    {dim:20s}: δ = {d:.3f} ({interp})")

        delta_results.append({
            'status': status,
            'dimension': dim,
            'cliffs_delta': round(d, 3),
            'interpretation': interp
        })


# Overall Cliff's delta for all system pairs, separately by status.
print(f"\n{'=' * 60}")
print("CLIFF'S DELTA – Alle Systempaare (overall dimension)")
print(f"{'=' * 60}")

for status in ['Diagnose', 'Verdacht']:
    df_sub = df[df['status'] == status]

    print(f"\n  --- {status} ---")

    for s1, s2 in combinations(systems, 2):
        x = df_sub[df_sub['system'] == s1]['overall'].dropna().values
        y = df_sub[df_sub['system'] == s2]['overall'].dropna().values

        d = cliffs_delta(x, y)
        interp = interpret_delta(d)
        direction = ">" if d > 0 else "<"

        print(f"    {s1:10s} {direction} {s2:10s}: δ = {d:.3f} ({interp})")


# Write the tables used for reporting.
with pd.ExcelWriter('within_system_tests.xlsx') as writer:
    pd.DataFrame(mw_results).to_excel(writer, sheet_name='mann_whitney', index=False)
    pd.DataFrame(delta_results).to_excel(writer, sheet_name='cliffs_delta_graphrag_ref', index=False)

print("\nGespeichert: within_system_tests.xlsx")