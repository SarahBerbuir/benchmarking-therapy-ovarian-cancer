from typing import Dict, Iterable, Callable
from .fact_prompt_builder import build_fact_prompt
from .factschema import validate_and_normalize, schema_for_key, FACT_SCHEMA


def extract_single_fact_llm(
        llm_json: Callable[[str, dict], dict],
        key: str, patient_info: str) -> tuple[dict[str, object], float]:

    spec = FACT_SCHEMA.get(key)
    if not spec:
        raise KeyError(f"Unknown FactKey: {key}")

    prompt = build_fact_prompt(key, patient_info)
    schema = schema_for_key(key)
    data = llm_json(prompt, schema)

    val = data.get(key, "unknown")
    print(f"\t{key}: {val}")
    #TODO calculate confidence
    conf=1.0
    return { key: validate_and_normalize(key, val)}, conf


def extract_many_facts_llm(
    llm_json: Callable[[str, dict], dict],
    keys: Iterable[str],
    patient_info: str
) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for k in keys:
        out.update(extract_single_fact_llm(llm_json, k, patient_info)[0])
    return out

