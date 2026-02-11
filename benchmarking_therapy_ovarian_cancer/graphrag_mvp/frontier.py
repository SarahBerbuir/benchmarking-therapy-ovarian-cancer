from typing import Optional, Dict, Any
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.evaluator.execute_evaluator_generic import execute_evaluator_generic
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.knowledge_graph import KG
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.utils import ROOT_STEP


def pick_next(frontier: list[tuple[str, str, int]]):
    return frontier[0] if frontier else None

def infer_tick(
    kg: KG,
    pid: str,
    patient_text: str,
    llm_json,
    frontier
) -> Dict[str, Any]:
    """One iteration"""
    # print("[tick] frontier:", frontier)
    evals = [t for t in frontier if t[1] == "Evaluator"]
    if not evals:
        return {"did_something": False, "reason": "no_evaluator_in_frontier"}

    step_name, step_kind, _depth = evals[0]  # Frontier ist schon sortiert
    outputs = execute_evaluator_generic(kg, pid, step_name, llm_json, patient_text)
    kg.recompute_on_hold(pid, root_name=ROOT_STEP)
    return {"did_something": True, "action": "evaluate", "step": step_name, "outputs": outputs}


def run_until_stable(kg, pid, patient_text, llm_json, max_steps=100):
    history = []
    for _ in range(max_steps):
        frontier = kg.frontier_steps(pid, root_name=ROOT_STEP)
        print("[loop] frontier:", frontier)

        # STOP 1: nothing reachable
        if not frontier:
            history.append({"did_something": False, "reason": "no_frontier"})
            break

        # STOP 2: no evaluators left -> awaiting diagnostics/evidence
        has_eval = any(kind == "Evaluator" for (_name, kind, _depth) in frontier)
        if not has_eval:
            history.append({
                "did_something": False,
                "reason": "only_non_evaluators_left",
                "action": "await_diagnostic_or_evidence",
                "outputs": []
            })
            break

        r = infer_tick(kg, pid, patient_text, llm_json, frontier)
        history.append(r)

        if not r.get("did_something"):
            break

    return history
