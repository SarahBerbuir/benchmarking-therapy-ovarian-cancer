from typing import Dict, Any, Callable

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.fact_extraction.fact_extractor_llm import extract_single_fact_llm
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.fact_extraction.factschema import FIGO_STAGES, FIGO_IV, FIGO_III, FIGO_II, FIGO_I

B_KEYS = [
    "B1_unilokulaer",
    "B2_solide_lt7mm",
    "B3_schallschatten",
    "B4_glatt_multilok_lt10cm",
    "B5_keine_doppler_flow",
]

M_KEYS = [
    "M1_unreg_solid",
    "M2_ascites",
    "M3_ge4_papillae",
    "M4_unreg_multilok_solid_gt10cm",
    "M5_hoher_doppler_flow",
]


def iota_simple_rules(facts: Dict[str, Any]) -> dict[str, str]:
    """
        Computes IOTA Simple Rules outcome.
        provides: {"iota_res": one of {"benigne_wahrscheinlich","maligne_wahrscheinlich","nicht_klassifizierbar"}}
        needs: the B/M sonography feature flags.
        """
    # True, False/None/"unknown" don´t count
    b = sum(1 for k in B_KEYS if facts.get(k) is True)
    m = sum(1 for k in M_KEYS if facts.get(k) is True)

    values = [facts.get(k) for k in (B_KEYS + M_KEYS)]
    any_known = any(v is True or v is False for v in values)

    if  not any_known: # not possible
        iota_res = "nicht_klassifizierbar"
    elif m >= 1 and b == 0:
        iota_res = "maligne_wahrscheinlich"
    elif m > b:
        iota_res = "maligne_wahrscheinlich"
    elif b >= 1 and m == 0:
        iota_res = "benigne_wahrscheinlich"
    else:
        # b==0 and m==0, b>=m
        iota_res = "nicht_klassifizierbar"

    print(f"Count benign: {b}, Count malignant: {m}, Iota: {iota_res}")
    return {"iota_res": iota_res}


def bd_classification(facts: Dict[str, Any], patient_info: str, llm_json: Callable[[str, dict], dict],) -> dict[str, str]:
    """
    Computes BD cyst classification (only relevant if IOTA suggests benign).
    provides: {"cyst_bd": one of {"BD1","BD2","BD3", "BD4", "unknown"}}
    """
    key = "cyst_bd"
    cyst_bd = str(extract_single_fact_llm(llm_json, key, patient_info)[0][key])
    print(f"[evaluator] Cyst BD classification: {cyst_bd}")
    return {"cyst_bd": cyst_bd}

def set_op_plan(facts: Dict[str, Any]) -> dict[str, str]:
    """
        Decides OP plan based on cyst BD and clinical context.
        provides: {"op_plan": one of {"no_op","Zystenausschälung","Adnektomie"}}
        needs: ["cyst_bd","praemenopausal","symptoms_present","growth","persistence",
                "complex_multiloculaer","psychic_unsure","ca125_u_ml","size_cm"]
        """
    praemenopausal = facts.get("praemenopausal")
    symptoms_present = facts.get("symptoms_present")
    growth = facts.get("growth")
    persistence = facts.get("persistence")
    complex_multiloculaer = facts.get("complex_multiloculaer")
    psychic_unsure = facts.get("psychic_unsure")
    ca125_u_ml = facts.get("ca125_u_ml")
    size_cm = facts.get("size_cm")
    cyst_bd = facts.get("cyst_bd")

    praemenopausal_clues = (symptoms_present or growth or persistence or size_cm>=5 or cyst_bd in ["BD1", "BD2"])
    menopausal_clues = (complex_multiloculaer or psychic_unsure or growth or persistence or ca125_u_ml>=35)
    if praemenopausal and praemenopausal_clues:
        op_plan = "Zystenausschälung"
    elif praemenopausal and not praemenopausal_clues:
        op_plan = "no_op"
    elif not praemenopausal and menopausal_clues:
        op_plan = "Adnektomie"
    else:
        op_plan = "no_op"
    print(f"[evaluator]: OP plan: {op_plan}")
    return {"op_plan": op_plan}


def set_figo_bucket(facts: Dict[str, Any]) -> dict[str, str]:
    """
    Buckets clinical FIGO (from CT/clinical) into early/advanced.
    provides: {"figo_bucket": one of {"early","advanced"}}
    needs: ["figo_clinical"]
    """
    figo_clinical = facts.get("figo_clinical")
    cut = FIGO_STAGES.index("IIIC") # TODO richtig ?
    s = figo_clinical.upper().replace(" ", "")
    if s in set(FIGO_STAGES[:cut]):
        bucket = "early"
    elif s in set(FIGO_STAGES[cut:]):
        bucket = "advanced"
    print(f"[evaluator]: FIGO bucket: {bucket}")
    return {"figo_bucket": bucket}


def set_debulking_possible(facts: Dict[str, Any], patient_info:str, llm_json: Callable[[str, dict], dict]) -> dict[
    str, object]:
    """
    Determines if primary debulking is possible.
    provides: {"debulking_possible": one of {True, False, "unknown"}}
    """
    key = "debulking_possible"
    debulking_possible = extract_single_fact_llm(llm_json, key, patient_info)[0][key]
    print(f"[evaluator]: Debulking possible: {debulking_possible}")
    return {"debulking_possible": debulking_possible}

def set_hrd_brca_status(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolves BRCA/HRD status from germline and tumor testing.
    provides: {"hrd_status": one of {"+","-"}, "brca_status": one of {"+","-"}}
    """
    g_brca = facts.get("gBRCA1/2")  # "+"/"-"/None
    s_hrd = facts.get("sHRD")  if "sHRD" in facts.keys() else None

    if s_hrd == None or g_brca == "+":
        hrd = "+"
        brca = g_brca # "+"
    else:
        brca = g_brca
        hrd = s_hrd
    print(f"[evaluator]: HRD status: {hrd}, BRCA status {brca}")
    return {"hrd_status": hrd, "brca_status": brca}

def get_higher_figo(figo_clinical, figo_path):
    # Take higher FIGO stage from figo_path and figo_clinical
    ip = FIGO_STAGES.index(figo_path)
    ic = FIGO_STAGES.index(figo_clinical)
    if ip > ic:
        return figo_path
    else:
        return figo_clinical

def get_systematic_therapy_strategy_and_step(facts, type_surgery):
    if type_surgery not in ["laparoscopy", "laparotomy"]:
        raise ValueError("Invalid type op")
    cycle_amount = "3x" if type_surgery == "laparoscopy" else "6x"

    grade = facts.get(f"grade_{type_surgery}")
    figo_clinical = facts.get("figo_clinical").upper().replace(" ", "")
    figo_path = facts.get(f"figo_path_{type_surgery}").upper().replace(" ", "")

    figo = get_higher_figo(figo_clinical = figo_clinical, figo_path = figo_path)
    c_group = [s for s in FIGO_I if "C" in s]
    if figo == "IA" and grade == "low":
        return "op_only", "Nachsorge"
    elif (figo == "IA" and grade == "high") or (
            figo == "IB" and (grade == "low" or grade == "high")):  # TODO wie übersetzen IB & G1/2 ?
        return f"carboplatin_optional_{cycle_amount}", "Nachsorge"
    elif figo in c_group or ((figo == "IA" or figo == "IB") and grade == "high"):
        return f"carboplatin_{cycle_amount}", "Nachsorge"
    elif (figo in FIGO_II) or (
            figo in FIGO_III and grade == "low"):  # TODO II komplett oder wirklich "II"
        return f"carboplatin_or_paclitaxel_{cycle_amount}", "Nachsorge"
    elif figo == "IIIA" and grade == "high":
        return f"carboplatin_or_paclitaxel_{cycle_amount}", "Erhaltungstherapie"
    elif (figo in FIGO_III or figo in FIGO_IV) and figo != "IIIA" and grade == "high":
        return f"carboplatin_or_paclitaxel_bevacizumab_{cycle_amount}", "Erhaltungstherapie"
    return "op_only", "Nachsorge"


def set_planning_adjuvant_therapy(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps inputs to an adjuvant therapy plan.
    plan_strategy_adjuvant: 'carboplatin_optional_6x' | 'carboplatin_6x' | 'carboplatin_or_paclitaxel_6x' | 'carboplatin_or_paclitaxel_bevacizumab_6x'
    plan_next_step_adjuvant: 'Nachsorge' | 'Erhaltungstherapie'
    """

    plan_strategy, plan_next = get_systematic_therapy_strategy_and_step(facts=facts, type_surgery="laparotomy")
    plan_strategy += "_6x"
    print(f"[evaluator] plan_strategy_adjuvant: {plan_strategy}, plan_next_step_adjuvant: {plan_next}")
    return {
        "plan_strategy_adjuvant": plan_strategy,
        "plan_next_step_adjuvant": plan_next
    }


def set_planning_neoadjuvant_therapy(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps inputs to a neoadjuvant therapy plan.
    plan_strategy_neoadjuvant: 'op_only' | 'carboplatin_optional_3x' | 'carboplatin_3x' | 'carboplatin_or_paclitaxel_3x' | 'carboplatin_or_paclitaxel_bevacizumab_3x'
    plan_next_step_neoadjuvant: 'Nachsorge' | 'Erhaltungstherapie'
    """
    plan_strategy, plan_next = get_systematic_therapy_strategy_and_step(facts=facts, type_surgery="laparoscopy")
    plan_strategy += "_3x"
    print(f"[evaluator] plan_strategy_neoadjuvant: {plan_strategy}, plan_next_step_neoadjuvant: {plan_next}")
    return {
        "plan_strategy_neoadjuvant": plan_strategy,
        "plan_next_step_neoadjuvant": plan_next
    }

def set_neoadjuvant_next_step(facts: Dict[str, Any]) -> dict[str, str]:
    """
    Converts strategy into the concrete 'next_step_neoadjuvant'.
    next_step_neoadjuvant: 'Nachsorge' | 'Erhaltungstherapie'
    """
    plan_strategy, plan_next = get_systematic_therapy_strategy_and_step(facts=facts, type_surgery="laparoscopy")

    print(f"Evidence strategy is {facts.get('strategy_neoadjuvant')}, plan strategy is {plan_strategy}, plan next is {plan_next}")
    return {"next_step_neoadjuvant": plan_next}

def set_adjuvant_next_step(facts: Dict[str, Any]) -> dict[str, str]:
    """
    Converts strategy into the concrete 'next_step_adjuvant'.
    next_step_neoadjuvant: 'Nachsorge' | 'Erhaltungstherapie'
    """
    plan_strategy, plan_next = get_systematic_therapy_strategy_and_step(facts=facts, type_surgery="laparotomy")

    print(
        f"Evidence strategy is {facts.get('strategy_adjuvant')}, plan strategy is {plan_strategy}, plan next is {plan_next}")
    return {"next_step_adjuvant": plan_next}

def set_next_step_therapy(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregates 'next step' of the whole systemic-therapy flow.
    provides: {"next_step_system_therapy": one of {"Nachsorge","Erhaltungstherapie"}}
    needs: ["next_step_neoadjuvant"] or ["next_step_adjuvant"]
    """
    neo = facts.get("next_step_neoadjuvant")
    adj = facts.get("next_step_adjuvant")

    if "Erhaltungstherapie" in [neo, adj]:
        next_step = "Erhaltungstherapie"
    else:
        next_step = "Nachsorge"
    print(f"[evaluator] Next step systemic therapy is {next_step}")
    return {"next_step_system_therapy": next_step}

def set_repeat_debulking_operabel_ass(facts: Dict[str, Any], patient_info: str, llm_json: Callable[[str, dict], dict]) -> \
        dict[str, object]:
    """
    repeated_debulking_possible: 'true' | 'false' # TODO | 'unknown'
    """
    key = "repeated_debulking_possible"
    repeated_debulking_possible = extract_single_fact_llm(llm_json, key, patient_info)[0][key]
    print(f"[evaluator] repeated_debulking_possible: {repeated_debulking_possible}")
    return {"repeated_debulking_possible": repeated_debulking_possible}

def set_maintenance_therapy(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decides concrete maintenance strategy.
    provides: {"plan_strategy_maintenance": 'bevacolap_olap_bevac_nirap' | 'bevacolap_bevac_nirap' | 'bevac_nirap'}
    bevacolap_olap_bevac_nirap: Bevacizumab + Olaparip oder Olaparib oder Bevacizumab oder Niraparib
    bevacolap_bevac_nirap: Bevacizumab + Olaparip oder Bevacizumab oder Niraparib
    bevac_nirap: Bevacizumab oder Niraparib
    """
    brca = facts.get("brca_status")
    hrd = facts.get("hrd_status")

    if brca == "+" and hrd == "+":
        plan_strategy_maintenance = "bevacolap_olap_bevac_nirap"
    elif brca == "-" and hrd == "+":
        plan_strategy_maintenance = "bevacolap_bevac_nirap"
    else: # hrd == "-"
        plan_strategy_maintenance = 'bevac_nirap'
    print(f"[evaluator] plan_strategy_maintenance: {plan_strategy_maintenance}")
    return {"plan_strategy_maintenance": plan_strategy_maintenance}
