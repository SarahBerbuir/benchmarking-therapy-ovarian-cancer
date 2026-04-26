import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations

# Run omnibus and pairwise tests for the qualitative rating dimensions.
df = pd.read_excel('qualitative_mapped.xlsx')
df['overall'] = df[['correctness', 'completeness', 'comprehensibility', 'applicability']].mean(axis=1)

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability', 'overall']
systems = ['Referenz', 'LLM', 'RAG', 'GraphRAG']
system_pairs = list(combinations(systems, 2))
alpha_bonferroni = 0.05 / len(system_pairs)  # 0.0083


# Friedman tests across all four systems.
print("=" * 60)
print("FRIEDMAN TESTS – ALL CASES (114 rater-case units)")
print("=" * 60)

friedman_results = []

for dim in dimensions:
    pivot = df.pivot_table(index=['rater', 'case_order'], columns='system', values=dim)
    pivot = pivot[systems].dropna()

    chi2, p = stats.friedmanchisquare(*[pivot[s].values for s in systems])
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"

    print(f"  {dim:20s}: χ² = {chi2:.3f}, p = {p:.4f} {sig}")

    friedman_results.append({
        'dimension': dim,
        'chi2': round(chi2, 3),
        'p': round(p, 4)
    })


# Pairwise Wilcoxon signed-rank tests with Bonferroni correction.
print(f"\n{'=' * 60}")
print(f"PAIRWISE WILCOXON – ALL CASES (Bonferroni α = {alpha_bonferroni:.4f})")
print(f"{'=' * 60}")

wilcoxon_results = []

for dim in dimensions:
    pivot = df.pivot_table(index=['rater', 'case_order'], columns='system', values=dim)
    pivot = pivot.dropna()

    print(f"\n  --- {dim} ---")

    for s1, s2 in system_pairs:
        w, p = stats.wilcoxon(pivot[s1], pivot[s2])

        sig = "SIG" if p < alpha_bonferroni else "trend" if p < 0.05 else "ns"
        direction = ">" if pivot[s1].mean() > pivot[s2].mean() else "<"

        print(f"    {s1:10s} {direction} {s2:10s}: W = {w:.1f}, p = {p:.4f} [{sig}]")

        wilcoxon_results.append({
            'dimension': dim,
            'system1': s1,
            'system2': s2,
            'W': round(w, 1),
            'p': round(p, 4),
            'significant_bonferroni': p < alpha_bonferroni,
            'significant_uncorrected': p < 0.05
        })


# Print only the pairwise results that remain significant after correction.
print(f"\n{'=' * 60}")
print("ZUSAMMENFASSUNG – Signifikant nach Bonferroni")
print(f"{'=' * 60}")

df_wilcox = pd.DataFrame(wilcoxon_results)
sig_pairs = df_wilcox[df_wilcox['significant_bonferroni']]

for dim in dimensions:
    dim_sig = sig_pairs[sig_pairs['dimension'] == dim]

    if len(dim_sig) > 0:
        pairs = [
            f"{row['system1']} vs {row['system2']} (p={row['p']:.4f})"
            for _, row in dim_sig.iterrows()
        ]
        print(f"  {dim}: {', '.join(pairs)}")
    else:
        print(f"  {dim}: keine")


# Store the test results for later reporting.
with pd.ExcelWriter('omnibus_pairwise_tests.xlsx') as writer:
    pd.DataFrame(friedman_results).to_excel(writer, sheet_name='friedman', index=False)
    df_wilcox.to_excel(writer, sheet_name='wilcoxon_pairwise', index=False)

print("\nGespeichert: omnibus_pairwise_tests.xlsx")