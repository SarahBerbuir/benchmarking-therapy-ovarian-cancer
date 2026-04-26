from itertools import combinations
from pathlib import Path

import pandas as pd
from scipy import stats

from benchmarking_therapy_ovarian_cancer import config
from benchmarking_therapy_ovarian_cancer.config import (
    LlmStrategy,
    EvaluationMetrics,
    OUTPUT_DATA_PATH,
    reco_col_for,
)
from benchmarking_therapy_ovarian_cancer.evaluation.evaluate_responses import (
    apply_metrics_for_strategy,
    compute_system_centroid_similarity,
    summarize_metric_columns,
)
from benchmarking_therapy_ovarian_cancer.recommendations import generate_recommendations
from benchmarking_therapy_ovarian_cancer.replacing_abbreviation import expand_abbreviations_df


# Pipeline mode:
# - "full_pipeline": load raw data, expand abbreviations, generate recommendations, evaluate.
# - "evaluate_existing": load existing recommendations and only run evaluation/analysis.
MODE = "evaluate_existing"

# Use an integer for quick smoke tests, e.g. 3. Keep None for the full dataset.
ROW_LIMIT = None

# "standard" is faster; "full" includes the slower metrics as well.
METRIC_PRESET = "standard"

CHECK_PATIENT_IDS = True


STRATEGIES = [
    LlmStrategy.VANILLA,
    LlmStrategy.RAG,
    LlmStrategy.GRAPHRAG,
]


def get_input_path(mode: str):
    if mode == "full_pipeline":
        return config.RAW_DATA_PATH
    if mode == "evaluate_existing":
        return config.RECOMMENDATION_DATA_PATH

    raise ValueError(f"Unknown MODE: {mode}")


def get_metrics(preset: str):
    if preset == "standard":
        return [
            EvaluationMetrics.EMBED_COSINE,
            EvaluationMetrics.BERT,
            EvaluationMetrics.BLEU,
            EvaluationMetrics.ROUGE,
        ]

    if preset == "full":
        return [
            EvaluationMetrics.COSINE,
            EvaluationMetrics.EMBED_COSINE,
            EvaluationMetrics.RERANKER,
            EvaluationMetrics.BERT,
            EvaluationMetrics.BLEU,
            EvaluationMetrics.ROUGE,
            EvaluationMetrics.LLM_AS_A_JUDGE,
        ]

    raise ValueError(f"Unknown METRIC_PRESET: {preset}")


def load_data(mode: str, row_limit: int | None = None) -> pd.DataFrame:
    print("Loading file")
    df = pd.read_excel(get_input_path(mode))

    if row_limit is not None:
        df = df.head(row_limit).copy()

    return df


def validate_patient_ids(df: pd.DataFrame, id_col: str = "Patientin-ID") -> None:
    if id_col not in df.columns:
        print(f"Skipping ID check: column '{id_col}' not found.")
        return

    if not df[id_col].is_unique:
        dups = df.loc[df[id_col].duplicated(keep=False), id_col]
        raise ValueError(
            f"Column '{id_col}' contains duplicated IDs. "
            f"Examples: {dups.unique()[:10].tolist()}."
        )

    if df[id_col].isna().any():
        raise ValueError(f"Column '{id_col}' contains NaN.")

    if not pd.api.types.is_numeric_dtype(df[id_col]):
        raise TypeError(f"Column '{id_col}' is not numeric.")


def reference_col_for(df: pd.DataFrame) -> str:
    candidates = [
        getattr(config, "gold_standard_col", None),
        "Referenz",
    ]

    for col in candidates:
        if col and col in df.columns:
            return col

    raise KeyError("No reference column found. Expected config.gold_standard_col or 'Referenz'.")


def candidate_col_for_strategy(df: pd.DataFrame, strategy: LlmStrategy) -> str:
    fallback_cols = {
        LlmStrategy.VANILLA: ["LLM_empfehlung"],
        LlmStrategy.RAG: ["RAG_empfehlung"],
        LlmStrategy.GRAPHRAG: ["graphrag_empfehlung"],
    }

    candidates = [reco_col_for(strategy)] + fallback_cols.get(strategy, [])

    for col in candidates:
        if col in df.columns:
            return col

    raise KeyError(
        f"No recommendation column found for {strategy}. "
        f"Checked: {candidates}"
    )


def prepare_data(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if CHECK_PATIENT_IDS:
        validate_patient_ids(df)

    if mode == "full_pipeline":
        print("Resolving abbreviations")
        df = expand_abbreviations_df(df)

    return df


def maybe_generate_recommendations(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if mode != "full_pipeline":
        return df

    print("Generating recommendations")
    return generate_recommendations(
        df=df,
        strategies=STRATEGIES,
    )


def evaluate_recommendations(df: pd.DataFrame, metrics: list[EvaluationMetrics]) -> pd.DataFrame:
    print("Evaluating recommendations")

    ref_col = reference_col_for(df)

    for strategy in STRATEGIES:
        candidate_col = candidate_col_for_strategy(df, strategy)

        df = apply_metrics_for_strategy(
            df=df,
            strategy=strategy,
            metrics=metrics,
            candidate_col=candidate_col,
            reference_col=ref_col,
            embedding_model_name="BAAI/bge-m3",
            reranker_model_name="BAAI/bge-reranker-v2-m3",
            reranker_normalize_0_1=True,
            reranker_symmetric=False,
        )

    return df


def collect_metric_columns(df: pd.DataFrame, metrics: list[EvaluationMetrics]) -> list[str]:
    return [
        col for col in df.columns
        if any(col.startswith(metric.value) for metric in metrics)
    ]


def compute_shapiro_wilk(df: pd.DataFrame, metric_cols: list[str]) -> pd.DataFrame:
    results = []

    for col in metric_cols:
        vals = df[col].dropna()

        if len(vals) < 3:
            continue

        stat, p = stats.shapiro(vals)

        results.append({
            "metric": col,
            "shapiro_stat": round(stat, 4),
            "p_value": round(p, 4),
            "normal": p > 0.05,
        })

    return pd.DataFrame(results)


def compute_wilcoxon_tests(df: pd.DataFrame, min_pairs: int = 10) -> pd.DataFrame:
    strategy_pairs = list(combinations(["vanilla", "rag", "graphrag"], 2))

    metric_patterns = {
        "embed_cosine": "embed_cosine_{strat}",
        "bert": "bert_{strat}",
        "bleu1": "bleu_{strat}1",
        "bleu2": "bleu_{strat}2",
        "bleu4": "bleu_{strat}4",
        "rouge1": "rouge_{strat}1_f",
        "rouge2": "rouge_{strat}2_f",
        "rougeL": "rouge_{strat}L_f",
    }

    results = []

    for strat_a, strat_b in strategy_pairs:
        for metric_name, pattern in metric_patterns.items():
            col_a = pattern.replace("{strat}", strat_a)
            col_b = pattern.replace("{strat}", strat_b)

            if col_a not in df.columns or col_b not in df.columns:
                continue

            paired = df[[col_a, col_b]].dropna()

            if len(paired) < min_pairs:
                continue

            try:
                stat, p = stats.wilcoxon(
                    paired[col_a],
                    paired[col_b],
                    zero_method="wilcox",
                )

                results.append({
                    "comparison": f"{strat_a} vs {strat_b}",
                    "metric": metric_name,
                    "n_pairs": len(paired),
                    "statistic": round(stat, 4),
                    "p_value": round(p, 4),
                    "significant": p < 0.05,
                })

            except Exception as e:
                results.append({
                    "comparison": f"{strat_a} vs {strat_b}",
                    "metric": metric_name,
                    "n_pairs": len(paired),
                    "statistic": None,
                    "p_value": None,
                    "significant": None,
                    "note": str(e),
                })

    return pd.DataFrame(results)


def compute_recommendation_lengths(df: pd.DataFrame) -> pd.DataFrame:
    length_cols = {
        "Gold": reference_col_for(df),
        "LLM": candidate_col_for_strategy(df, LlmStrategy.VANILLA),
        "RAG": candidate_col_for_strategy(df, LlmStrategy.RAG),
        "GraphRAG": candidate_col_for_strategy(df, LlmStrategy.GRAPHRAG),
    }

    results = []

    for system, col in length_cols.items():
        words = df[col].dropna().apply(lambda x: len(str(x).split()))

        results.append({
            "system": system,
            "median": round(words.median(), 1),
            "q1": round(words.quantile(0.25), 1),
            "q3": round(words.quantile(0.75), 1),
        })

    return pd.DataFrame(results)


def compute_analysis_tables(df: pd.DataFrame, metrics: list[EvaluationMetrics]) -> dict[str, pd.DataFrame]:
    metric_cols = collect_metric_columns(df, metrics)

    system_cols = {
        "gold": reference_col_for(df),
        "vanilla": candidate_col_for_strategy(df, LlmStrategy.VANILLA),
        "rag": candidate_col_for_strategy(df, LlmStrategy.RAG),
        "graphrag": candidate_col_for_strategy(df, LlmStrategy.GRAPHRAG),
    }

    return {
        "summary_median_iqr": summarize_metric_columns(df, metric_cols=metric_cols),
        "centroid_similarity": compute_system_centroid_similarity(df, system_cols=system_cols),
        "shapiro_wilk": compute_shapiro_wilk(df, metric_cols),
        "wilcoxon_tests": compute_wilcoxon_tests(df),
        "recommendation_lengths": compute_recommendation_lengths(df),
    }


def output_path() -> Path:
    path = Path(OUTPUT_DATA_PATH)
    return path.with_name(f"{path.stem}_results{path.suffix}")


def save_results(df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    path = output_path()

    print(f"Saving file: {path}")

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name="raw_scores", index=False)

        for sheet_name, table in tables.items():
            write_index = sheet_name == "centroid_similarity"
            table.to_excel(writer, sheet_name=sheet_name, index=write_index)


def main() -> None:
    metrics = get_metrics(METRIC_PRESET)

    df = load_data(MODE, row_limit=ROW_LIMIT)
    df = prepare_data(df, MODE)
    df = maybe_generate_recommendations(df, MODE)
    df = evaluate_recommendations(df, metrics)

    tables = compute_analysis_tables(df, metrics)
    save_results(df, tables)

    print("Done")


if __name__ == "__main__":
    main()