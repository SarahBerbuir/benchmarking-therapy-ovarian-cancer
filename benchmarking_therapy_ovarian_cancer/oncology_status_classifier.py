#TODO in more files & less details -> let LLM decide without guidance

from __future__ import annotations
import os
from typing import Any
import pandas as pd

from benchmarking_therapy_ovarian_cancer import config
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix
)
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Dict

from benchmarking_therapy_ovarian_cancer.llm_vertex import init_vertexai_llm, get_json_llm_fn

SYSTEM_MSG = (
    "Du bist Fachärzt:in für Gynäkologische Onkologie in einem interdisziplinären Tumorboard. "
    "Deine Aufgabe ist eine BINÄRE Einstufung für die Zielentität 'Ovarialkarzinom': "
    "'Diagnose' ODER 'Verdacht'. Arbeite streng evidenzbasiert (Pathologie/Histologie > klinische Impression > Bildgebung). "
    "Antworte ausschließlich als JSON."
)


RULES = (
    "Evidenz-Priorität (höchste Regel zuerst):\n"
    "1) **Diagnose** bei gesichertem Befund in Text ODER Pathologie/Histologie, z. B.:\n"
    "   • explizite Nennung 'Ovarialkarzinom' ODER typische Ovar-Histologien (HGSC/LGSC, endometrioid, klarzellig, muzinös),\n"
    "   • **Ovarialer Borderline-Tumor (z. B. muzinöser/seröser Borderline-Tumor) gilt als gesicherte Diagnose**,\n"
    "   • Formulierungen wie 'Biopsie bestätigt' / 'histologisch gesichert/vereinbar mit', FIGO-Stadium, \n"
    "   •  organisatorische Marker wie 'Zweitmeinung', 'postoperative Vorstellung'\n"
    "2) **Verdacht** bei Unsicherheit/Vorläufigkeit: 'Verdacht auf', 'V. a.', 'suspekt', 'Hinweis auf', 'fraglich', 'am ehesten'.\n"
    "3) Wenn in der Histologie Unsicherheitsbegriffe ('am ehesten', 'fraglich') stehen **ohne** harte Bestätigung aus (1), dann 'Verdacht'.\n"
    "4) Bildgebung allein (CT/MRT/US/PET-CT) genügt nicht für 'Diagnose' – ohne Bestätigung → 'Verdacht'.\n"
    "5) Entscheide strikt BINÄR. Bei unzureichender Evidenz konservativ 'Verdacht'. Paraphrasen/Synonyme erkennen."
)
USER_TEMPLATE = (
    "Bestimme **nur** für 'Ovarialkarzinom' den Status. Gib **ausschließlich** folgendes JSON zurück (keine weiteren Worte):\n"
    "{{\"label\": \"Diagnose|Verdacht\", \"rationale\": \"kurze Begründung\", \"evidence_spans\": [\"wörtliche Textausschnitte\"]}}"
    "\n\nPatientin (alle Spalten als 'Name: Wert', semikolon-getrennt):\n{patient_block}\n"
)


ONCO_SCHEMA: Dict = {
    "type": "OBJECT",
    "properties": {
        "label": {"type": "STRING", "enum": ["Diagnose", "Verdacht"]},
        "rationale": {"type": "STRING"},
        "evidence_spans": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["label", "rationale", "evidence_spans"],
}

def make_patient_block(row: pd.Series) -> str:
    """ Concatenate patient blocks if not in excluded columns"""
    exclude_cols = {
        "Original Tumorboard-Empfehlung",
        "Referenz Goldstandard",
        "Kommentar",
    }
    exclude_lower = {c.lower() for c in exclude_cols}


    name_value_pairs = []
    for column_name, value in row.items():
        if column_name.lower() in exclude_lower:
            continue
        if pd.isna(value):
            continue
        value_str = str(value).strip()
        if not value_str:
            continue
        name_value_pairs.append(f"{column_name}: {value_str}")
    return " ; ".join(name_value_pairs)

def generate_oncology_prompt(row: pd.Series) -> str:
    patient_block = make_patient_block(row)
    prompt = f"{SYSTEM_MSG}\n\n{RULES}\n\n" + USER_TEMPLATE.format(patient_block=patient_block)
    return prompt

def classify_oncology_status(df):
    df_out, sys_msg, rules_text, user_tmpl = evaluate_oncology_status(df)
    # TODO
    # metrics = evaluate_oncology_binary(df_out)
    # print(f"Metrics classification oncology status: {metrics}")
    # save_run_json(
    #     metrics=metrics,
    #     system_msg=sys_msg,
    #     rules_text=rules_text,
    #     user_template=user_tmpl,
    #     model_name=config.LLM_MODEL_NAME,
    #     n_cases=len(df_out),
    #     out_path="runs/oncology_runs.json",
    # )
    return df_out

def evaluate_oncology_status(
    df: pd.DataFrame
):
    model = init_vertexai_llm()

    llm_json = get_json_llm_fn(model)
    labels, rationales, spans_list = [], [], []

    for _, row in df.iterrows():
        prompt = generate_oncology_prompt(row)
        data = llm_json(prompt, ONCO_SCHEMA)

        labels.append(data.get("label", "Verdacht"))
        rationales.append(data.get("rationale", ""))
        spans = data.get("evidence_spans", [])
        spans_list.append(spans if isinstance(spans, list) else [str(spans)])
    out_df = df.copy()
    out_df["oncology_status"] = labels
    out_df["oncology_rationale"] = rationales
    out_df["oncology_evidence_spans"] = [" ; ".join(s) if s else "" for s in spans_list]

    return out_df, SYSTEM_MSG, RULES, USER_TEMPLATE


def evaluate_oncology_binary(
    df: pd.DataFrame,
    y_true_col: str = "Referenz Goldstandard",
    y_pred_col: str = "oncology_status",
    positive_label: str = "Diagnose",
) -> Dict[str, Any]:
    y_true = df[y_true_col].astype(str).str.strip().str.lower()
    y_pred = df[y_pred_col].astype(str).str.strip().str.lower()
    pos = positive_label.strip().lower()
    neg = "verdacht" if pos == "diagnose" else "diagnose"

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, pos_label=pos, average="binary", zero_division=0)
    rec  = recall_score(y_true, y_pred,  pos_label=pos, average="binary", zero_division=0)
    f1   = f1_score(y_true, y_pred,      pos_label=pos, average="binary", zero_division=0)

    cm = confusion_matrix(y_true, y_pred, labels=[pos, neg])
    tp, fn = int(cm[0,0]), int(cm[0,1])
    fp, tn = int(cm[1,0]), int(cm[1,1])

    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "confusion_matrix": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
    }


def save_run_json(
    metrics: dict,
    system_msg: str,
    rules_text: str,
    user_template: str,
    model_name: str,
    n_cases: int,
    out_path: str | Path = "runs/oncology_runs.json",
) -> Path:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        with out_path.open("r", encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = {}

    log[ts] = {
        "timestamp_utc": ts,
        "model": model_name,
        "n_cases": n_cases,
        "system_msg": system_msg,
        "rules": rules_text,
        "user_template": user_template,
        "metrics": metrics,
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    return out_path

