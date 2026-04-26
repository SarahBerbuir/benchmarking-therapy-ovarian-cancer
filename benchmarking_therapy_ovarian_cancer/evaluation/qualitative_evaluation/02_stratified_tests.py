import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations

# Stratified Friedman and pairwise Wilcoxon tests by case status.
df = pd.read_excel('qualitative_mapped.xlsx')
# TODO generalize
df_study = pd.read_excel('/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/qualitative_eval/Studienaufbau kopie.xlsx')

status_map = dict(zip(df_study['Case order google form'], df_study['Status']))
df['status'] = df['case_order'].map(status_map)
df['overall'] = df[['correctness', 'completeness', 'comprehensibility', 'applicability']].mean(axis=1)

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability', 'overall']
systems = ['Referenz', 'LLM', 'RAG', 'GraphRAG']
system_pairs = list(combinations(systems, 2))
alpha_bonferroni = 0.05 / len(system_pairs)  # 0.0083

all_friedman = []
all_wilcoxon = []

for status, status_label, n_cases in [
    ('Diagnose', 'Confirmed diagnosis', 8),
    ('Verdacht', 'Suspected ovarian cancer', 11)
]:
    df_sub = df[df['status'] == status]
    n_units = df_sub[['rater', 'case_order']].drop_duplicates().shape[0]

    # Omnibus comparison across systems.
    print(f"\n{'=' * 60}")
    print(f"FRIEDMAN – {status_label} (n={n_cases}, {n_units} rater-case units)")
    print(f"{'=' * 60}")

    for dim in dimensions:
        pivot = df_sub.pivot_table(index=['rater', 'case_order'], columns='system', values=dim)
        pivot = pivot[systems].dropna()

        chi2, p = stats.friedmanchisquare(*[pivot[s].values for s in systems])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"

        print(f"  {dim:20s}: χ² = {chi2:.3f}, p = {p:.4f} {sig}")

        all_friedman.append({
            'status': status,
            'dimension': dim,
            'chi2': round(chi2, 3),
            'p': round(p, 4)
        })

    # Pairwise follow-up tests.
    print(f"\n{'=' * 60}")
    print(f"PAIRWISE WILCOXON – {status_label} (Bonferroni α = {alpha_bonferroni:.4f})")
    print(f"{'=' * 60}")

    for dim in dimensions:
        pivot = df_sub.pivot_table(index=['rater', 'case_order'], columns='system', values=dim)
        pivot = pivot.dropna()

        print(f"\n  --- {dim} ---")

        for s1, s2 in system_pairs:
            if s1 not in pivot.columns or s2 not in pivot.columns:
                continue

            try:
                w, p = stats.wilcoxon(pivot[s1], pivot[s2])
            except ValueError:
                print(f"    {s1:10s} vs {s2:10s}: cannot compute (all differences zero)")
                continue

            sig = "SIG" if p < alpha_bonferroni else "trend" if p < 0.05 else "ns"
            direction = ">" if pivot[s1].mean() > pivot[s2].mean() else "<"

            print(f"    {s1:10s} {direction} {s2:10s}: W = {w:.1f}, p = {p:.4f} [{sig}]")

            all_wilcoxon.append({
                'status': status,
                'dimension': dim,
                'system1': s1,
                'system2': s2,
                'W': round(w, 1),
                'p': round(p, 4),
                'significant_bonferroni': p < alpha_bonferroni
            })

    # Short summary for the current stratum.
    print(f"\n  --- Signifikant nach Bonferroni ({status}) ---")

    df_w = pd.DataFrame(all_wilcoxon)
    df_w_status = df_w[(df_w['status'] == status) & (df_w['significant_bonferroni'])]

    for dim in dimensions:
        dim_sig = df_w_status[df_w_status['dimension'] == dim]

        if len(dim_sig) > 0:
            pairs = [
                f"{row['system1']} vs {row['system2']} (p={row['p']:.4f})"
                for _, row in dim_sig.iterrows()
            ]
            print(f"    {dim}: {', '.join(pairs)}")
        else:
            print(f"    {dim}: keine")


# Save both result tables.
with pd.ExcelWriter('stratified_friedman_wilcoxon.xlsx') as writer:
    pd.DataFrame(all_friedman).to_excel(writer, sheet_name='friedman', index=False)
    pd.DataFrame(all_wilcoxon).to_excel(writer, sheet_name='wilcoxon', index=False)

print("\nGespeichert: stratified_friedman_wilcoxon.xlsx")