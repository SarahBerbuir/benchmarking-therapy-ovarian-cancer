from .frontier import run_until_stable
from .generate_recommendation import get_graph_recommendation
from .knowledge_graph import KG
from .evidence_pass import run_evidence_pass
from .utils import ROOT_STEP
from ..llm_vertex import init_vertexai_llm, get_json_llm_fn



def run_inference(kg: KG, pid: str, patient_text: str):
    model = init_vertexai_llm()
    llm_json = get_json_llm_fn(model)

    kg.upsert_patient(pid)

    # Collect evidence flags from patient and set steps which have evidence on COMPLETED
    run_evidence_pass(kg, pid, patient_text, llm_json)

    # On hold for steps which are on path root to complete nodes
    kg.recompute_on_hold(pid, root_name=ROOT_STEP)

    completed = [row["name"] for row in kg.run_list(
        "MATCH (p:Patient {pid:$pid})-[:COMPLETED]->(s:Step) RETURN s.name AS name",
        pid=pid
    )]
    frontier = kg.frontier_steps(pid, root_name=ROOT_STEP)

    print(f"[start] completed={completed}")
    print(f"[start] frontier={frontier}")

    history = run_until_stable(kg, pid, patient_text, llm_json)
    print(f"[start] run_until_stable: {len(history)} ticks")

    completed = [row["name"] for row in kg.run_list(
        "MATCH (p:Patient {pid:$pid})-[:COMPLETED]->(s:Step) RETURN s.name AS name",
        pid=pid
    )]
    frontier = kg.frontier_steps(pid, root_name=ROOT_STEP)

    print(f"[endInference] completed={completed}")
    print(f"[endInference] frontier={frontier}")
    # TODO what to do, where is patient now


    summary = {
        "completed": completed,
        "frontier": frontier,
        "history": history,
        "llm_json": llm_json,
    }
    print(f"[endInference] {summary}")

    anchor = kg.pick_anchor(pid, root_name=ROOT_STEP)
    print(f"[anchor] anchor={anchor}")


    therapy_recommendation = get_graph_recommendation(kg, pid, anchor)
    print(f"[therapy_recommendation] {therapy_recommendation}")
    return therapy_recommendation
