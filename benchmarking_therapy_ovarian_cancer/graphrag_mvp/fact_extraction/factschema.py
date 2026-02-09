from typing import Any, Sequence


FIGO_I = ["I", "IA", "IB", "IC1", "IC2", "IC3"]
FIGO_II = ["II", "IIA", "IIB", "IIC"]
FIGO_III = ["III", "IIIA", "IIIA1", "IIIA2", "IIIB", "IIIC"]
FIGO_IV = ["IV", "IVA", "IVB"]
FIGO_STAGES: Sequence[str] = FIGO_I + FIGO_II + FIGO_III + FIGO_IV

FACT_SCHEMA = {
    "B1_unilokulaer": {
        "role": "input", "type": "bool3",
        "title": "Unilokuläre Zyste",
        "definition": "Unilokuläre (einkammerige) Zyste in der Sonographie.",
        "pos_examples": ["unilokulär"],
        "neg_examples": ["nicht unilokulär", "multilokulär"],
        "producer": ["llm"],
    },
    "B2_solide_lt7mm": {
        "role": "input", "type": "bool3",
        "title": "Solide Komponenten < 7mm",
        "definition": "Solide Komponenten < 7 mm in der Sonographie.",
        "producer": ["llm"],
    },
    "B3_schallschatten": {
        "role": "input", "type": "bool3",
        "title": "Schallschatten",
        "definition": "Schallschatten in der Sonographie.",
        "producer": ["llm"],
    },
    "B4_glatt_multilok_lt10cm": {
        "role": "input", "type": "bool3",
        "title": "Glatt, multilokulär, <10 cm",
        "definition": "Glatter multilokulärer Tumor. Durchmesser < 10 cm in der Sonographie.",
        "producer": ["llm"],
    },
    "B5_keine_doppler_flow": {
        "role": "input", "type": "bool3",
        "title": "Kein Blutfluss",
        "definition": "Kein Blutfluss in der farbkodierten Duplexsonografie (Farbdopplerscore 1).",
        "producer": ["llm"],
    },
    "M1_unreg_solid": {
        "role": "input", "type": "bool3",
        "title": "Unregelmäßiger solider Tumor",
        "definition": "Unregelmäßiger solider Tumor in der Sonographie.",
        "producer": ["llm"],
    },
    "M2_ascites": {
        "role": "input", "type": "bool3",
        "title": "Aszites",
        "definition": "Aszites in der Sonographie.",
        "pos_examples": ["Aszites vorhanden", "moderater Aszites", "free fluid/ascites"],
        "neg_examples": ["kein Aszites", "kein Nachweis von Aszites", "no ascites"],
        "producer": ["llm"],
    },
    "M3_ge4_papillae": {
        "role": "input", "type": "bool3",
        "title": "Mindestens vier papilläre Strukturen",
        "definition": "Mindestens vier papilläre Strukturen in der Sonographie.",
        "producer": ["llm"],
    },
    "M4_unreg_multilok_solid_gt10cm": {
        "role": "input", "type": "bool3",
        "title": "Unregelmäßiger multilokulärer solider Tumor ≥ 10 cm",
        "definition": "Unregelmäßiger multilokulärer solider Tumor ≥ 10 cm in der Sonographie",
        "producer": ["llm"],
    },
    "M5_hoher_doppler_flow": {
        "role": "input", "type": "bool3",
        "title": "Sehr starker Blutfluss",
        "definition": "Hoher Blutfluss in der farbkodiertem Duplexsonografie (Farbdopplerscore 4).",
        "producer": ["llm"],
    },
    "praemenopausal": {
        "role": "input",
        "type": "bool2",
        "title": "Prämenopausal",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "symptoms_present": {
        "role": "input", "type": "bool2",
        "title": "Symptome vorhanden",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "growth": {
        "role": "input", "type": "bool2",
        "title": "Größenzunahme",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "persistence": {
        "role": "input", "type": "bool2",
        "title": "Persistenz",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "complex_multiloculaer": {
        "role": "input", "type": "bool2",
        "title": "Komplex multilokulär",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "psychic_unsure": {
        "role": "input", "type": "bool2",
        "title": "Psychische Unsicherheit",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "ca125_u_ml": {
        "role": "input", "type": "number",
        "title": "CA125 (U/ml)",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "size_cm": {
        "role": "input",
        "type": "number",
        "title": "Größe (cm)",
        "definition": "TBD",
        "producer": ["llm"],
    },
    "figo_clinical": {
        "role": "input", "type": "enum",
        "title": "FIGO clinical",
        "allowed": FIGO_STAGES,
        # TODO
        "definition": "TBD. ",
        "producer": ["llm"],
    },
    "figo_path_laparotomy": {
        "role": "input", "type": "enum",
        "title": "FIGO pathologisch (Laparotomie)",
        "definition": "TBD",
        "allowed": FIGO_STAGES,
        "producer": ["llm"],
    },
    "figo_path_laparoscopy": {
        "role": "input", "type": "enum",
        "title": "FIGO pathologisch (Laparoskopie)",
        "definition": "TBD",
        "allowed": FIGO_STAGES,
        "producer": ["llm"],
    },
    "grade_laparotomy": {
        "role": "input",
        "type": "enum",
        "title": "Grading (Laparotomie)",
        "definition": "TBD",
        "allowed": ["low", "high"],
        "producer": ["llm"],
    },
    "histology_laparotomy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Laparotomie)",
        "definition": "TBD",
        "allowed": ["benigne", "maligne", "TBD"],
        "producer": ["llm"],
    },
    "grade_laparoscopy": {
        "role": "input", "type": "enum",
        "title": "Grading (Laparoskopie)",
        "definition": "TBD",
        "allowed": ["low", "high"],
        "producer": ["llm"],
    },
    "histology_laparoscopy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Laparoskopie)",
        "definition": "TBD",
        "allowed": ["benigne", "maligne", "TBD"],
        "producer": ["llm"],
    },
    "histology_cystectomy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Zystektomie)",
        "definition": "TBD",
        "allowed": ["benigne", "maligne", "TBD"],
        "producer": ["llm"],
    },
    "histology_adnexectomy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Adnektomie)",
        "definition": "TBD",
        "allowed": ["benigne", "maligne", "TBD"],
        "producer": ["llm"],
    },
    "gBRCA1/2": {
        "role": "input", "type": "enum",
        "title": "gBRCA1/2",
        "definition": "TBD",
        "allowed": ["+", "-"],
        "producer": ["llm"],
    },
    "sBRCA1/2": {
        "role": "input", "type": "enum",
        "title": "sBRCA1/2",
        "definition": "TBD",
        "allowed": ["+", "-"],
        "producer": ["llm"],
    },
    "sHRD": {
        "role": "input", "type": "enum",
        "title": "sHRD",
        "definition": "TBD",
        "allowed": ["+", "-"],
        "producer": ["llm"],
    },
    "strategy_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Strategie (Adjuvant)",
        "definition": "TBD",
        "allowed": [
            "op_only",
            "carboplatin_optional_6x",
            "carboplatin_6x",
            "carboplatin_or_paclitaxel_6x",
            "carboplatin_or_paclitaxel_bevacizumab_6x",
        ],
        "producer": ["llm"],  # Step-Output
    },
    "strategy_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Strategie (Neoadjuvant)",
        "definition": "TBD",
        "allowed": [
            "op_only",
            "carboplatin_optional_3x",
            "carboplatin_3x",
            "carboplatin_or_paclitaxel_3x",
            "carboplatin_or_paclitaxel_bevacizumab_3x",
        ],
        "producer": ["llm"],  # Step-Output
    },
    "strategy_maintenance": {
        "role": "output", "type": "enum",
        "title": "Strategie (Erhaltung)",
        "definition": "TBD",
        "allowed": [
            "bevacolap_olap_bevac_nirap",
            "bevacolap_bevac_nirap",
            "bevac_nirap"
        ],
        "producer": ["llm"],
    },


    # --- Evidence ---
    "ev_sonography_present": {
        "role": "evidence", "type": "bool2",
        "title": "Sonographie in Akte vorhanden",
        "definition": "Hinweise, dass Sonographie durchgeführt wurde. Nicht verwechseln mit Werten von Sonografie!",
        "producer": ["llm"],
    },
    "ev_ct_present": {
        "role": "evidence", "type": "bool2",
        "title": "CT-Befund in Akte vorhanden",
        "definition": "Hinweise, dass CT Thorax/Abdomen durchgeführt wurde und gemacht wurde. Nicht verwechweln mit Werten von Sonografie! Meistens steht auch \"CT\" im Text.",
        "producer": ["llm"],
    },
    "ev_cystectomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Zystenausschälung durchgeführt",
        "definition": "Hinweise, dass eine Zystenausschälung bereits durchgeführt wurde und vermutlich benign oder maligne ist.",
        "producer": ["llm"],
    },
    "ev_adnexectomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Adnektomie durchgeführt",
        "definition": "Hinweise, dass eine Adnektomie bereits durchgeführt wurde.",
        "producer": ["llm"],
    },
    "ev_laparotomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Laparotomie durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_laparoscopy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Laparoskopie durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_genetic_counseling_done": {
        "role": "evidence", "type": "bool2",
        "title": "Humangenetische Beratung durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_hrd_test_done": {
        "role": "evidence", "type": "bool2",
        "title": "HRD-Test durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_neoadjuvant_therapy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Neoadjuvante Therapie durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_adjuvant_therapy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Adjuvante Therapie durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_interim_restaging_3_done": {
        "role": "evidence", "type": "bool2",
        "title": "Interim Restaging (Zyklus 3) durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_chemo_protocol_switch_completion_done": {
        "role": "evidence", "type": "bool2",
        "title": "Wechsel/Komp.-Chemotherapie durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    "ev_optimal_debulking_completion_done": {
        "role": "evidence", "type": "bool2",
        "title": "Optimales Debulking + Chemo abgeschlossen", "definition": "TBD", "producer": ["llm"],
    },
    "ev_maintenance_therapy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Erhaltungstherapie durchgeführt", "definition": "TBD", "producer": ["llm"],
    },
    # --- Evaluator-Output  ---
    "iota_res": {
        "role": "output", "type": "enum",
        "allowed": ["benigne_wahrscheinlich","maligne_wahrscheinlich","nicht_klassifizierbar"],
        "producer": ["iota_simple_rules"],
    },
    "cyst_bd": {
        "role": "output", "type": "enum",
        "allowed": ["BD1","BD2","BD3","BD4", "unknown"], # TODO
        "producer": ["bd_classification"],
    },
    "op_plan": {
        "role": "output", "type": "enum",
        "allowed": ["no_op","Zystenausschälung","Adnektomie","unknown"], # TODO unknown ?
        "producer": ["set_op_plan"],
    },
    "figo_bucket": {
        "role": "output", "type": "enum",
        "allowed": ["early", "advanced"],
        "producer": ["set_figo_bucket"],
    },
    "debulking_possible": {
        "role": "output", "type": "bool3",
        "producer": ["set_debulking_possible"],
    },
    "plan_strategy_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Strategie (Adjuvant)",
        "definition": "TBD",
        "allowed": [
            "op_only",
            "carboplatin_optional_6x",
            "carboplatin_6x",
            "carboplatin_or_paclitaxel_6x",
            "carboplatin_or_paclitaxel_bevacizumab_6x",
        ],
        "producer": ["set_planning_adjuvant_therapy"],
    },
    "plan_next_step_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Next Step (Adjuvant)",
        "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_planning_adjuvant_therapy"],
    },
    "next_step_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Next Step (Adjuvant)", "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_adjuvant_next_step"],
    },
    "plan_strategy_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Strategie (Neoadjuvant)",
        "definition": "TBD",
        "allowed": [
            "op_only",
            "carboplatin_optional_3x",
            "carboplatin_3x",
            "carboplatin_or_paclitaxel_3x",
            "carboplatin_or_paclitaxel_bevacizumab_3x",
        ],
        "producer": ["set_planning_neoadjuvant_therapy"],
    },
    "plan_next_step_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Next Step (Neoadjuvant)",
        "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_planning_neoadjuvant_therapy"],
    },
    "next_step_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Next Step (Neoadjuvant)", "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_neoadjuvant_next_step"],
    },
    "next_step_system_therapy": {
        "role": "output", "type": "enum",
        "title": "Next Step (Systemtherapie)",
        "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_next_step_therapy"],
    },
    "plan_strategy_maintenance": {
        "role": "output", "type": "enum",
        "title": "Plan Strategie (Erhaltung)", "definition": "TBD",
        "allowed": [
            "bevacolap_olap_bevac_nirap",
            "bevacolap_bevac_nirap",
            "bevac_nirap"
        ],
        "producer": ["set_maintenance_therapy"],
    },
    "hrd_status": {
        "role": "output", "type": "enum",
        "title": "HRD Status", "definition": "TBD",
        "allowed": ["+", "-"], "producer": ["set_hrd_brca_status"],
    },
    "brca_status": {
        "role": "output", "type": "enum",
        "title": "BRCA Status", "definition": "TBD",
        "allowed": ["+", "-"], "producer": ["set_hrd_brca_status"],
    },
}


def schema_for_bool2(key: str) -> dict:
    return {
        "type": "OBJECT",
        "properties": { key: { "type": "STRING", "enum": ["true","false"] } },
        "required": [key],
    }

def schema_for_bool3(key: str) -> dict:
    return {
        "type": "OBJECT",
        "properties": {
            key: {
                "type": "STRING",
                "enum": ["true", "false", "unknown"]
            }
        },
        "required": [key],
    }

def schema_for_enum(key: str, allowed: list[str]) -> dict:
    return {
        "type": "OBJECT",
        "properties": { key: { "type": "STRING", "enum": allowed } },
        "required": [key],
    }

def schema_for_number(key: str) -> dict:
    return {
        "type": "OBJECT",
        "properties": { key: { "type": "NUMBER" } },
        "required": [key],
    }

def schema_for_key(key: str) -> dict:
    spec = FACT_SCHEMA[key]
    t = spec["type"]
    if t == "bool2":
        return schema_for_bool2(key)
    if t == "bool3":
        return schema_for_bool3(key)
    if t == "enum":
        return schema_for_enum(key, spec.get("allowed", []))
    if t == "number":
        return schema_for_number(key)
    return {"type":"OBJECT","properties":{key:{"type":"STRING"}}, "required":[key]}

_TRUE  = {"true","wahr","ja","yes","1"}
_FALSE = {"false","falsch","nein","no","0"}
_UNK   = {"unknown","unk","na","n/a",""}


def validate_and_normalize(key: str, value: Any):
    if "route" in key.lower():
        spec = None
        type_value = "bool2"
    else:
        spec = FACT_SCHEMA.get(key)
        if not spec:
            raise KeyError(f"Unknown FactKey: {key}")
        type_value = spec["type"]
    s = str(value).strip().lower() if value is not None else ""

    if type_value == "bool2":
        if s in _TRUE or value is True:  return True
        if s in _FALSE or value is False: return False
        return False

    if type_value == "bool3":
        if s in _TRUE or value is True:   return True
        if s in _FALSE or value is False: return False
        if s in _UNK:                     return "unknown"
        return "unknown"

    if type_value == "enum":
        allowed = set(spec.get("allowed", []))
        return value if isinstance(value, str) and value in allowed else "unknown"

    if type_value == "number":
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    return value
