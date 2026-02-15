from functools import partial
from pathlib import Path

import pandas as pd
from tqdm import tqdm

import config
from benchmarking_therapy_ovarian_cancer.benchmarking_methods.long_context_llm import _load_guideline_text
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.inference import run_inference
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.utils import rebuild_graph
from benchmarking_therapy_ovarian_cancer.prompt_list import diagnosed_prompt_template, suspected_prompt_template, \
    long_context_diagnosed_prompt_template, long_context_suspected_prompt_template

EXCLUDE_COLS = {
    config.gold_standard_col,
    "oncology_status", "oncology_rationale", "oncology_evidence_spans",
    "Patientin-ID", "Referenz Goldstandard", "Kommentar"
}

def generate_patient_info(patient: pd.Series, exclude_cols: list[str]) -> str:
    """
    Generate a formatted string with patient information for the prompt.
    :param patient: Series representing a single patient's data
    :return:
    """
    return " \n - ".join(
            f"{col}: {val}" for col, val in patient.items()
            if col not in exclude_cols and pd.notna(val) and str(val).strip()
        )

def generate_prompt(
    patient_info: pd.Series,
    exclude_cols: list[str],
    strategy: config.LlmStrategy = config.LlmStrategy.VANILLA,
    context_text: str | None = None
) -> str:
    """
    Generate a prompt for the LLM based on patient information and an optional context block.
    :param strategy:
    :param patient_info: Series containing patient data
    :param context_text: Optional context text to include in the prompt
    :return: Formatted prompt string
    """
    status = str(patient_info.get("oncology_status", "")).strip().lower()
    patient_block = generate_patient_info(patient_info, exclude_cols)
    if strategy == config.LlmStrategy.LONG_CTX:
        template = long_context_diagnosed_prompt_template if status == "Diagnose" else long_context_suspected_prompt_template
    else:
        template = diagnosed_prompt_template if status == "Diagnose" else suspected_prompt_template

    prompt_vars = {"patient_info": patient_block}
    if "{context_block}" in template:
        prompt_vars["context_block"] = context_text or ""

    return template.format(**prompt_vars)


def load_data() -> pd.DataFrame:
    # TODO remove [0:2]
    return pd.read_excel(config.RAW_DATA_PATH)#[0:]

def save_data(df: pd.DataFrame):
    df.to_excel(config.OUTPUT_DATA_PATH, index=False)

def generate_recommendations_baseline(
    df: pd.DataFrame,
    llm_fn: callable,
    reco_col,
    exclude_cols: list[str],
    strategy: config.LlmStrategy = config.LlmStrategy.VANILLA
) -> pd.DataFrame:
    """
    Evaluate each patient in the DataFrame using the respective method and store results in specified columns.
    """

    if strategy == config.LlmStrategy.LONG_CTX:
        context = _load_guideline_text(config.GUIDELINE_DATA_PATH)
    else:
        context = None
    prompt_generator_fn = partial(generate_prompt, exclude_cols = exclude_cols, strategy=strategy, context_text=context)

    if reco_col not in df.columns:
        df[reco_col] = ""

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        prompt = prompt_generator_fn(row)

        try:
            recommendation = llm_fn(prompt).strip()
            print(f"{row['Patientin-ID']}: {recommendation}")
            df.at[index, reco_col] = recommendation
        except Exception as e:
            df.at[index, reco_col] = f"Error: {e}"

    return df

def generate_recommendations_graphrag(
        df: pd.DataFrame,
        reco_col,
        exclude_cols: list[str]
    ) -> pd.DataFrame:
    if reco_col not in df.columns:
        df[reco_col] = ""
    kg = rebuild_graph(
        neo4j_path = config.CREDENTIALS_NEO4J,
        create_nodes_path=config.CREATE_NODES,
        create_flow_evidence_path=config.CREATE_FLOW_EVIDENCE,
        create_facts=config.CREATE_FACTS
    )

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):

        try:
            pid = row["Patientin-ID"]
            patient_block = generate_patient_info(row, exclude_cols)
            recommendation = run_inference(kg, pid, patient_block)
            print(f"{row['Patientin-ID']}: {recommendation}")
            df.at[index, reco_col] = recommendation
        except Exception as e:
            df.at[index, reco_col] = f"Error: {e}"

    return df

def save_df_to_excel(df, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)