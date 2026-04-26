import pandas as pd
from scipy import stats

# Compare expert ratings with LLM-as-a-judge ratings.
df_expert = pd.read_excel('qualitative_mapped.xlsx')
df_judge = pd.read_excel('llm_as_a_judge_v2.xlsx', sheet_name='likert_ratings')

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability']

# Average expert ratings across raters for each case and system.
df_expert_agg = df_expert.groupby(['case_order', 'system'])[dimensions].mean().reset_index()

df_merged = pd.merge(
    df_expert_agg,
    df_judge[['case_order', 'system'] + dimensions],
    on=['case_order', 'system'],
    suffixes=('_expert', '_judge')
)

print(f"Merged rows: {len(df_merged)}")

results = []

for dim in dimensions:
    col_expert = f'{dim}_expert'
    col_judge = f'{dim}_judge'

    rho, p = stats.spearmanr(df_merged[col_expert], df_merged[col_judge])

    results.append({
        'dimension': dim,
        'rho': round(rho, 4),
        'p_value': round(p, 4),
        'significant': p < 0.05
    })

    print(f"{dim}: ρ = {round(rho, 4)}, p = {round(p, 4)}")

df_spearman = pd.DataFrame(results)
df_spearman.to_excel('spearman_correlation.xlsx', index=False)

print("\nGespeichert: spearman_correlation.xlsx")