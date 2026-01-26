from pathlib import Path

import pandas as pd
import config
from benchmarking_therapy_ovarian_cancer.prompt_list import diagnosed_prompt_template, suspected_prompt_template, \
    long_context_diagnosed_prompt_template, long_context_suspected_prompt_template

EXCLUDE_COLS = {
    config.gold_standard_col,
    getattr(config, "llm_output_col", ""),
    getattr(config, "llm_output_col_recommendation", ""),
    getattr(config, "llm_output_col_reasoning", ""),
    "oncology_status", "oncology_rationale", "oncology_evidence_spans",
}

def generate_patient_info(patient: pd.Series) -> str:
    """
    Generate a formatted string with patient information for the prompt.
    :param patient: Series representing a single patient's data
    :return:
    """
    return "\n".join(
            f"{col}: {val}" for col, val in patient.items()
            if col not in EXCLUDE_COLS and pd.notna(val) and str(val).strip()
        )

def generate_prompt(
    patient_info: pd.Series,
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
    patient_block = generate_patient_info(patient_info)
    # TODO if I have more
    #if strategy == config.LlmStrategy.VANILLA:
    if strategy == config.LlmStrategy.LONG_CTX:
        template = long_context_diagnosed_prompt_template if status == "diagnosed" else long_context_suspected_prompt_template
    else:
        template = diagnosed_prompt_template if status == "diagnose" else suspected_prompt_template

    prompt_vars = {"patient_info": patient_block}
    if "{context_block}" in template:
        prompt_vars["context_block"] = context_text or ""

    return template.format(**prompt_vars)

#TODO make json
def split_response(full_text: str) -> tuple[str, str]:
    """
    Extract therapy recommendation and reasoning from a structured response.
    """
    if "**Therapieempfehlung:**" in full_text and "**Begründung:**" in full_text:
        parts = full_text.split("**Begründung:**")
        recommendation = parts[0].replace("**Therapieempfehlung:**", "").strip()
        recommendation = recommendation.replace("Therapieempfehlung:", "")
        reasoning = parts[1].strip()
    else:
        recommendation = "Not extractable"
        reasoning = full_text.strip()
    return recommendation, reasoning

def load_data() -> pd.DataFrame:
    # TODO remove [0:2]
    return pd.read_excel(config.RAW_DATA_PATH)[0:2]

def save_data(df: pd.DataFrame):
    df.to_excel(config.OUTPUT_DATA_PATH, index=False)

def evaluate_patients(
    df: pd.DataFrame,
    llm_fn: callable,
    prompt_generator_fn: callable,
    output_col: str,
    reco_col: str,
    reasoning_col: str
) -> pd.DataFrame:
    """
    Evaluate each patient in the DataFrame using the respective method and store results in specified columns.
    :param df: DataFrame containing patient data
    :param llm_fn: Function to call the respective method with a prompt
    :param prompt_generator_fn: Function to generate the prompt for each patient
    :param output_col: Column name to store the full response
    :param reco_col: Column name to store the therapy recommendation
    :param reasoning_col: Column name to store the reasoning
    :return: DataFrame with results added
    """
    for col in [output_col, reco_col, reasoning_col]:
        if col not in df.columns:
            df[col] = ""

    for index, row in df.iterrows():
        prompt = prompt_generator_fn(row)

        try:
            full_text = llm_fn(prompt).strip()
            recommendation, reasoning = split_response(full_text)

            df.at[index, output_col] = full_text
            df.at[index, reco_col] = recommendation
            df.at[index, reasoning_col] = reasoning

        except Exception as e:
            df.at[index, output_col] = f"Error: {e}"
            df.at[index, reco_col] = ""
            df.at[index, reasoning_col] = ""

    return df

def save_df_to_excel(df, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)