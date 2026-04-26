import pandas as pd

# Compare mean Likert ratings by case status and system.
df_mapped = pd.read_excel('qualitative_mapped.xlsx')

# TODO generalize
df_study = pd.read_excel('/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/qualitative_eval/Studienaufbau kopie.xlsx')

status_map = dict(zip(
    df_study['Case order google form'],
    df_study['Status']
))

df_mapped['status'] = df_mapped['case_order'].map(status_map)

print(df_mapped.groupby(['status', 'system'])[
    ['correctness', 'completeness', 'comprehensibility', 'applicability']
].mean().round(2))