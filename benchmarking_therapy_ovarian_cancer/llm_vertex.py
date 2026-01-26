from pathlib import Path
import os, json
import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel
from typing import Callable, Dict, Any
from benchmarking_therapy_ovarian_cancer import config

def init_vertexai_llm(model_name: str | None = None) -> GenerativeModel:
    creds = Path(getattr(config, "CREDENTIALS_PATH", "credentials.json"))
    if not creds.exists():
        raise FileNotFoundError(f"credentials.json not found at {creds}")
    vertexai.init(
        project=config.gcp_project_id,
        location=config.gcp_region,
        credentials=service_account.Credentials.from_service_account_file(str(creds)),
    )
    return GenerativeModel(
        model_name=model_name or config.LLM_MODEL_NAME,
        generation_config=config.generation_config,
        safety_settings=config.safety_settings,
    )

def get_text_llm_fn(model: GenerativeModel) -> Callable[[str], str]:

    def llm_fn(prompt: str) -> str:
        return (model.generate_content(prompt).text or "").strip()
    return llm_fn

def get_json_llm_fn(model: GenerativeModel) -> Callable[[str, Dict[str, Any]], Dict[str, Any]]:
    def llm_json(prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        resp = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0, "top_p": 1, "top_k": 1,
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )
        return json.loads(resp.text or "{}")
    return llm_json
