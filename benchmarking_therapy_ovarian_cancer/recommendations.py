from functools import partial
from typing import List

import pandas as pd

from benchmarking_therapy_ovarian_cancer import config
from benchmarking_therapy_ovarian_cancer.benchmarking_methods.basic_rag import build_rag_llm_fn
from benchmarking_therapy_ovarian_cancer.config import LlmStrategy, cols_for
from benchmarking_therapy_ovarian_cancer.llm_vertex import get_text_llm_fn, init_vertexai_llm
from benchmarking_therapy_ovarian_cancer.benchmarking_methods.long_context_llm import _load_guideline_text
from benchmarking_therapy_ovarian_cancer.process_data import generate_prompt, evaluate_patients

def _generate_recommendations(df: pd.DataFrame,
                             strategy: LlmStrategy,
                             llm_fn: callable) -> pd.DataFrame:
    columns = cols_for(strategy)
    if strategy == LlmStrategy.LONG_CTX:
        context = _load_guideline_text(config.GUIDELINE_DATA_PATH)
    else:
        context = None
    prompt_gen = partial(generate_prompt, strategy=strategy, context_text=context)
    return evaluate_patients(
        df=df,
        llm_fn=llm_fn,
        prompt_generator_fn=prompt_gen,
        output_col=columns["output"],
        reco_col=columns["reco"],
        reasoning_col=columns["reasoning"],
    )


def make_llm_fn(strategy: LlmStrategy):
    # TODO
    # if strategy == LlmStrategy.VANILLA:
    if strategy == LlmStrategy.RAG:
        return build_rag_llm_fn(
            pdf_path=str(config.GUIDELINE_DATA_PATH),
            embedding_model_name=config.EMBEDDING_MODEL_NAME,
            llm_model_name=config.LLM_MODEL_NAME,
        )
        # LONG_CTX doesn't need own LLM just different prompt
    model = init_vertexai_llm(config.LLM_MODEL_NAME)
    return get_text_llm_fn(
        model = model
    )

def generate_recommendations_with_strategies(
        df: pd.DataFrame,
        strategies: List[LlmStrategy]):
    df_acc = df.copy()
    for strategy in strategies:
        llm_fn = make_llm_fn(strategy)
        df_rec = _generate_recommendations(df, strategy, llm_fn)
        cols = list(set(df_rec.columns) - set(df_acc.columns))
        df_acc[cols] = df_rec[cols]
    return df_acc
