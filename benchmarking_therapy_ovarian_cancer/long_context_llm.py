import logging
import os
import vertexai
import pandas as pd
import pymupdf
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel
import config
from process_data import (
    generate_prompt,
    load_data,
    save_data,
    evaluate_patients
)
from evaluate_responses import apply_cosine_similarity
from config import LLM_MODEL_NAME


def init_vertexai() -> GenerativeModel:
    """Initialize Vertex AI with service account credentials and return the model."""
    if not os.path.exists("credentials.json"):
        print("Error: credentials.json is missing!")
        exit()
    credentials = service_account.Credentials.from_service_account_file("credentials.json")
    vertexai.init(
        project=config.gcp_project_id,
        location=config.gcp_region,
        credentials=credentials,
    )
    model = GenerativeModel(
        model_name=LLM_MODEL_NAME,
        generation_config=config.generation_config,
        safety_settings=config.safety_settings,
    )
    return model


def vertex_llm_response(prompt: str) -> str:
    """Call Vertex AI with the given prompt and return the response text."""
    model = init_vertexai()
    return model.generate_content(prompt).text


def extract_guideline_text(path: str, max_chars: int = 100_000) -> str:
    """Extract and return text from a PDF file up to a character limit."""
    doc = pymupdf.open(path)
    full_text = "\n".join(page.get_text() for page in doc)
    return full_text[:max_chars]


def main():
    logging.basicConfig(level=logging.INFO)

    df = load_data()
    context_text = extract_guideline_text(config.GUIDELINE_DATA_PATH)

    def prompt_with_context(row: pd.Series) -> str:
        return generate_prompt(
            patient_info=row,
            prompt_template=config.long_context_prompt_template,
            context_text=context_text
        )

    df = evaluate_patients(
        df=df,
        llm_fn=vertex_llm_response,
        prompt_generator_fn=prompt_with_context,
        output_col=config.long_context_output_col,
        reco_col=config.long_context_output_col_recommendation,
        reasoning_col=config.long_context_output_col_reasoning
    )

    df = apply_cosine_similarity(
        df,
        config.long_context_cosine_similarity_col,
        config.long_context_output_col_recommendation,
        config.gold_standard_col
    )

    save_data(df)


if __name__ == "__main__":
    main()
