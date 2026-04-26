import pandas as pd
import numpy as np
import krippendorff

# Check rater behavior and compute Krippendorff's alpha for the qualitative ratings.
df_mapped = pd.read_excel('qualitative_mapped.xlsx')

print(df_mapped[df_mapped['system'] == 'GraphRAG'].groupby('rater')[
    ['correctness', 'completeness', 'comprehensibility', 'applicability']
].mean().round(2))

for system in ['LLM', 'RAG', 'GraphRAG', 'Referenz']:
    print(f"\n=== {system} ===")
    print(df_mapped[df_mapped['system'] == system].groupby('rater')[
        ['correctness', 'completeness', 'comprehensibility', 'applicability']
    ].mean().round(2))

print("--")

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability']

# Rater-wise z-scores.
for dim in dimensions:
    df_mapped[f'{dim}_z'] = df_mapped.groupby('rater')[dim].transform(
        lambda x: (x - x.mean()) / x.std()
    )


def compute_alpha(df, dim_col, measurement):
    df['unit'] = df['case_order'].astype(str) + '_' + df['system']
    units = df['unit'].unique()
    raters = sorted(df['rater'].unique())

    matrix = np.full((len(raters), len(units)), np.nan)
    unit_idx = {u: i for i, u in enumerate(units)}

    for _, row in df.iterrows():
        r = raters.index(row['rater'])
        u = unit_idx[row['unit']]
        val = row[dim_col]

        if pd.notna(val):
            matrix[r, u] = float(val)

    return krippendorff.alpha(
        reliability_data=matrix,
        level_of_measurement=measurement
    )


# Mean score pattern per rater.
rater_means = df_mapped.groupby('rater')[dimensions].mean().round(2)

print("=== Bewertungsverhalten pro Rater ===")
print(rater_means)

# Alpha on original ordinal scores and rater-standardized scores.
all_alpha_results = []

for dim in dimensions:
    alpha_orig = compute_alpha(df_mapped, dim, 'ordinal')
    alpha_std = compute_alpha(df_mapped, f'{dim}_z', 'interval')

    all_alpha_results.append({
        'dimension': dim,
        'alpha_original': round(alpha_orig, 4),
        'alpha_standardized': round(alpha_std, 4),
    })

    print(f"{dim}: α_original = {round(alpha_orig, 4)} | α_standardized = {round(alpha_std, 4)}")

alpha_df = pd.DataFrame(all_alpha_results)

with pd.ExcelWriter('krippendorff_alpha.xlsx') as writer:
    alpha_df.to_excel(writer, sheet_name='alpha', index=False)
    rater_means.to_excel(writer, sheet_name='rater_means')

print("\nGespeichert: krippendorff_alpha.xlsx")