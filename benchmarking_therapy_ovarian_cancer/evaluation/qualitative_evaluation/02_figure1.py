import pandas as pd

# Summarize the Likert score distribution for each system and rating dimension.
df_mapped = pd.read_excel('qualitative_mapped.xlsx')

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability']
systems = ['Referenz', 'LLM', 'RAG', 'GraphRAG']
likert = [1, 2, 3]

records = []

for system in systems:
    df_sys = df_mapped[df_mapped['system'] == system]

    for dim in dimensions:
        total = df_sys[dim].notna().sum()

        for val in likert:
            count = (df_sys[dim] == val).sum()
            pct = round(count / total * 100, 1) if total > 0 else 0

            records.append({
                'system': system,
                'dimension': dim,
                'rating': val,
                'count': count,
                'percent': pct,
                'total': total,
            })


df_likert = pd.DataFrame(records)

# Percent table used for reporting.
df_pivot = df_likert.pivot_table(
    index=['system', 'dimension'],
    columns='rating',
    values='percent'
).reset_index()

df_pivot.columns = ['system', 'dimension', 'pct_poor', 'pct_acceptable', 'pct_good']

print(df_pivot.to_string())

with pd.ExcelWriter('likert_distributions.xlsx') as writer:
    df_likert.to_excel(writer, sheet_name='raw_counts', index=False)
    df_pivot.to_excel(writer, sheet_name='pivot_percent', index=False)

print("\nGespeichert: likert_distributions.xlsx")