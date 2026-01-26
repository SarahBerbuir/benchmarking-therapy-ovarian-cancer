from .factschema import FACT_SCHEMA

_PATIENT_FACT_EXTRACTION_PROMPT = (
    "You are an information extraction engine.\n"
    "Return ONLY a JSON object with the requested key.\n"
    "If evidence is insufficient or contradictory, return \"unknown\".\n"
    "Never guess. Do not add any text before or after the JSON.")

def _allowed_values_line(spec: dict) -> str:
    t = spec.get("type")
    if t == "bool3":
        return 'true | false | "unknown"'
    if t == "enum":
        return " | ".join(f'"{v}"' for v in spec.get("allowed", []))
    return 'number | "unknown"'

def build_fact_prompt(key: str, patient_info: str) -> str:
    spec = FACT_SCHEMA[key]

    details = []
    if spec.get("title"):
        details.append(f'Title: {spec["title"]}')
    if spec.get("definition"):
        details.append(f'Definition: {spec["definition"]}')
    if spec.get("neg_examples"):
        details.append("Negative examples: " + ", ".join(spec["neg_examples"]))
    if spec.get("pos_examples"):
        details.append("Positive examples: " + ", ".join(spec["pos_examples"]))
    details.append("Language: German text.")
    details_block = "\n".join(details)

    allowed = _allowed_values_line(spec)

    user = f"""Patientinnenakte:
---
{patient_info}
---

Extract the following key with these allowed values:

- "{key}": {allowed} 

Guidance:
{details_block}

Return ONLY JSON (no prose, no code fences):
{{ "{key}": <value> }}"""

    return f"SYSTEM\n{_PATIENT_FACT_EXTRACTION_PROMPT}\n\nUSER\n{user}\n"