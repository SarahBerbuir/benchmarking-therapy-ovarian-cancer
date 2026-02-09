from typing import Callable, Any, Dict
from .knowledge_graph import KG
from .fact_extraction.fact_extractor_llm import extract_single_fact_llm

UNKNOWN_VALUES = {None, "unknown", "UNK", "Unknown"}

def _is_unknown(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and v.strip() in UNKNOWN_VALUES:
        return True
    return False

def _apply_step_specific_policy(step: str, values: Dict[str, Any], ok_so_far: bool) -> bool:
    """
    Conditional-hard logic. Explicit for MVP
    """
    if not ok_so_far:
        return False
    if step == "Laparotomie, SS":
        hist = values.get("histology_laparotomy", "unknown")
        if hist == "maligne":
            if _is_unknown(values.get("grade_laparotomy")) or _is_unknown(values.get("figo_path_laparotomy")):
                return False

    if step == "Laparoskopie oder Minilaparotomie":
        hist = values.get("histology_laparoscopy", "unknown")
        if hist == "maligne":
            if _is_unknown(values.get("grade_laparoscopy")) or _is_unknown(values.get("figo_path_laparoscopy")):
                return False
    return True

def run_evidence_pass(
    kg: KG,
    pid: str,
    patient_text: str,
    llm_json: Callable[[str, dict], dict],
) -> None:
    """
        Robust MVP evidence-pass:

        1) evidence_hint_true := LLM extracts ev_key (true/false).
        2) If evidence_hint_true:
             - mark PERFORMED
             - extract ALL PROVIDES_FACT for the step
             - no_unknown_provides := none of extracted provides is unknown
           else:
             - skip provides extraction
        3) final_ev := evidence_hint_true AND no_unknown_provides
        4) final_ev true => mark COMPLETED
        """
    hinted = kg.run_list("""
            MATCH (s:Step)-[:EVIDENCE_HINTS]->(evfk:FactKey)
            RETURN s.name AS step, evfk.key AS ev_key
        """)

    print(f"[evidence] pid={pid} | hinted_steps={len(hinted)}")

    for row in hinted:
        step = row["step"]
        ev_key = row["ev_key"]

        # evidence hint extraction
        res, conf = extract_single_fact_llm(llm_json, ev_key, patient_text)
        evidence_hint_true = bool(res.get(ev_key, False))
        kg.upsert_fact(pid, ev_key, evidence_hint_true, source="llm:evidence_hint", conf=conf)

        print(f"  • {step}: hint {ev_key} -> {evidence_hint_true}")

        # if hinted true => performed + provides extraction
        no_unknown_hard = True
        provides = kg.step_provides_meta(step)

        if evidence_hint_true:
            # PERFOMED is useful for later verbalization, not for frontier
            kg.mark_performed(pid, step, reason="evidence_hint_true")
            values = {}
            for item in provides:
                fact = item["key"]
                hard = item["hard"]

                pres, pconf = extract_single_fact_llm(llm_json, fact, patient_text)
                val = pres.get(fact, "unknown")
                kg.upsert_fact(pid, fact, val, source=f"llm:provides:{step}", conf=pconf)
                values[fact] = val

                if hard and _is_unknown(val):
                    no_unknown_hard = False
            no_unknown_hard = _apply_step_specific_policy(step, values, no_unknown_hard)

        else:
            no_unknown_hard = False

        # final evidence
        final_ev = bool(evidence_hint_true and no_unknown_hard)

        # overwrite ev_key with final_ev (important!)
        kg.upsert_fact(pid, ev_key, final_ev, source="system:ev_and_no_unknown_provides", conf=1.0)

        print(f"    -> provides={len(provides)} no_unknown_hard={no_unknown_hard} => final {ev_key}={final_ev}")

        # final_ev => COMPLETED
        if final_ev:
            kg.mark_completed(pid, step)

    completed_after = [r["name"] for r in kg.run_list(
        "MATCH (p:Patient {pid:$pid})-[:COMPLETED]->(s:Step) RETURN s.name AS name",
        pid=pid
    )]
    performed_after = [r["name"] for r in kg.run_list(
        "MATCH (p:Patient {pid:$pid})-[:PERFORMED]->(s:Step) RETURN s.name AS name",
        pid=pid
    )]
    print(f"[evidence] completed={completed_after}")
    print(f"[evidence] performed={performed_after}")
