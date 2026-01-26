import pytest

from ..fact_extraction.fact_extractor_llm import extract_many_facts_llm
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.evaluator.evaluators import iota_simple_rules, B_KEYS, M_KEYS

pytestmark = pytest.mark.integration

def _blank_bm():
    return {k: "unknown" for k in (B_KEYS + M_KEYS)}

def test_ascites_present_drives_iota_to_malignant(llm_json):
    patient_info = "Sonographie: freie Flüssigkeit im Abdomen, Aszites vorhanden."
    facts = extract_many_facts_llm(llm_json, B_KEYS + M_KEYS, patient_info)
    assert facts["M2_ascites"] in (True, "unknown")
    iota = iota_simple_rules({**_blank_bm(), **facts})
    if facts["M2_ascites"] is True:
        assert iota == "maligne_wahrscheinlich"
    else:
        assert iota in {"nicht_klassifizierbar", "unknown", "maligne_wahrscheinlich", "benigne_wahrscheinlich"}

def test_no_ascites_not_force_malignant(llm_json):
    patient_info = "Sonographie: kein Aszites nachweisbar. Unauffälliger Doppler."
    facts = extract_many_facts_llm(llm_json, B_KEYS + M_KEYS, patient_info)
    assert facts["M2_ascites"] in (False, "unknown")

    iota = iota_simple_rules({**_blank_bm(), **facts})
    assert iota in {"nicht_klassifizierbar", "benigne_wahrscheinlich", "unknown"}

def test_unilocular_hint_but_no_ascites(llm_json):
    patient_info = "Sonographie: unilokuläre Zyste, kein Hinweis auf Aszites."
    facts = extract_many_facts_llm(llm_json, B_KEYS + M_KEYS, patient_info)
    iota = iota_simple_rules({**_blank_bm(), **facts})
    assert iota in {"benigne_wahrscheinlich", "nicht_klassifizierbar", "unknown", "maligne_wahrscheinlich"}
