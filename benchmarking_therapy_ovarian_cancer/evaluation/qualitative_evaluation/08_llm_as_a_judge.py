import os
import json
import time
import pandas as pd
from anthropic import Anthropic

# Run Claude-based judge ratings for each case and recommendation.
with open('credentials.json', 'r') as f:
    credentials = json.load(f)

os.environ['ANTHROPIC_API_KEY'] = credentials['ANTHROPIC_API_KEY']

df_study = pd.read_excel('/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/qualitative_eval/Studienaufbau kopie.xlsx')

study_map = {}

for _, row in df_study.iterrows():
    case_order = int(row['Case order google form'])
    study_map[case_order] = {
        'orig_case': int(row['Case']),
        'patient': str(row['Patient']),
        'A': {'method': row['A_method'], 'text': str(row['A Empfehlung'])},
        'B': {'method': row['B_method'], 'text': str(row['B Empfehlung'])},
        'C': {'method': row['C_method'], 'text': str(row['C Empfehlung'])},
        'D': {'method': row['D_method'], 'text': str(row['D Empfehlung'])},
    }

client = Anthropic()

SYSTEM_PROMPT = """Du bist ein erfahrener Facharzt für Gynäkologie und Onkologie mit langjähriger Tumorboard-Erfahrung.
Du bewertest Therapieempfehlungen für Patientinnen mit Ovarialkarzinom."""


# Tool schemas keep the model output in the expected format.
LIKERT_TOOL = {
    "name": "submit_likert_ratings",
    "description": "Übermittle die Bewertungen für eine Tumorboard-Empfehlung",
    "input_schema": {
        "type": "object",
        "properties": {
            "correctness": {
                "type": "integer",
                "enum": [1, 2, 3],
                "description": "Korrektheit: 1=schlecht, 2=akzeptabel, 3=gut"
            },
            "completeness": {
                "type": "integer",
                "enum": [1, 2, 3],
                "description": "Vollständigkeit: 1=schlecht, 2=akzeptabel, 3=gut"
            },
            "comprehensibility": {
                "type": "integer",
                "enum": [1, 2, 3],
                "description": "Verständlichkeit: 1=schlecht, 2=akzeptabel, 3=gut"
            },
            "applicability": {
                "type": "integer",
                "enum": [1, 2, 3],
                "description": "Praktische Anwendbarkeit: 1=schlecht, 2=akzeptabel, 3=gut"
            }
        },
        "required": ["correctness", "completeness", "comprehensibility", "applicability"]
    }
}

PREFERENCE_TOOL = {
    "name": "submit_preference",
    "description": "Übermittle Präferenz und Human-Detection für einen Fall",
    "input_schema": {
        "type": "object",
        "properties": {
            "preferred": {
                "type": "string",
                "enum": ["A", "B", "C", "D"],
                "description": "Die beste Empfehlung"
            },
            "human_guess": {
                "type": "string",
                "enum": ["A", "B", "C", "D", "Nicht beurteilbar"],
                "description": "Welche Empfehlung klingt am menschlichsten"
            }
        },
        "required": ["preferred", "human_guess"]
    }
}


def call_likert(
    patient_info: str,
    letter: str,
    recommendation: str,
    max_retries: int = 3
) -> dict | None:
    prompt = f"""Bewerte die folgende Tumorboard-Empfehlung anhand der Patienteninformation.

PATIENTENINFORMATION:
{patient_info}

EMPFEHLUNG {letter}:
{recommendation}

Bewerte auf einer 3-Punkte-Skala (1=schlecht, 2=akzeptabel, 3=gut):
- Korrektheit: Fachlich richtig und leitliniennah
- Vollständigkeit: Alle entscheidenden Bausteine genannt
- Verständlichkeit: Klar und tumorboard-tauglich formuliert
- Praktische Anwendbarkeit: Würde ein Kliniker dieser Empfehlung folgen

Nutze das Tool submit_likert_ratings um deine Bewertung zu übermitteln."""

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                system=SYSTEM_PROMPT,
                tools=[LIKERT_TOOL],
                tool_choice={"type": "tool", "name": "submit_likert_ratings"},
                messages=[{"role": "user", "content": prompt}]
            )

            # Read the tool-call payload.
            for block in response.content:
                if block.type == "tool_use":
                    return block.input

        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    return None


def call_preference(
    patient_info: str,
    recommendations: dict,
    max_retries: int = 3
) -> dict | None:
    recs_text = "\n\n".join([
        f"EMPFEHLUNG {letter}:\n{text}"
        for letter, text in recommendations.items()
    ])

    prompt = f"""Du siehst vier Tumorboard-Empfehlungen für denselben Fall.

PATIENTENINFORMATION:
{patient_info}

{recs_text}

Beantworte:
1. Welche Empfehlung ist insgesamt die beste?
2. Welche klingt am ehesten wie sie von einem menschlichen Tumorboard stammt?
   Falls nicht beurteilbar, wähle "Nicht beurteilbar".

Nutze das Tool submit_preference um deine Antwort zu übermitteln."""

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                system=SYSTEM_PROMPT,
                tools=[PREFERENCE_TOOL],
                tool_choice={"type": "tool", "name": "submit_preference"},
                messages=[{"role": "user", "content": prompt}]
            )

            for block in response.content:
                if block.type == "tool_use":
                    return block.input

        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    return None


likert_records = []
preference_records = []

for case_order in range(1, 20):
    row = study_map[case_order]
    patient_info = row['patient']
    orig_case = row['orig_case']

    print(f"Processing case_order={case_order} (orig_case={orig_case})...")

    # Rate all four recommendations separately.
    for letter in ['A', 'B', 'C', 'D']:
        method = row[letter]['method']
        rec_text = row[letter]['text']

        print(f"  Likert: {letter} → {method}")

        ratings = call_likert(patient_info, letter, rec_text)

        if ratings is None:
            print(f"  WARNING: failed for case={case_order}, letter={letter}")
            ratings = {
                'correctness': None,
                'completeness': None,
                'comprehensibility': None,
                'applicability': None,
            }

        likert_records.append({
            'case_order': case_order,
            'orig_case': orig_case,
            'letter': letter,
            'system': method,
            'correctness': ratings.get('correctness'),
            'completeness': ratings.get('completeness'),
            'comprehensibility': ratings.get('comprehensibility'),
            'applicability': ratings.get('applicability'),
        })

        time.sleep(0.5)

    # Ask for the best and most human-like recommendation once per case.
    print("  Preference + Human Detection...")

    recs = {l: row[l]['text'] for l in ['A', 'B', 'C', 'D']}
    pref_data = call_preference(patient_info, recs)

    if pref_data is None:
        print(f"  WARNING: preference failed for case={case_order}")
        pref_data = {'preferred': None, 'human_guess': None}

    preferred_letter = pref_data.get('preferred')
    human_guess_letter = pref_data.get('human_guess')

    preferred_system = row.get(preferred_letter, {}).get('method') \
        if preferred_letter in ['A', 'B', 'C', 'D'] else None

    human_guess_system = row.get(human_guess_letter, {}).get('method') \
        if human_guess_letter in ['A', 'B', 'C', 'D'] else human_guess_letter

    preference_records.append({
        'case_order': case_order,
        'orig_case': orig_case,
        'preferred_letter': preferred_letter,
        'preferred_system': preferred_system,
        'human_guess_letter': human_guess_letter,
        'human_guess_system': human_guess_system,
    })

    time.sleep(0.5)


df_likert = pd.DataFrame(likert_records)
df_preference = pd.DataFrame(preference_records)

print("\n=== NaN counts ===")
print(df_likert.isna().sum())

print("\n=== Likert Mittelwerte ===")
print(df_likert.groupby('system')[
    ['correctness', 'completeness', 'comprehensibility', 'applicability']
].mean().round(2))

print("\n=== Präferenz ===")
print(df_preference['preferred_system'].value_counts())

print("\n=== Human Detection ===")
print(df_preference['human_guess_system'].value_counts())

with pd.ExcelWriter('llm_as_a_judge_v2.xlsx') as writer:
    df_likert.to_excel(writer, sheet_name='likert_ratings', index=False)
    df_preference.to_excel(writer, sheet_name='preference_human', index=False)

print("\nGespeichert: llm_as_a_judge_v2.xlsx")