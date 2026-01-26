from typing import Optional, Dict, Any
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.evaluator.execute_evaluator_generic import execute_evaluator_generic
from .knowledge_graph import KG
from .evidence_pass import run_evidence_pass
from ..llm_vertex import init_vertexai_llm, get_json_llm_fn


# TODO
def pick_next(frontier: list[tuple[str, str]]) -> Optional[tuple[str, str]]:
    """Priority for now Evaluator"""
    evals = [t for t in frontier if t[1] == "Evaluator"]
    return evals[0] if evals else (frontier[0] if frontier else None)

def infer_tick(
    kg: KG,
    pid: str,
    patient_text: str,
    llm_json,
) -> Dict[str, Any]:
    """One iteration"""
    frontier = kg.frontier_steps(pid) # [(name, kind)]
    nxt = pick_next(frontier)
    if not nxt:
        return {
            "did_something": False,
            "reason": "no_frontier"
        }

    step_name, step_kind = nxt

    if step_kind == "Evaluator":
        outputs = execute_evaluator_generic(kg, pid, step_name, llm_json, patient_text)
        kg.recompute_on_hold(pid, root_name="Vorsorge/Symptome")
        return {
            "did_something": True,
            "action": "evaluate",
            "step": step_name,
            "outputs": outputs,
        }

    expected = kg.step_provides(step_name)
    return {
        "did_something": False,
        "action": "await_diagnostic_or_evidence",
        "step": step_name,
        "expected_outputs": expected,
    }

def run_until_stable(kg, pid, patient_text, llm_json, max_steps=3):
    history = []
    for _ in range(max_steps):
        r = infer_tick(kg, pid, patient_text, llm_json)
        history.append(r)
        if not r.get("did_something"):
            #TODO
            break # stop, no progress
    return history

def start_inference(kg: KG, pid: str, patient_text: str):
    """Init LLM, evidence pass, then one frontier tick."""
    model = init_vertexai_llm()
    llm_json = get_json_llm_fn(model)

    kg.upsert_patient(pid)

    # Collect evidence flags from patient and set steps which have evidence on COMPLETED
    run_evidence_pass(kg, pid, patient_text, llm_json)

    # TODO
    # On hold for steps which are on path root to complete nodes
    kg.recompute_on_hold(pid, root_name="Vorsorge/Symptome")

    completed = [row["name"] for row in kg.run_list(
        "MATCH (p:Patient {pid:$pid})-[:COMPLETED]->(s:Step) RETURN s.name AS name",
        pid=pid
    )]
    frontier = kg.frontier_steps(pid)  # [(name, kind), …]

    print(f"[start] completed={completed}")
    print(f"[start] frontier={frontier}")

    history = run_until_stable(kg, pid, patient_text, llm_json, max_steps=3)
    print(f"[start] run_until_stable: {len(history)} ticks")

    # TODO what to do, where is patient now
    return {
        "completed": completed,
        "frontier": frontier,
        "history": history,
        "llm_json": llm_json,
    }
