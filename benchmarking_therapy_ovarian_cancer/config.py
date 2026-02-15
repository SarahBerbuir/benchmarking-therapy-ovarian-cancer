from vertexai.generative_models import GenerationConfig, HarmCategory, HarmBlockThreshold
from pathlib import Path
import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

PROJECT_ROOT = Path(__file__).resolve().parents[0]
CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"

class LlmStrategy(Enum):
    VANILLA = "vanilla"
    RAG = "rag"
    LONG_CTX = "long_ctx"
    GRAPHRAG = "graphrag"

def prefix_for(strategy: LlmStrategy) -> str:
    return strategy.value

_COL_TEMPLATES = {
    "output":    "{pfx}_evaluation",
    "reco":      "{pfx}_empfehlung",
    "reasoning": "{pfx}_begründung",
}


class EvaluationMetrics(Enum):
    COSINE = "cosine"         # bleibt TF-IDF Cosine
    EMBED_COSINE = "embed_cosine"
    RERANKER = "reranker"
    BERT = "bert"
    BLEU = "bleu"
    ROUGE = "rouge"
    LLM_AS_A_JUDGE = "llm_as_a_judge"

def cols_for(strategy: LlmStrategy) -> dict[str, str]:
    """Return dict mit keys: output, reco, reasoning."""
    pfx = prefix_for(strategy)
    return {k: v.format(pfx=pfx) for k, v in _COL_TEMPLATES.items()}

def reco_col_for(strategy: LlmStrategy) -> str:
    return cols_for(strategy)["reco"]

def reasoning_col_for(strategy: LlmStrategy) -> str:
    return cols_for(strategy)["reasoning"]

def metric_col(metric: EvaluationMetrics, strategy: LlmStrategy, suffix: str | None = None) -> str:
    """
    metric_col(EvaluationMetrics.COSINE, LlmStrategy.VANILLA) -> 'cos_sim_vanilla'
    metric_col(EvaluationMetrics.BLEU,   LlmStrategy.VANILLA, '1') -> 'bleu_vanilla1'
    metric_col(EvaluationMetrics.ROUGE,  LlmStrategy.LONG_CTX, 'L_f') -> 'rouge_long_ctxL_f'
    """
    base = f"{metric.value}_{prefix_for(strategy)}"
    return f"{base}{suffix}" if suffix else base


# Column names
gold_standard_col = "Original Tumorboard-Empfehlung"

# Data paths
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "2026-02-09_Raw_Deutsch_OV.xlsx"
OUTPUT_DATA_PATH = BASE_DIR / "data" / "processed" / "Raw_Deutsch_OV_wLLM5.xlsx"
GUIDELINE_DATA_PATH = BASE_DIR / "data" / "raw" / "LL_Ovarialkarzinom_Langversion_6.0.pdf"
CREDENTIALS_NEO4J = BASE_DIR / "benchmarking_therapy_ovarian_cancer/graphrag_mvp/credentials_neo4j.json"
CREATE_NODES = BASE_DIR / "benchmarking_therapy_ovarian_cancer/graphrag_mvp/graph_cypher/cypher_graph/01_create_names.cypher"
CREATE_FLOW_EVIDENCE = BASE_DIR / "benchmarking_therapy_ovarian_cancer/graphrag_mvp/graph_cypher/cypher_graph/02_evidence_flow.cypher"
CREATE_FACTS = BASE_DIR / "benchmarking_therapy_ovarian_cancer/graphrag_mvp/graph_cypher/cypher_graph/03_facts.cypher"

# Google Cloud config
gcp_project_id = os.getenv("GCP_PROJECT_ID")

gcp_region = "us-central1"

# Model configuration
# TODO try out more
LLM_MODEL_NAME = "gemini-2.5-flash"
EMBEDDING_MODEL_NAME = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"


generation_config = GenerationConfig(
    temperature=0.4,
    top_p=0.8,
    top_k=40,
    max_output_tokens=2048,
)

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}
