from functools import partial
from typing import List

import pandas as pd

from benchmarking_therapy_ovarian_cancer import config
from benchmarking_therapy_ovarian_cancer.benchmarking_methods.basic_rag import build_rag_llm_fn
from benchmarking_therapy_ovarian_cancer.config import LlmStrategy, cols_for
from benchmarking_therapy_ovarian_cancer.llm_vertex import get_text_llm_fn, init_vertexai_llm
from benchmarking_therapy_ovarian_cancer.oncology_status_classifier import classify_oncology_status
from benchmarking_therapy_ovarian_cancer.process_data import generate_recommendations_baseline, \
    generate_recommendations_graphrag, EXCLUDE_COLS


def make_llm_fn(strategy: LlmStrategy):
    if strategy == LlmStrategy.RAG:
        return build_rag_llm_fn(
            pdf_path=str(config.GUIDELINE_DATA_PATH),
            embedding_model_name=config.EMBEDDING_MODEL_NAME,
            llm_model_name=config.LLM_MODEL_NAME,
        )
    model = init_vertexai_llm(config.LLM_MODEL_NAME)
    return get_text_llm_fn(
        model = model
    )

def generate_recommendations(
        df: pd.DataFrame,
        strategies: List[LlmStrategy]
):
    df = classify_oncology_status(df)
    df_acc = df.copy()
    EXCLUDE_COLS_all = EXCLUDE_COLS

    for strategy in strategies:
        print(f"Generating recommendations for {strategy}")
        llm_fn = make_llm_fn(strategy)
        columns = config.cols_for(strategy)
        reco_col = columns["reco"]
        EXCLUDE_COLS_all =EXCLUDE_COLS_all.union({reco_col})

        if strategy == LlmStrategy.GRAPHRAG:
            df_rec = generate_recommendations_graphrag(
                df=df,
                reco_col=reco_col,
                exclude_cols=EXCLUDE_COLS_all
            )
        else:


            df_rec = generate_recommendations_baseline(
                df=df,
                strategy=strategy,
                llm_fn=llm_fn,
                reco_col=reco_col,
                exclude_cols=EXCLUDE_COLS_all
            )

        cols = list(set(df_rec.columns) - set(df_acc.columns))
        df_acc[cols] = df_rec[cols]
    return df_acc
