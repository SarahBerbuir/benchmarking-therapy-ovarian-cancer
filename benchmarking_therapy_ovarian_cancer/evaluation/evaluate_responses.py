from __future__ import annotations

from typing import List, Tuple, Optional, Dict, Any

import numpy as np
import pandas as pd
import torch

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import BERTScorer

from benchmarking_therapy_ovarian_cancer.config import EvaluationMetrics, LlmStrategy, metric_col
from benchmarking_therapy_ovarian_cancer.evaluation.llm_as_a_judge import apply_llm_judge_json
from benchmarking_therapy_ovarian_cancer.llm_vertex import init_vertexai_llm, get_json_llm_fn


try:
    from tqdm.auto import tqdm
except Exception:  # pragma: no cover
    tqdm = None


_ROUGE_SCORER: Optional[rouge_scorer.RougeScorer] = None
_BERTSCORER_CACHE: Dict[Tuple[str, bool, int, str], BERTScorer] = {}
_EMBEDDER_CACHE: Dict[Tuple[str, str], Any] = {}
_RERANKER_CACHE: Dict[str, Any] = {}


def _to_text_list(s: pd.Series) -> List[str]:
    return s.fillna("").astype(str).tolist()


def _get_rouge_scorer() -> rouge_scorer.RougeScorer:
    global _ROUGE_SCORER
    if _ROUGE_SCORER is None:
        _ROUGE_SCORER = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
    return _ROUGE_SCORER


def _get_bertscorer(model_type: str, rescale: bool, batch_size: int, device: str) -> BERTScorer:
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

def apply_tfidf_cosine(
    df: pd.DataFrame,
    out_col: str,
    candidate_col: str,
    reference_col: str,
) -> pd.DataFrame:
    if out_col not in df.columns:
        df[out_col] = 0.0

    cands = _to_text_list(df[candidate_col])
    refs  = _to_text_list(df[reference_col])

    mask = np.array([bool(c.strip()) and bool(r.strip()) for c, r in zip(cands, refs)], dtype=bool)
    out = np.zeros(len(df), dtype=float)
    if not mask.any():
        df[out_col] = 0.0
        return df

    c_eff = [c for c, m in zip(cands, mask) if m]
    r_eff = [r for r, m in zip(refs,  mask) if m]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(c_eff + r_eff)
    n = len(c_eff)
    Xc = normalize(X[:n])
    Xr = normalize(X[n:])

    sims = np.asarray(Xc.multiply(Xr).sum(axis=1)).ravel()
    out[mask] = np.nan_to_num(sims, nan=0.0, posinf=0.0, neginf=0.0)

    df[out_col] = np.round(out, 4)
    return df

def _get_embedder(model_name: str, backend: str = "auto") -> tuple[str, Any]:

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
            raise ImportError("Für bge-m3 via FlagEmbedding: pip install FlagEmbedding") from e
        model = BGEM3FlagModel(model_name)
        _EMBEDDER_CACHE[key] = model
        return backend, model

    # sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise ImportError("Für Embeddings via sentence-transformers: pip install sentence-transformers") from e
    model = SentenceTransformer(model_name)
    _EMBEDDER_CACHE[key] = model
    return backend, model


def apply_embedding_cosine(
    df: pd.DataFrame,
    out_col: str,
    candidate_col: str,
    reference_col: str,
    model_name: str = "BAAI/bge-m3",
    backend: str = "auto",
    batch_size: int = 64,
    use_progress: bool = True,
) -> pd.DataFrame:
    if out_col not in df.columns:
        df[out_col] = 0.0

    cands = _to_text_list(df[candidate_col])
    refs  = _to_text_list(df[reference_col])

    mask = np.array([bool(c.strip()) and bool(r.strip()) for c, r in zip(cands, refs)], dtype=bool)
    out = np.zeros(len(df), dtype=float)
    if not mask.any():
        df[out_col] = 0.0
        return df

    c_eff = [c for c, m in zip(cands, mask) if m]
    r_eff = [r for r, m in zip(refs,  mask) if m]

    backend_used, model = _get_embedder(model_name, backend=backend)

    if "e5" in model_name.lower():
        c_eff = [("query: " + t) for t in c_eff]
        r_eff = [("passage: " + t) for t in r_eff]

    if backend_used == "flag":
        try:
            oc = model.encode(c_eff, return_dense=True, batch_size=batch_size)
        except TypeError:
            oc = model.encode(c_eff, return_dense=True)
        try:
            orf = model.encode(r_eff, return_dense=True, batch_size=batch_size)
        except TypeError:
            orf = model.encode(r_eff, return_dense=True)

        emb_c = np.asarray(oc["dense_vecs"], dtype=float)
        emb_r = np.asarray(orf["dense_vecs"], dtype=float)

        emb_c = emb_c / (np.linalg.norm(emb_c, axis=1, keepdims=True) + 1e-12)
        emb_r = emb_r / (np.linalg.norm(emb_r, axis=1, keepdims=True) + 1e-12)
        sims = (emb_c * emb_r).sum(axis=1)

    else:
        emb_c = model.encode(c_eff, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=use_progress)
        emb_r = model.encode(r_eff, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=use_progress)
        sims = (emb_c * emb_r).sum(axis=1)

    out[mask] = np.nan_to_num(sims, nan=0.0, posinf=0.0, neginf=0.0)
    df[out_col] = np.round(out, 4)
    return df


def _get_reranker(model_name: str):
    if model_name in _RERANKER_CACHE:
        return _RERANKER_CACHE[model_name]
    try:
        from FlagEmbedding import FlagReranker
    except Exception as e:
        raise ImportError("Für Reranker: pip install FlagEmbedding") from e
    rr = FlagReranker(model_name, use_fp16=torch.cuda.is_available())
    _RERANKER_CACHE[model_name] = rr
    return rr


def apply_reranker_score(
    df: pd.DataFrame,
    out_col: str,
    candidate_col: str,
    reference_col: str,
    model_name: str = "BAAI/bge-reranker-v2-m3",
    normalize_0_1: bool = True,
    symmetric: bool = False,     # avg(score(a,b), score(b,a))
    use_progress: bool = True,
) -> pd.DataFrame:
    if out_col not in df.columns:
        df[out_col] = 0.0

    cands = _to_text_list(df[candidate_col])
    refs  = _to_text_list(df[reference_col])

    pairs = []
    idxs = []
    for i, (c, r) in enumerate(zip(cands, refs)):
        if c.strip() and r.strip():
            pairs.append([c, r])
            idxs.append(i)

    out = np.zeros(len(df), dtype=float)
    if not pairs:
        df[out_col] = 0.0
        return df

    rr = _get_reranker(model_name)

    # compute in one shot
    scores = np.asarray(rr.compute_score(pairs, normalize=normalize_0_1), dtype=float)

    if symmetric:
        pairs_rev = [[b, a] for a, b in pairs]
        scores2 = np.asarray(rr.compute_score(pairs_rev, normalize=normalize_0_1), dtype=float)
        scores = 0.5 * (scores + scores2)

    out[idxs] = scores
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

    if out_col not in df.columns:
        df[out_col] = 0.0

    cands = _to_text_list(df[candidate_col])
    refs  = _to_text_list(df[reference_col])

    mask = [bool(c.strip()) and bool(r.strip()) for c, r in zip(cands, refs)]
    if not any(mask):
        df[out_col] = 0.0
        return df

    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        torch.set_num_threads(1)
    except Exception:
        pass

    scorer = _get_bertscorer(model_type, rescale_with_baseline, batch_size, device)

    c_eff = [c for c, m in zip(cands, mask) if m]
    r_eff = [r for r, m in zip(refs,  mask) if m]

    try:
        _, _, F1 = scorer.score(c_eff, r_eff)
        f1_vals = F1.detach().cpu().numpy()
    except Exception:
        f1_vals = np.zeros(len(c_eff), dtype=float)

    out = np.zeros(len(df), dtype=float)
    j = 0
    for i, m in enumerate(mask):
        out[i] = float(f1_vals[j]) if m else 0.0
        if m:
            j += 1

    df[out_col] = np.round(out, 4)
    return df

def apply_bleu(df: pd.DataFrame, prefix: str, candidate_col: str, reference_col: str) -> pd.DataFrame:
    sm = SmoothingFunction().method3
    weights = {
        "1": (1.0, 0.0, 0.0, 0.0),
        "2": (0.5, 0.5, 0.0, 0.0),
        "4": (0.25, 0.25, 0.25, 0.25),
    }

    cands = _to_text_list(df[candidate_col])
    refs  = _to_text_list(df[reference_col])

    # pre-tokenize once
    c_tok = [c.lower().split() for c in cands]
    r_tok = [r.lower().split() for r in refs]

    for k, w in weights.items():
        col = f"{prefix}{k}"
        df[col] = [
            round(sentence_bleu([rt], ct, weights=w, smoothing_function=sm), 4)
            if ct and rt else 0.0
            for ct, rt in zip(c_tok, r_tok)
        ]
    return df

def apply_rouge(df: pd.DataFrame, prefix: str, candidate_col: str, reference_col: str) -> pd.DataFrame:
    c1, c2, cL = f"{prefix}1_f", f"{prefix}2_f", f"{prefix}L_f"
    for c in (c1, c2, cL):
        if c not in df.columns:
            df[c] = 0.0

    sc = _get_rouge_scorer()

    cands = _to_text_list(df[candidate_col])
    refs  = _to_text_list(df[reference_col])

    r1 = np.zeros(len(df), dtype=float)
    r2 = np.zeros(len(df), dtype=float)
    rL = np.zeros(len(df), dtype=float)

    for i, (h, r) in enumerate(zip(cands, refs)):
        if not (h.strip() and r.strip()):
            continue
        try:
            s = sc.score(r, h)  # (reference, hypothesis)
            r1[i] = s["rouge1"].fmeasure
            r2[i] = s["rouge2"].fmeasure
            rL[i] = s["rougeL"].fmeasure
        except Exception:
            pass

    df[c1] = np.round(r1, 4)
    df[c2] = np.round(r2, 4)
    df[cL] = np.round(rL, 4)
    return df

def apply_metrics_for_strategy(
    df: pd.DataFrame,
    strategy: LlmStrategy,
    metrics: List[EvaluationMetrics],
    candidate_col: str,
    reference_col: str,
    # new knobs:
    embedding_model_name: str = "BAAI/bge-m3",
    embedding_backend: str = "auto",
    reranker_model_name: str = "BAAI/bge-reranker-v2-m3",
    reranker_normalize_0_1: bool = True,
    reranker_symmetric: bool = False,
) -> pd.DataFrame:
    out = df
    llm_json = None

    for metric in metrics:
        print(f"Evaluating {metric.name}")
        metric_column = metric_col(metric=metric, strategy=strategy)

        if metric == EvaluationMetrics.COSINE:
            # COSINE = TF-IDF Cosine (lexikal)
            out = apply_tfidf_cosine(out, metric_column, candidate_col, reference_col)

        elif metric == EvaluationMetrics.EMBED_COSINE:
            out = apply_embedding_cosine(
                out, metric_column, candidate_col, reference_col,
                model_name=embedding_model_name,
                backend=embedding_backend,
            )

        elif metric == EvaluationMetrics.RERANKER:
            out = apply_reranker_score(
                out, metric_column, candidate_col, reference_col,
                model_name=reranker_model_name,
                normalize_0_1=reranker_normalize_0_1,
                symmetric=reranker_symmetric,
            )

        elif metric == EvaluationMetrics.BERT:
            out = apply_bertscore(out, metric_column, candidate_col, reference_col)

        elif metric == EvaluationMetrics.BLEU:
            out = apply_bleu(out, metric_column, candidate_col, reference_col)

        elif metric == EvaluationMetrics.ROUGE:
            out = apply_rouge(out, metric_column, candidate_col, reference_col)

        elif metric == EvaluationMetrics.LLM_AS_A_JUDGE:
            if llm_json is None:
                model = init_vertexai_llm()
                llm_json = get_json_llm_fn(model)
            out = apply_llm_judge_json(
                df=out,
                llm_json=llm_json,
                candidate_col=candidate_col,
                reference_col=reference_col,
                prefix=metric_column,
            )
        else:
            raise ValueError(f"Unknown metric: {metric}")

    return out
