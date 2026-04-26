from __future__ import annotations

import re
from typing import List, Tuple, Optional, Dict, Any

import numpy as np
import pandas as pd
import torch

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import BERTScorer

from benchmarking_therapy_ovarian_cancer.config import (
    EvaluationMetrics,
    LlmStrategy,
    metric_col,
)


_ROUGE_SCORER: Optional[rouge_scorer.RougeScorer] = None
_BERTSCORER_CACHE: Dict[Tuple[str, bool, int, str], BERTScorer] = {}
_EMBEDDER_CACHE: Dict[Tuple[str, str], Any] = {}


# ---------------------------------------------------------------------
# Text normalization / tokenization
# ---------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize text consistently across all metrics.
    Keeps wording intact but removes formatting noise.
    """
    text = str(text or "")
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([,;:.])\s*", r"\1 ", text)
    return text.strip()


def simple_tokenize(text: str) -> List[str]:
    """
    Lightweight tokenizer for BLEU.
    Separates punctuation more robustly than plain split().
    """
    text = normalize_text(text).lower()
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def _to_text_list(s: pd.Series) -> List[str]:
    return [normalize_text(x) for x in s.fillna("").astype(str).tolist()]


# ---------------------------------------------------------------------
# Cached scorers / embedders
# ---------------------------------------------------------------------

def _get_rouge_scorer() -> rouge_scorer.RougeScorer:
    global _ROUGE_SCORER
    if _ROUGE_SCORER is None:
        _ROUGE_SCORER = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"],
            use_stemmer=False,
        )
    return _ROUGE_SCORER


def _get_bertscorer(
    model_type: str,
    rescale: bool,
    batch_size: int,
    device: str,
) -> BERTScorer:
    key = (model_type, rescale, batch_size, device)
    if key not in _BERTSCORER_CACHE:
        _BERTSCORER_CACHE[key] = BERTScorer(
            model_type=model_type,
            rescale_with_baseline=rescale,
            batch_size=batch_size,
            device=device,
            idf=False,
        )
    return _BERTSCORER_CACHE[key]


def _get_embedder(model_name: str, backend: str = "auto") -> tuple[str, Any]:
    """
    Supports:
    - FlagEmbedding backend for BAAI/bge-m3
    - sentence-transformers backend for other embedding models
    """
    if backend == "auto":
        if model_name.lower().startswith("baai/bge-m3"):
            backend = "flag"
        else:
            backend = "st"

    key = (backend, model_name)
    if key in _EMBEDDER_CACHE:
        return backend, _EMBEDDER_CACHE[key]

    if backend == "flag":
        try:
            from FlagEmbedding import BGEM3FlagModel
        except Exception as e:
            raise ImportError(
                "For bge-m3 via FlagEmbedding please install: pip install FlagEmbedding"
            ) from e

        model = BGEM3FlagModel(model_name)
        _EMBEDDER_CACHE[key] = model
        return backend, model

    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise ImportError(
            "For embeddings via sentence-transformers please install: pip install sentence-transformers"
        ) from e

    model = SentenceTransformer(model_name)
    _EMBEDDER_CACHE[key] = model
    return backend, model


# ---------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------

def _embed_texts(
    texts: List[str],
    model_name: str = "BAAI/bge-m3",
    backend: str = "auto",
    batch_size: int = 64,
    normalize_embeddings: bool = False,
    use_progress: bool = False,
) -> np.ndarray:
    """
    Returns dense embeddings for a list of texts.
    """
    cleaned = [normalize_text(t) for t in texts]
    cleaned = [t for t in cleaned if t.strip()]

    if not cleaned:
        return np.empty((0, 1), dtype=float)

    backend_used, model = _get_embedder(model_name, backend=backend)

    if "e5" in model_name.lower():
        cleaned = [("query: " + t) for t in cleaned]

    if backend_used == "flag":
        try:
            output = model.encode(
                cleaned,
                return_dense=True,
                batch_size=batch_size,
            )
        except TypeError:
            output = model.encode(
                cleaned,
                return_dense=True,
            )

        emb = np.asarray(output["dense_vecs"], dtype=float)

        if normalize_embeddings:
            emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)

        return emb

    emb = model.encode(
        cleaned,
        batch_size=batch_size,
        normalize_embeddings=normalize_embeddings,
        show_progress_bar=use_progress,
    )
    return np.asarray(emb, dtype=float)


# ---------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------

def apply_embedding_cosine(
    df: pd.DataFrame,
    out_col: str,
    candidate_col: str,
    reference_col: str,
    model_name: str = "BAAI/bge-m3",
    backend: str = "auto",
    batch_size: int = 64,
    use_progress: bool = False,
) -> pd.DataFrame:
    """
    Embedding-based cosine similarity between candidate and reference.
    This is the cosine metric you described in the thesis.
    """
    if out_col not in df.columns:
        df[out_col] = 0.0

    cands = _to_text_list(df[candidate_col])
    refs = _to_text_list(df[reference_col])

    mask = np.array(
        [bool(c.strip()) and bool(r.strip()) for c, r in zip(cands, refs)],
        dtype=bool,
    )

    out = np.zeros(len(df), dtype=float)

    if not mask.any():
        df[out_col] = 0.0
        return df

    c_eff = [c for c, m in zip(cands, mask) if m]
    r_eff = [r for r, m in zip(refs, mask) if m]

    emb_c = _embed_texts(
        c_eff,
        model_name=model_name,
        backend=backend,
        batch_size=batch_size,
        normalize_embeddings=True,
        use_progress=use_progress,
    )
    emb_r = _embed_texts(
        r_eff,
        model_name=model_name,
        backend=backend,
        batch_size=batch_size,
        normalize_embeddings=True,
        use_progress=use_progress,
    )

    if emb_c.shape[0] != emb_r.shape[0]:
        raise RuntimeError(
            f"Embedding shape mismatch: candidates={emb_c.shape}, references={emb_r.shape}"
        )

    sims = (emb_c * emb_r).sum(axis=1)
    out[mask] = np.nan_to_num(sims, nan=0.0, posinf=0.0, neginf=0.0)

    df[out_col] = np.round(out, 4)
    return df


def apply_bertscore(
    df: pd.DataFrame,
    out_col: str,
    candidate_col: str,
    reference_col: str,
    model_type: str = "xlm-roberta-base",
    rescale_with_baseline: bool = False,
    batch_size: int = 8,
) -> pd.DataFrame:
    """
    Computes BERTScore F1 for each row.
    """
    if out_col not in df.columns:
        df[out_col] = 0.0

    cands = _to_text_list(df[candidate_col])
    refs = _to_text_list(df[reference_col])

    mask = [bool(c.strip()) and bool(r.strip()) for c, r in zip(cands, refs)]
    if not any(mask):
        df[out_col] = 0.0
        return df

    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        torch.set_num_threads(1)
    except Exception:
        pass

    scorer = _get_bertscorer(
        model_type=model_type,
        rescale=rescale_with_baseline,
        batch_size=batch_size,
        device=device,
    )

    c_eff = [c for c, m in zip(cands, mask) if m]
    r_eff = [r for r, m in zip(refs, mask) if m]

    try:
        _, _, f1 = scorer.score(c_eff, r_eff)
        f1_vals = f1.detach().cpu().numpy()
    except Exception as e:
        raise RuntimeError(f"BERTScore failed: {e}") from e

    out = np.zeros(len(df), dtype=float)
    j = 0
    for i, m in enumerate(mask):
        if m:
            out[i] = float(f1_vals[j])
            j += 1
        else:
            out[i] = 0.0

    df[out_col] = np.round(out, 4)
    return df


def apply_bleu(
    df: pd.DataFrame,
    prefix: str,
    candidate_col: str,
    reference_col: str,
) -> pd.DataFrame:
    """
    Computes BLEU-1, BLEU-2, BLEU-4.
    """
    sm = SmoothingFunction().method3
    weights = {
        "1": (1.0, 0.0, 0.0, 0.0),
        "2": (0.5, 0.5, 0.0, 0.0),
        "4": (0.25, 0.25, 0.25, 0.25),
    }

    cands = _to_text_list(df[candidate_col])
    refs = _to_text_list(df[reference_col])

    c_tok = [simple_tokenize(c) for c in cands]
    r_tok = [simple_tokenize(r) for r in refs]

    for k, w in weights.items():
        col = f"{prefix}{k}"
        vals = []
        for ct, rt in zip(c_tok, r_tok):
            if ct and rt:
                score = sentence_bleu([rt], ct, weights=w, smoothing_function=sm)
                vals.append(round(score, 4))
            else:
                vals.append(0.0)
        df[col] = vals

    return df


def apply_rouge(
    df: pd.DataFrame,
    prefix: str,
    candidate_col: str,
    reference_col: str,
) -> pd.DataFrame:
    """
    Computes ROUGE-1 F1, ROUGE-2 F1, ROUGE-L F1.
    """
    c1, c2, cL = f"{prefix}1_f", f"{prefix}2_f", f"{prefix}L_f"
    for col in (c1, c2, cL):
        if col not in df.columns:
            df[col] = 0.0

    scorer = _get_rouge_scorer()

    cands = _to_text_list(df[candidate_col])
    refs = _to_text_list(df[reference_col])

    r1 = np.zeros(len(df), dtype=float)
    r2 = np.zeros(len(df), dtype=float)
    rL = np.zeros(len(df), dtype=float)

    for i, (cand, ref) in enumerate(zip(cands, refs)):
        if not (cand.strip() and ref.strip()):
            continue

        try:
            scores = scorer.score(ref, cand)  # reference first, candidate second
        except Exception as e:
            raise RuntimeError(f"ROUGE failed at row {i}: {e}") from e

        r1[i] = scores["rouge1"].fmeasure
        r2[i] = scores["rouge2"].fmeasure
        rL[i] = scores["rougeL"].fmeasure

    df[c1] = np.round(r1, 4)
    df[c2] = np.round(r2, 4)
    df[cL] = np.round(rL, 4)
    return df


# ---------------------------------------------------------------------
# Main metric pipeline
# ---------------------------------------------------------------------

def apply_metrics_for_strategy(
    df: pd.DataFrame,
    strategy: LlmStrategy,
    metrics: List[EvaluationMetrics],
    candidate_col: str,
    reference_col: str,
    embedding_model_name: str = "BAAI/bge-m3",
    embedding_backend: str = "auto",
    bertscore_model_type: str = "xlm-roberta-base",
    bertscore_batch_size: int = 8,
    embedding_batch_size: int = 64,
) -> pd.DataFrame:
    """
    Apply the selected quantitative metrics to one strategy output column.
    Supported metrics in this cleaned version:
    - BLEU
    - ROUGE
    - BERT
    - EMBED_COSINE
    """
    out = df.copy()

    for metric in metrics:
        print(f"Evaluating {metric.name}")
        metric_column = metric_col(metric=metric, strategy=strategy)

        if metric == EvaluationMetrics.BLEU:
            out = apply_bleu(
                out,
                prefix=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
            )

        elif metric == EvaluationMetrics.ROUGE:
            out = apply_rouge(
                out,
                prefix=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
            )

        elif metric == EvaluationMetrics.BERT:
            out = apply_bertscore(
                out,
                out_col=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
                model_type=bertscore_model_type,
                batch_size=bertscore_batch_size,
            )

        elif metric == EvaluationMetrics.EMBED_COSINE:
            out = apply_embedding_cosine(
                out,
                out_col=metric_column,
                candidate_col=candidate_col,
                reference_col=reference_col,
                model_name=embedding_model_name,
                backend=embedding_backend,
                batch_size=embedding_batch_size,
            )

        else:
            raise ValueError(
                f"Unsupported metric in this quantitative evaluation module: {metric}"
            )

    return out


# ---------------------------------------------------------------------
# Summary statistics: median / IQR
# ---------------------------------------------------------------------

def summarize_metric_columns(
    df: pd.DataFrame,
    metric_cols: List[str],
) -> pd.DataFrame:
    """
    Summarizes metric columns using:
    - median
    - Q1
    - Q3
    - IQR
    - n
    """
    rows = []

    for col in metric_cols:
        vals = pd.to_numeric(df[col], errors="coerce").dropna()

        if vals.empty:
            rows.append(
                {
                    "metric": col,
                    "median": None,
                    "q1": None,
                    "q3": None,
                    "iqr": None,
                    "n": 0,
                }
            )
            continue

        q1 = vals.quantile(0.25)
        q3 = vals.quantile(0.75)

        rows.append(
            {
                "metric": col,
                "median": round(float(vals.median()), 4),
                "q1": round(float(q1), 4),
                "q3": round(float(q3), 4),
                "iqr": round(float(q3 - q1), 4),
                "n": int(vals.shape[0]),
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Centroid similarity
# ---------------------------------------------------------------------

def compute_centroid(
    texts: List[str],
    model_name: str = "BAAI/bge-m3",
    backend: str = "auto",
    batch_size: int = 64,
) -> np.ndarray:
    """
    Computes one normalized centroid vector for a list of texts.
    """
    emb = _embed_texts(
        texts,
        model_name=model_name,
        backend=backend,
        batch_size=batch_size,
        normalize_embeddings=False,
        use_progress=False,
    )

    if emb.shape[0] == 0:
        raise ValueError("No non-empty texts available for centroid computation.")

    centroid = emb.mean(axis=0)
    centroid = centroid / (np.linalg.norm(centroid) + 1e-12)
    return centroid


def cosine_between_vectors(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    return float(np.dot(a, b))


def compute_system_centroid_similarity(
    df: pd.DataFrame,
    system_cols: Dict[str, str],
    model_name: str = "BAAI/bge-m3",
    backend: str = "auto",
    batch_size: int = 64,
) -> pd.DataFrame:
    """
    Computes centroid embeddings for multiple systems and returns
    a cosine similarity matrix.

    Example:
        system_cols = {
            "gold": "gold_recommendation",
            "vanilla": "vanilla_recommendation",
            "rag": "rag_recommendation",
            "graphrag": "graphrag_recommendation",
        }
    """
    centroids: Dict[str, np.ndarray] = {}

    for system_name, col in system_cols.items():
        texts = df[col].fillna("").astype(str).tolist()
        centroids[system_name] = compute_centroid(
            texts=texts,
            model_name=model_name,
            backend=backend,
            batch_size=batch_size,
        )

    names = list(centroids.keys())
    sim_matrix = np.zeros((len(names), len(names)), dtype=float)

    for i, a in enumerate(names):
        for j, b in enumerate(names):
            sim_matrix[i, j] = cosine_between_vectors(centroids[a], centroids[b])

    return pd.DataFrame(sim_matrix, index=names, columns=names).round(4)