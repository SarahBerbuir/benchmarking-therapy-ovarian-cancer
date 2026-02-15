import pandas as pd

from benchmarking_therapy_ovarian_cancer import config
from benchmarking_therapy_ovarian_cancer.config import LlmStrategy, EvaluationMetrics, reco_col_for, OUTPUT_DATA_PATH
from benchmarking_therapy_ovarian_cancer.evaluation.evaluate_responses import apply_metrics_for_strategy
from benchmarking_therapy_ovarian_cancer.process_data import save_df_to_excel
from benchmarking_therapy_ovarian_cancer.recommendations import generate_recommendations
from benchmarking_therapy_ovarian_cancer.replacing_abbreviation import expand_abbreviations_df

if __name__ == '__main__':
    print("Loading file")
    df = pd.read_excel(config.RAW_DATA_PATH)
    df = df.head(3).copy()

    col = "Patientin-ID"
    if not df[col].is_unique:
        dups = df.loc[df[col].duplicated(keep=False), col]
        raise ValueError(
            f"Column '{col}' contains doubled Ids. E.g.: {dups.unique()[:10].tolist()}."
        )
    if df[col].isna().any():
        raise ValueError(f"Column '{col}' contains NaN.")
    if not pd.api.types.is_numeric_dtype(df[col]):
        raise TypeError(f"Column '{col}' is not numeric.")

    print("Resolve abbreviations")
    df = expand_abbreviations_df(df)

    strategies = [LlmStrategy.VANILLA, LlmStrategy.RAG, LlmStrategy.GRAPHRAG]

    print("Generate recommendations")
    df = generate_recommendations(
            df=df,
            strategies=strategies
        )

    print("Evaluate recommendations")
    evaluation_metrics = [
        EvaluationMetrics.COSINE,  # TF-IDF Cosine (lexikal)
        EvaluationMetrics.EMBED_COSINE,  # Embeddings + Cosine (semantisch, schnell)
        EvaluationMetrics.RERANKER,  # Cross-Encoder Score (meist beste Qualität)
        EvaluationMetrics.BERT,
        EvaluationMetrics.BLEU,
        EvaluationMetrics.ROUGE,
        EvaluationMetrics.LLM_AS_A_JUDGE,
    ]

    for strat in strategies:
        df = apply_metrics_for_strategy(
            df=df,
            strategy=strat,
            metrics=evaluation_metrics,
            candidate_col=reco_col_for(strat),
            reference_col=config.gold_standard_col,
            embedding_model_name="BAAI/bge-m3",
            reranker_model_name="BAAI/bge-reranker-v2-m3",
            reranker_normalize_0_1=True,
            reranker_symmetric=False,
        )

    print("Saving file")
    save_df_to_excel(df, OUTPUT_DATA_PATH)

