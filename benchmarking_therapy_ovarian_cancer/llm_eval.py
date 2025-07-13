import vertexai
from benchmarking_therapy_ovarian_cancer import config
import logging
import os
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel
from process_data import generate_prompt, load_data, save_data, evaluate_patients
from evaluate_responses import apply_cosine_similarity
from config import LLM_MODEL_NAME


def init_vertexai():
    if not os.path.exists("credentials.json"):
        print("credentials.json missing!")
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
    model = init_vertexai()
    return model.generate_content(prompt).text


def main():
    logging.basicConfig(level=logging.INFO)

    df = load_data()

    df = evaluate_patients(
        df=df,
        llm_fn=vertex_llm_response,
        prompt_generator_fn=generate_prompt,
        output_col=config.llm_output_col,
        reco_col=config.llm_output_col_recommendation,
        reasoning_col=config.llm_output_col_reasoning
    )

    df = apply_cosine_similarity(
        df,
        config.llm_cosine_similarity_col,
        config.llm_output_col_recommendation,
        config.gold_standard_col)
    save_data(df)



if __name__ == "__main__":
    main()
