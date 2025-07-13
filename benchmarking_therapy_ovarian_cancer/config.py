from vertexai.generative_models import GenerationConfig, HarmCategory, HarmBlockThreshold
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent.parent

# Data paths
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "Raw_Deutsch_OV.xlsx"
OUTPUT_DATA_PATH = BASE_DIR / "data" / "processed" / "Raw_Deutsch_OV_wLLM.xlsx"
GUIDELINE_DATA_PATH = BASE_DIR / "data" / "raw" / "LL_Ovarialkarzinom_Langversion_6.0.pdf"

# Google Cloud config
gcp_project_id = os.getenv("GCP_PROJECT_ID")

gcp_region = "us-central1"


LLM_MODEL_NAME = "gemini-2.0-flash"
EMBEDDING_MODEL_NAME = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"

basic_prompt_template = treatment_prompt_german = """
## Aufgabe: Erstelle eine präzise Primärtherapie-Empfehlung

Du assistierst Onkolog:innen bei der Auswahl einer geeigneten Primärtherapie für Patienten mit komplexen oder seltenen Krebserkrankungen.

### Deine Aufgabe:

1. Lies sorgfältig die folgenden Patientendaten.
2. Gib eine konkrete, medizinisch präzise Therapieempfehlung (z.B. in der Form: "LSK mit Adnektomie bds. Ergänzung CT-Thorax ...").
3. Begründe deine Entscheidung klar auf Basis der Tumorbiologie, Biomarker, Literatur oder klinischer Studien.
4. Falls relevante Biomarker nicht bestimmt sind, aber laut Literatur sinnvoll wären, weise darauf hin.
5. Wenn klinische Studien infrage kommen, gib eine konkrete Empfehlung.

### Format:

Bitte gib deine Antwort in folgendem Format zurück:

**Therapieempfehlung:** <eine medizinisch präzise Zeile>

**Begründung:** <klarer Fließtext, warum diese Therapie für diesen Patienten geeignet ist, inkl. Verweise auf Biomarker, Studien oder Tumorbiologie>

---

### Patientendaten:
{patient_info}
"""

long_context_prompt_template = """
## Aufgabe: Erstelle eine präzise Primärtherapie-Empfehlung

Du assistierst Onkolog:innen bei der Auswahl einer geeigneten Primärtherapie für Patienten mit komplexen oder seltenen Krebserkrankungen.

### Kontext aus Leitlinie:

Nutze den folgenden Ausschnitt aus der medizinischen Leitlinie als Grundlage für deine Empfehlung. Beziehe dich **ausschließlich** auf diesen Kontext und die Patientendaten – keine Halluzinationen oder Vermutungen!

{context_block}

---

### Deine Aufgabe:

1. Lies sorgfältig die Patientendaten und den Leitlinienkontext.
2. Gib eine konkrete, medizinisch präzise Therapieempfehlung (z.B. in der Form: "LSK mit Adnektomie bds. Ergänzung CT-Thorax ...").
3. Begründe deine Entscheidung auf Basis der Tumorbiologie, Biomarker, Literatur oder klinischer Studien, **sofern im Kontext enthalten**.

### Format:

**Therapieempfehlung:** <eine medizinisch präzise Zeile>

**Begründung:** <warum diese Therapie auf Basis des Kontexts empfohlen wird>

---

### Patientendaten:
{patient_info}
"""
# 4. Wenn keine klare Empfehlung im Kontext gegeben ist, schreibe: "Keine klare Empfehlung laut Kontext gefunden."

gold_standard_col = "Original Tumorbaord-Empfehlung"

# LLM
llm_output_col = "LLM Evaluation"
llm_output_col_recommendation = "LLM_Empfehlung"
llm_output_col_reasoning = "LLM_Begründung"
llm_cosine_similarity_col = "cos_sim_llm"

# Basic RAG
rag_output_col = "RAG Evaluation"
rag_output_col_recommendation = "RAG_Empfehlung"
rag_output_col_reasoning = "RAG_Begründung"
rag_cosine_similarity_col = "cos_sim_rag"

# Long context LLM
long_context_output_col = "Long Context LLM Evaluation"
long_context_output_col_recommendation = "Long_Context_LLM_Empfehlung"
long_context_output_col_reasoning = "Long_Context_LLM_Begründung"
long_context_cosine_similarity_col = "cos_sim_long_context_llm"

generation_config = GenerationConfig(
    temperature=0.4,
    top_p=0.8,
    top_k=40,
    max_output_tokens=2048,
)

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}
