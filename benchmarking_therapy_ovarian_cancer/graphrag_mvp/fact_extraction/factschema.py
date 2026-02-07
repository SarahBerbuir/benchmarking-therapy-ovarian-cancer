from typing import Any

FACT_SCHEMA = {
    "B1_unilokulaer": {
        "role": "input", "type": "bool3",
        "title": "Unilokuläre Zyste",
        "definition": "Unilokuläre (einkammerige) Zyste in der Sonographie.",
        "sections": ["Sonographie"],
        "pos_examples": ["unilokulär"],
        "neg_examples": ["nicht unilokulär", "multilokulär"],
        "producer": ["llm"],
    },
    "B2_solide_lt7mm": {
        "role": "input", "type": "bool3",
        "title": "Solide Komponenten < 7mm",
        "definition": "Solide Komponenten < 7 mm in der Sonographie.",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },
    "B3_schallschatten": {
        "role": "input", "type": "bool3",
        "title": "Schallschatten",
        "definition": "Schallschatten in der Sonographie.",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },
    "B4_glatt_multilok_lt10cm": {
        "role": "input", "type": "bool3",
        "title": "Glatt, multilokulär, <10 cm",
        "definition": "Glatter multilokulärer Tumor. Durchmesser < 10 cm in der Sonographie.",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },
    "B5_keine_doppler_flow": {
        "role": "input", "type": "bool3",
        "title": "Kein Blutfluss",
        "definition": "Kein Blutfluss in der farbkodierten Duplexsonografie (Farbdopplerscore 1).",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },
    "M1_unreg_solid": {
        "role": "input", "type": "bool3",
        "title": "Unregelmäßiger solider Tumor",
        "definition": "Unregelmäßiger solider Tumor in der Sonographie.",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },
    "M2_ascites": {
        "role": "input", "type": "bool3",
        "title": "Aszites",
        "definition": "Aszites in der Sonographie.",
        "sections": ["Sonographie", "Bildgebung"],
        "pos_examples": ["Aszites vorhanden", "moderater Aszites", "free fluid/ascites"],
        "neg_examples": ["kein Aszites", "kein Nachweis von Aszites", "no ascites"],
        "producer": ["llm"],
    },
    "M3_ge4_papillae": {
        "role": "input", "type": "bool3",
        "title": "Mindestens vier papilläre Strukturen",
        "definition": "Mindestens vier papilläre Strukturen in der Sonographie.",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },
    "M4_unreg_multilok_solid_gt10cm": {
        "role": "input", "type": "bool3",
        "title": "Unregelmäßiger multilokulärer solider Tumor ≥ 10 cm",
        "definition": "Unregelmäßiger multilokulärer solider Tumor ≥ 10 cm in der Sonographie",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },
    "M5_hoher_doppler_flow": {
        "role": "input", "type": "bool3",
        "title": "Sehr starker Blutfluss",
        "definition": "Hoher Blutfluss in der farbkodiertem Duplexsonografie (Farbdopplerscore 4).",
        "sections": ["Sonographie"],
        "producer": ["llm"],
    },

    # --- Evidence ---
    "ev_sonography_present": {
        "role": "evidence", "type": "bool2",
        "title": "Sonographie in Akte vorhanden",
        "definition": "Hinweise, dass Sonographie durchgeführt wurde. Nicht verwechseln mit Werten von Sonografie!",
        "sections": ["Sonographie", "Befunde"],
        "producer": ["llm"],
    },
    "ev_ct_present": {
        "role": "evidence", "type": "bool2",
        "title": "CT-Befund in Akte vorhanden",
        "definition": "Hinweise, dass CT Thorax/Abdomen durchgeführt wurde und gemacht wurde. Nicht verwechweln mit Werten von Sonografie! Meistens steht auch \"CT\" im Text.",
        "sections": ["Bildgebung", "CT", "Befunde"],
        "producer": ["llm"],
    },
    "ev_followup_present": {
        "role": "evidence", "type": "bool2",
        "title": "Verlaufskontrolle vorhanden",
        "definition": "Hinweise, dass eine Verlaufskontrolle/Follow-up dokumentiert ist (z. B. Kontrolltermin, Kontrollbefund).",
        "sections": [],
        "producer": ["llm"],
    },
    "ev_cystectomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Zystenausschälung durchgeführt",
        "definition": "Hinweise, dass eine Zystenausschälung bereits durchgeführt wurde.",
        "sections": [],
        "producer": ["llm"],
    },
    "ev_adnexectomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Adnektomie durchgeführt",
        "definition": "Hinweise, dass eine Adnektomie bereits durchgeführt wurde.",
        "sections": [],
        "producer": ["llm"],
    },
    # --- Evaluator-Output  ---
    "iota_res": {
        "role": "output", "type": "enum",
        "allowed": ["benigne_wahrscheinlich","maligne_wahrscheinlich","nicht_klassifizierbar","unknown"],
        "producer": ["iota_simple_rules"],
    },
    "cyst_bd": {
        "role": "output", "type": "enum",
        "allowed": ["BD1","BD2","BD3","BD4", "unknown"],
        "producer": ["bd_classification"],
    },
    "op_plan": {
        "role": "output", "type": "enum",
        "allowed": ["no_op","Zystenausschälung","Adnektomie","unknown"],
        "producer": ["get_op_plan"],
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
