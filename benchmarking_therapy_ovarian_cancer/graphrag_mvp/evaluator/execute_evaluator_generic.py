from benchmarking_therapy_ovarian_cancer.graphrag_mvp.fact_extraction.factschema import validate_and_normalize
from typing import Callable, Dict, Any
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.knowledge_graph import KG
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.fact_extraction.fact_extractor_llm import extract_single_fact_llm
from .evaluators import iota_simple_rules, bd_classification, set_op_plan, set_figo_bucket, set_debulking_possible, \
    set_hrd_brca_status, set_planning_neoadjuvant_therapy, set_neoadjuvant_next_step, set_next_step_therapy, \
    set_repeat_debulking_operabel_ass, set_planning_adjuvant_therapy, set_maintenance_therapy, set_adjuvant_next_step, \
    resolve_path_stage_grade_lap, resolve_path_stage_grade_lsk

EVAL_NEEDS_LLM = {
    "bd_classification",
    "set_debulking_possible",
    "set_repeat_debulking_operabel_ass",
    "resolve_path_stage_grade_lap",
    "resolve_path_stage_grade_lsk",
}

EVAL_DISPATCH: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any] | str]] = {
    "iota_simple_rules": iota_simple_rules,
    "bd_classification": bd_classification,
    "set_op_plan": set_op_plan,
    "set_figo_bucket": set_figo_bucket,
    "set_debulking_possible": set_debulking_possible,
    "set_hrd_brca_status": set_hrd_brca_status,
    "set_planning_neoadjuvant_therapy": set_planning_neoadjuvant_therapy,
    "set_neoadjuvant_next_step": set_neoadjuvant_next_step,
    "set_adjuvant_next_step": set_adjuvant_next_step,
    "set_next_step_therapy": set_next_step_therapy,
    "set_repeat_debulking_operabel_ass": set_repeat_debulking_operabel_ass,
    "set_planning_adjuvant_therapy": set_planning_adjuvant_therapy,
    "set_maintenance_therapy": set_maintenance_therapy,
    "resolve_path_stage_grade_lap": resolve_path_stage_grade_lap,
    "resolve_path_stage_grade_lsk": resolve_path_stage_grade_lsk
}

def execute_evaluator_generic(
    kg: KG,
    pid: str,
    step_name: str,
    llm_json: Callable[[str, dict], dict],
    patient_text: str,
) -> Dict[str, object]:

    logic = kg.step_logic(step_name)
    if  not logic or logic != "set_route_flag" and logic not in EVAL_DISPATCH:
        raise RuntimeError(f"No evaluator function for logic='{logic}' on '{step_name}'")

    # Collect needed inputs
    need_keys = kg.step_needs(step_name)
    requires = kg.step_requires(step_name)
    facts = kg.get_patient_facts(pid)

    for key in need_keys:
        if key not in facts:
            print(f"[eval] {step_name}: Missing input -> {key}")
    for req_key, req_val in requires:
        have = facts.get(req_key, None)
        if have != req_val:
            print(f"[eval] {step_name}: REQUIRES not met -> {req_key} need=={req_val!r} have=={have!r}")


    provide_keys = kg.step_provides(step_name)
    if not provide_keys:
        raise RuntimeError(f"Step '{step_name}' provides no facts (no PROVIDES_FACT edges).")

    # Run logic
    if logic == "set_route_flag":
        result: Dict[str, Any] = {k: True for k in provide_keys}
    else:
        print(f"[eval] {step_name}: Logic '{logic}'")
        if logic in EVAL_NEEDS_LLM:
            result = EVAL_DISPATCH[logic](facts, patient_text, llm_json)
        else:
            result = EVAL_DISPATCH[logic](facts)
        if result == {}:
            print(f"[eval] evaluator {step_name} returned unknown result. Nothing saved for patient")
            kg.mark_failed(pid, step_name)
            return result
        if not isinstance(result, dict): # if node has more then one provide fact relation and function doesn't return dict -> error
            if len(provide_keys) != 1:
                raise RuntimeError(
                    f"Evaluator '{logic}' returned scalar but step '{step_name}' provides {len(provide_keys)} facts: {provide_keys}. "
                )
            result = {provide_keys[0]: result}

    outputs: Dict[str, Any] = {}

    for key in provide_keys:
        if key in result:
            value = validate_and_normalize(key, result[key])
            # TODO conf
            kg.upsert_fact(pid=pid, key=key, value=value, source=f"logic:{logic}", conf=1.0)
            outputs[key] = value
        else:
            raise RuntimeError(
                f"Evaluator '{logic}' did not return provided key '{key}' for step '{step_name}'. "
                f"Returned keys: {list(result.keys())}"
            )

    kg.mark_completed(pid, step_name)
    facts_after = kg.get_patient_facts(pid)
    print(f"[eval] {step_name}: outputs -> {outputs}")
    print(f"[eval] patient facts snapshot -> {facts_after}")
    return outputs

# inference.py

def log_step_readiness(kg, pid: str, step_name: str, only_if_missing: bool = True) -> None:
    """
    Soft-Logger für jeden Step:
    - listet NEEDS_FACT (Wert vorhanden? Provider completed?)
    - listet REQUIRES_FACT (Gate erfüllt? PatientFact vorhanden?)
    """
    needs = kg.step_needs(step_name)          # -> List[str]
    requires = kg.step_requires(step_name)    # -> List[Tuple[str, Any]]
    facts = kg.get_patient_facts(pid)         # -> Dict[str, Any]

    header = f"[frontier] {step_name}"
    lines = []

    # NEEDS_FACT: Wert + Provider-Completion
    for key in needs:
        val = facts.get(key, None)
        providers = kg.providers_of_fact(key)                # -> List[str] (Step-Namen/-IDs)
        provider_done = any(kg.is_step_completed(pid, s) for s in providers)
        line = f"  NEED  {key:<32} value={val!r:<12} provider_completed={provider_done} providers={providers}"
        if not only_if_missing or val is None or val == "unknown" or not provider_done:
            lines.append(line)

    # REQUIRES_FACT: Gate-Abgleich (ALLES muss erfüllt sein)
    for key, req_val in requires:
        have = facts.get(key, None)
        ok = (have == req_val)
        line = f"  REQ   {key:<32} need=={req_val!r:<10} have={have!r:<10} ok={ok}"
        if not only_if_missing or not ok:
            lines.append(line)

    if lines:
        print(header)
        for l in lines:
            print(l)
