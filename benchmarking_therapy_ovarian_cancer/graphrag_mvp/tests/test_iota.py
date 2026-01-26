from benchmarking_therapy_ovarian_cancer.graphrag_mvp.evaluator.evaluators import iota_simple_rules, B_KEYS, M_KEYS

not_classifiable = "nicht_klassifizierbar"
benigne_probable = "benigne_wahrscheinlich"
maligne_probable = "maligne_wahrscheinlich"

def test_all_unknown():
    facts = {k: "unknown" for k in (B_KEYS + M_KEYS)}
    assert iota_simple_rules(facts) == "unknown"

def test_all_false():
    facts = {k: False for k in (B_KEYS + M_KEYS)}
    assert iota_simple_rules(facts) == not_classifiable

def test_only_b():
    assert iota_simple_rules({"B1_unilokulaer": True}) == benigne_probable

def test_only_m():
    assert iota_simple_rules({"M2_ascites": True}) == maligne_probable

def test_m_greater_than_b():
    facts = {"M2_ascites": True, "M3_ge4_papillae": True, "B1_unilokulaer": True}
    assert iota_simple_rules(facts) == maligne_probable

def test_b_greater_than_m():
    facts = {"M2_ascites": True, "B2_solide_lt7mm": True, "B1_unilokulaer": True}
    assert iota_simple_rules(facts) != benigne_probable

def test_b_equals_m_nonzero():
    facts = {"B3_schallschatten": True, "M1_unreg_solid": True}
    assert iota_simple_rules(facts) == not_classifiable
