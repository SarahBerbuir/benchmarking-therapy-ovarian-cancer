from __future__ import annotations

import pandas as pd

from benchmarking_therapy_ovarian_cancer.prompt_list import judge_prompt


def _prompt(gold: str, cand: str) -> str:
    return judge_prompt.format(gold=gold.strip(), cand=cand.strip())

JUDGE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "label": {"type": "STRING", "enum": ["korrekt", "inkorrekt"]},
        "score": {"type": "NUMBER"},
        "rationale": {"type": "STRING"},
    },
    "required": ["label", "score", "rationale"],
}


def apply_llm_judge_json(
    df: pd.DataFrame,
    llm_json,
    candidate_col: str,
    reference_col: str,
    prefix: str = "vanilla",
    threshold: float | None = None,
) -> pd.DataFrame:
    score_col = f"judge_score_{prefix}"
    label_col = f"judge_label_{prefix}"
    rat_col   = f"judge_rationale_{prefix}"
    if score_col not in df: df[score_col] = 0.0
    if label_col not in df: df[label_col] = ""
    if rat_col   not in df: df[rat_col]   = ""

    for i, row in df.iterrows():
        gold = str(row.get(reference_col, "") or "").strip()
        cand = str(row.get(candidate_col, "") or "").strip()
        if not gold or not cand:
            df.at[i, score_col] = 0.0
            df.at[i, label_col] = "inkorrekt"
            df.at[i, rat_col]   = "leer/fehlend"
            continue

        # TODO
        data = llm_json(_prompt(gold, cand), JUDGE_SCHEMA)

        label = str(data.get("label", "inkorrekt")).strip().lower()
        score = float(data.get("score", 0.0))
        rationale = str(data.get("rationale", "") or "")

        if label not in {"korrekt", "inkorrekt"}:
            label = "inkorrekt"
        score = max(0.0, min(1.0, score))

        if threshold is not None:
            label = "korrekt" if score >= float(threshold) else "inkorrekt"

        df.at[i, score_col] = score
        df.at[i, label_col] = label
        df.at[i, rat_col]   = rationale

    return df
