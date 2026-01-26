from benchmarking_therapy_ovarian_cancer.graphrag_mvp.fact_extraction.factschema import validate_and_normalize
from typing import Callable, Dict, Any
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.knowledge_graph import KG
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.fact_extraction.fact_extractor_llm import extract_single_fact_llm
from .evaluators import iota_simple_rules

EVAL_DISPATCH: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any] | str]] = {
    "iota_simple_rules": iota_simple_rules,
}

def execute_evaluator_generic(
    kg: KG,
    pid: str,
    step_name: str,
    llm_json: Callable[[str, dict], dict],
    patient_text: str,
) -> Dict[str, object]:

    logic = kg.step_logic(step_name)
    if not logic or logic not in EVAL_DISPATCH:
        raise RuntimeError(f"No evaluator function for logic='{logic}' on '{step_name}'")

    # Collect needed inputs
    need_keys = kg.step_needs(step_name)
    facts = kg.get_patient_facts(pid)

    # Fill missing/unknown inputs
    missing = [k for k in need_keys if facts.get(k) in (None, "unknown")]
    if missing:
        print(f"[eval] {step_name}: Missing inputs -> {missing}")
    for key in missing:
        fact_dict, conf = extract_single_fact_llm(llm_json, key, patient_text)
        val = fact_dict[key]
        kg.upsert_fact(pid=pid, key=key, value=val, source=f"llm:{step_name}:input", conf=conf)

    facts_now = kg.get_patient_facts(pid)

    # Run logic
    result = EVAL_DISPATCH[logic](facts_now)

    provide_keys = kg.step_provides(step_name)
    outputs: Dict[str, Any] = {}

    if isinstance(result, dict):
        for key in provide_keys:
            if key in result:
                value = validate_and_normalize(key, result[key])
                # TODO conf
                kg.upsert_fact(pid=pid, key=key, value=value, source=f"logic:{logic}", conf=1.0)
                outputs[key] = value
    else:
        if len(provide_keys) != 1:
            raise RuntimeError(
                f"Expected exactly 1 PROVIDED_FACT for '{step_name}', got {len(provide_keys)}: {provide_keys}"
            )
        out_key = provide_keys[0]
        out_val = validate_and_normalize(out_key, result)
        # TODO conf
        kg.upsert_fact(pid=pid, key=out_key, value=out_val, source=f"logic:{logic}", conf=1.0)
        outputs[out_key] = out_val

    kg.mark_completed(pid, step_name)
    print(f"[eval] {step_name}: outputs -> {outputs}")
    return outputs
