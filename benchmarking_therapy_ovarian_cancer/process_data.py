import pandas as pd
import config


def generate_patient_info(patient: pd.Series) -> str:
    """
    Generate a formatted string with patient information for the prompt.
    :param df: DataFrame containing patient data
    :param patient: Series representing a single patient's data
    :return:
    """
    return "\n".join(
        f"{col}: {patient[col]}" for col in patient.index
        if col not in [
            config.gold_standard_col,
            config.llm_output_col,
            config.llm_output_col_recommendation,
            config.llm_output_col_reasoning,
        ]
    )

def generate_prompt(
    patient_info: pd.Series,
    prompt_template: str = config.basic_prompt_template,
    context_text: str | None = None
) -> str:
    """
    Generate a prompt for the LLM based on patient information and an optional context block.
    :param patient_info: Series containing patient data
    :param prompt_template: Template string for the prompt
    :param context_text: Optional context text to include in the prompt
    :return: Formatted prompt string
    """
    patient_block = generate_patient_info(patient_info)

    prompt_vars = {"patient_info": patient_block}
    if "{context_block}" in prompt_template:
        prompt_vars["context_block"] = context_text or ""

    return prompt_template.format(**prompt_vars)

def split_response(full_text: str) -> tuple[str, str]:
    """
    Extract therapy recommendation and reasoning from a structured response.
    """
    if "**Therapieempfehlung:**" in full_text and "**Begründung:**" in full_text:
        parts = full_text.split("**Begründung:**")
        recommendation = parts[0].replace("**Therapieempfehlung:**", "").strip()
        reasoning = parts[1].strip()
    else:
        recommendation = "Not extractable"
        reasoning = full_text.strip()
    return recommendation, reasoning

def load_data() -> pd.DataFrame:
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