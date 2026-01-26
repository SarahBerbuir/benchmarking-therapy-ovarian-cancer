def test_upsert_and_get_facts(kg):
    kg.upsert_patient("P1")
    kg.upsert_fact("P1", "M2_ascites", True, source="llm", conf=0.95)
    facts = kg.get_patient_facts("P1")
    assert facts["M2_ascites"] is True

def test_frontier_malignant_routes_to_ct(kg):
    kg.upsert_patient("P2")
    # IOTA-Output -> CT Frontier, Zyste not
    kg.upsert_fact("P2", "iota_res", "maligne_wahrscheinlich", source="eval:iota", conf=1.0)
    frontier = kg.frontier_steps("P2")
    names = [n for n, kind in frontier]
    assert "CT Thorax/Abdomen" in names
    assert "Zystenklassifikation (BD-Klassifikation)" not in names

def test_frontier_benign_routes_to_cyst(kg):
    kg.upsert_patient("P3")
    kg.upsert_fact("P3", "iota_res", "benigne_wahrscheinlich", source="eval:iota", conf=1.0)
    frontier = kg.frontier_steps("P3")
    names = [n for n, kind in frontier]
    assert "Zystenklassifikation (BD-Klassifikation)" in names
    assert "CT Thorax/Abdomen" not in names

def test_completed_removes_from_frontier(kg):
    pid = "P4"
    kg.upsert_patient(pid)
    kg.upsert_fact(pid, "iota_res", "maligne_wahrscheinlich", source="eval:iota", conf=1.0)
    # before Completion: CT drin
    names = [n for n, _ in kg.frontier_steps(pid)]
    assert "CT Thorax/Abdomen" in names

    # complete CT
    kg.mark_completed(pid, "CT Thorax/Abdomen")
    names2 = [n for n, _ in kg.frontier_steps(pid)]
    assert "CT Thorax/Abdomen" not in names2
