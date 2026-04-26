import pandas as pd
import re

# Convert raw questionnaire exports into one row per rater, case, and system.
df_study = pd.read_excel('/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/qualitative_eval/Studienaufbau kopie.xlsx')
# TODO generalize
df_responses = pd.read_excel(
    '/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/qualitative_eval/Qualitative Evaluation von Therapieempfehlungen bei Ovarialkarzinom (Responses).xlsx'
)


def parse_likert(val):
    """Extract the numeric Likert score from the response text."""
    if pd.isna(val):
        return None

    s = str(val)

    if s.startswith('1'):
        return 1
    if s.startswith('2'):
        return 2
    if s.startswith('3'):
        return 3

    return None


# Map recommendation letters to the underlying system for each case.
method_map = {}

for _, row in df_study.iterrows():
    case_order = int(row['Case order google form'])
    method_map[case_order] = {
        'A': row['A_method'],
        'B': row['B_method'],
        'C': row['C_method'],
        'D': row['D_method'],
        'orig_case': int(row['Case']),
    }


dimensions = ['Korrektheit', 'Vollständigkeit', 'Verständlichkeit', 'Würdest du']
dim_keys = ['correctness', 'completeness', 'comprehensibility', 'applicability']

records = []

for rater_idx, rater_row in df_responses.iterrows():
    for case_order in range(1, 20):
        for letter in ['A', 'B', 'C', 'D']:
            system = method_map[case_order][letter]

            record = {
                'rater': rater_idx + 1,
                'case_order': case_order,
                'orig_case': method_map[case_order]['orig_case'],
                'letter': letter,
                'system': system,
            }

            # Rating dimensions for the current recommendation.
            for dim, dim_key in zip(dimensions, dim_keys):
                col_prefix = f'Bewertung Empfehlung {letter} (Fall {case_order}) [{dim}'
                matching = [c for c in df_responses.columns if c.startswith(col_prefix)]
                record[dim_key] = parse_likert(rater_row[matching[0]]) if matching else None

            # Preferred recommendation for the current case.
            pref_prefix = 'Welche der Empfehlungen A–D ist insgesamt die Beste'
            pref_cols = [c for c in df_responses.columns if c.startswith(pref_prefix)]

            if case_order <= len(pref_cols):
                pref_letter = str(rater_row[pref_cols[case_order - 1]]).strip()
                record['preferred_letter'] = pref_letter
                record['preferred_system'] = method_map[case_order].get(pref_letter, pref_letter)

            # Recommendation perceived as human-written.
            human_prefix = 'Welche Empfehlung wurde deiner Einschätzung nach von Menschen'
            human_cols = [c for c in df_responses.columns if c.startswith(human_prefix)]

            if case_order <= len(human_cols):
                guess_letter = str(rater_row[human_cols[case_order - 1]]).strip()
                record['human_guess_letter'] = guess_letter
                record['human_guess_system'] = method_map[case_order].get(guess_letter, guess_letter)

            records.append(record)


df_mapped = pd.DataFrame(records)

df_mapped.to_excel('qualitative_mapped.xlsx', index=False)

print(f"Shape: {df_mapped.shape}")
print(df_mapped.head(8).to_string())