from __future__ import annotations
from typing import List, Tuple

import numpy as np
from sacrebleu.metrics import BLEU
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


from benchmarking_therapy_ovarian_cancer.config import EvaluationMetrics, LlmStrategy, metric_col
import numpy as np
import torch
from bert_score import BERTScorer

from rouge_score import rouge_scorer

from benchmarking_therapy_ovarian_cancer.evaluation.llm_as_a_judge import apply_llm_judge
from benchmarking_therapy_ovarian_cancer.recommendations import make_llm_fn


def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """
    Calculate the cosine similarity between two text strings.
    :param text1: First text string
    :param text2: Second text string
    :return: Cosine similarity score rounded to 4 decimal places
    """

    if not text1 or not text2:
        return 0.0

    vectorizer = TfidfVectorizer().fit([text1, text2])
    vectors = vectorizer.transform([text1, text2])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score, 4)

def apply_cosine_similarity(
        df: pd.DataFrame,
        cosine_similarity_col,
        candidate_col,
        reference_col) -> pd.DataFrame:
    """
    Apply cosine similarity calculation to the DataFrame.
    :param df: DataFrame containing the recommendations and gold standard
    :param cosine_similarity_col: Name of the column to store cosine similarity results
    :param candidate_col: Column containing the LLM recommendations
    :param reference_col: Column containing the gold standard recommendations
    :return: DataFrame with cosine similarity scores added
    """
    if cosine_similarity_col not in df.columns:
        df[cosine_similarity_col] = 0.0

    for index, row in df.iterrows():
        try:
            reco = str(row[candidate_col])
            gold = str(row[reference_col])
            similarity = calculate_cosine_similarity(reco, gold)
            df.at[index, cosine_similarity_col] = similarity
        except Exception:
            df.at[index, cosine_similarity_col] = -1.0

    return df

def apply_bertscore_fast(
    df: pd.DataFrame,
    out_col: str,
    candidate_col: str,
    reference_col: str,
    model_type: str = "xlm-roberta-base",
    rescale_with_baseline: bool = False,
    batch_size: int = 8,
) -> pd.DataFrame:

    if out_col not in df.columns:
        df[out_col] = 0.0

    cands = df[candidate_col].fillna("").astype(str).tolist()
    refs  = df[reference_col].fillna("").astype(str).tolist()

    # skip empty pairs
    mask = [(bool(c.strip()) and bool(r.strip())) for c, r in zip(cands, refs)]
    if not any(mask):
        return df

    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        torch.set_num_threads(1)
    except Exception:
        pass

    scorer = BERTScorer(
        model_type=model_type,
        rescale_with_baseline=rescale_with_baseline,
        batch_size=batch_size,
        device=device,
        idf=False,
    )

    c_eff = [c for c, m in zip(cands, mask) if m]
    r_eff = [r for r, m in zip(refs,  mask) if m]

    try:
        _, _, F1 = scorer.score(c_eff, r_eff)
        f1_vals = F1.cpu().numpy()
    except Exception:
        f1_vals = np.zeros(len(c_eff), dtype=float)

    out = np.zeros(len(df), dtype=float)
    j = 0
    for i, m in enumerate(mask):
        out[i] = f1_vals[j] if m else 0.0
        if m: j += 1
    df[out_col] = np.round(out, 4)
    return df

_bleu_metric = BLEU(effective_order=True)


def apply_bleu(df, prefix, candidate_col, reference_col):
    sm = SmoothingFunction().method3
    weights = {"1": (1.0, 0, 0, 0), "2": (0.5, 0.5, 0, 0), "4": (0.25, 0.25, 0.25, 0.25)}
    for k, w in weights.items():
        df[f"{prefix}{k}"] = [
            round(sentence_bleu([str(ref).lower().split()],
                                str(hyp).lower().split(),
                                weights=w, smoothing_function=sm), 4)
            if str(hyp).strip() and str(ref).strip() else 0.0
            for hyp, ref in zip(df[candidate_col], df[reference_col])
        ]
    return df


def _rouge(h: str, r: str) -> Tuple[float, float, float]:
    if not (h and h.strip() and r and r.strip()):
        return 0.0, 0.0, 0.0
    try:
        sc = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        s = sc.score(r, h)  # (reference, hypothesis)
        return (float(np.round(s["rouge1"].fmeasure, 4)),
                float(np.round(s["rouge2"].fmeasure, 4)),
                float(np.round(s["rougeL"].fmeasure, 4)))
    except Exception:
        return 0.0, 0.0, 0.0

def apply_rouge(
    df: pd.DataFrame,
    prefix: str,
    candidate_col: str,
    reference_col: str,
) -> pd.DataFrame:
    c1, c2, cL = f"{prefix}1_f", f"{prefix}2_f", f"{prefix}L_f"
    for c in (c1, c2, cL):
        if c not in df.columns: df[c] = 0.0
    for i, row in df.iterrows():
        hyp = str(row.get(candidate_col, "") or ""); ref = str(row.get(reference_col, "") or "")
        r1, r2, rL = _rouge(hyp, ref)
        df.at[i, c1], df.at[i, c2], df.at[i, cL] = r1, r2, rL
    return df



def apply_metrics_for_strategy(
    df: pd.DataFrame,
    strategy: LlmStrategy,
    metrics: List[EvaluationMetrics],
    candidate_col: str,
    reference_col: str,
) -> pd.DataFrame:
    out = df

    for metric in metrics:
        metric_column = metric_col(metric= metric, strategy=strategy)
        if metric == EvaluationMetrics.COSINE:
            out = apply_cosine_similarity(
                df=out,
                cosine_similarity_col=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
            )

        elif metric == EvaluationMetrics.BERT:
            out = apply_bertscore_fast(
                df=out,
                out_col=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
                model_type="xlm-roberta-base",
                rescale_with_baseline=False,
            )

        elif metric == EvaluationMetrics.BLEU:
            out = apply_bleu(
                df=out,
                prefix=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
            )

        elif metric == EvaluationMetrics.ROUGE:
            out = apply_rouge(
                df=out,
                prefix=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
            )

        elif metric == EvaluationMetrics.LLM_AS_A_JUDGE:
            judge_llm = make_llm_fn(strategy)
            out = apply_llm_judge(
                df=out,
                llm_fn=judge_llm,
                candidate_col=candidate_col,
                reference_col=reference_col,
                prefix=metric_column,
            )

        else:
            raise ValueError(f"Unknown metric: {metric}")

    return out