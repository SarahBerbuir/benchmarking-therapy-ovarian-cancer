from typing import Callable
from .knowledge_graph import KG
from .fact_extraction.fact_extractor_llm import extract_single_fact_llm

def run_evidence_pass(
    kg: KG,
    pid: str,
    patient_text: str,
    llm_json: Callable[[str, dict], dict],
) -> None:
    """Extract evidence facts and mark steps completed if evidence==true"""
    evidence = kg.run_list("""
        MATCH (s:Step)-[:EVIDENCE_HINTS]->(fk:FactKey)
        RETURN s.name AS step, fk.key AS ev_key
    """)

    print(f"[evidence] pid={pid} | hints={len(evidence)}")

    for row in evidence:
        step = row["step"]
        ev_key = row["ev_key"]
        res, conf = extract_single_fact_llm(llm_json, ev_key, patient_text)
        val = res.get(ev_key, False)
        print(f"  • {step}: {ev_key} -> {val}")
        # TODO get confidence from LLM
        kg.upsert_fact(pid, ev_key, val, source="llm:evidence", conf=conf)

    # evidence true -> completed
    kg.run_write("""
        MATCH (p:Patient {pid:$pid})
        MATCH (p)-[:HAS_FACT]->(pf:PatientFact)-[:OF_KEY]->(fk:FactKey)
        MATCH (s:Step)-[:EVIDENCE_HINTS]->(fk)
        WHERE pf.value = true
          AND NOT EXISTS { MATCH (p)-[:COMPLETED]->(s) }
        MERGE (p)-[:COMPLETED {ts:datetime(), reason:'evidence'}]->(s)
    """, pid=pid)


    completed_after = {
        row["name"] for row in kg.run_list(
            "MATCH (p:Patient {pid:$pid})-[:COMPLETED]->(s:Step) RETURN s.name AS name",
            pid=pid
        )
    }
    print(f"[evidence] pid={pid} | completed after evidence={completed_after}")

