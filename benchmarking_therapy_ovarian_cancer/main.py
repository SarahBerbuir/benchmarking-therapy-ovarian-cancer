import pandas as pd

from benchmarking_therapy_ovarian_cancer import config
from benchmarking_therapy_ovarian_cancer.oncology_status_classifier import classify_oncology_status
from benchmarking_therapy_ovarian_cancer.config import LlmStrategy, EvaluationMetrics, reco_col_for
from benchmarking_therapy_ovarian_cancer.evaluation.evaluate_responses import apply_metrics_for_strategy
from benchmarking_therapy_ovarian_cancer.recommendations import generate_recommendations_with_strategies
from benchmarking_therapy_ovarian_cancer.replacing_abbreviation import expand_abbreviations_df

if __name__ == '__main__':
    print("Loading file")
    df = pd.read_excel(config.RAW_DATA_PATH)
    df = df.head(3).copy()

    print("Resolve abbreviations")
    df = expand_abbreviations_df(df)

    print("Classifying oncology status")
    df = classify_oncology_status(df)
    strategies = [LlmStrategy.VANILLA, LlmStrategy.LONG_CTX, LlmStrategy.RAG]
    print("Generating recommendations")
    df = generate_recommendations_with_strategies(df, strategies)

    print("Evaluating recommendations")
    evaluation_metrics = [EvaluationMetrics.BLEU] #EvaluationMetrics.COSINE, EvaluationMetrics.BERT, EvaluationMetrics.BLEU, EvaluationMetrics.ROUGE, EvaluationMetrics.LLM_AS_A_JUDGE]

    for strat in strategies:
        df = apply_metrics_for_strategy(
            df=df,
            strategy=strat,
            metrics=evaluation_metrics,
            candidate_col=reco_col_for(strat),
            reference_col=config.gold_standard_col,
        )
        print("test")


    # save_df_to_excel(df, OUTPUT_DATA_PATH)
    print("test")

