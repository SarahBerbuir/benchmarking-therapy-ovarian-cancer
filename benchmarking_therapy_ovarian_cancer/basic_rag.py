import logging
import os
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAI

from config import (
    GUIDELINE_DATA_PATH,
    EMBEDDING_MODEL_NAME,
    LLM_MODEL_NAME,
    rag_output_col_recommendation,
    rag_output_col_reasoning,
    rag_cosine_similarity_col,
    rag_output_col,
    gold_standard_col,
)

from process_data import generate_prompt, load_data, save_data, evaluate_patients
from evaluate_responses import apply_cosine_similarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def init_environment():
    """Load environment variables and configure credentials."""
    load_dotenv()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
    logger.info("Environment variables loaded.")
    return os.getenv("GCP_PROJECT_ID"), os.getenv("GCP_REGION")

def prepare_retrieval_qa(
        gcp_project,
        gcp_region,
        embedding_model_name=EMBEDDING_MODEL_NAME,
        llm_model_name=LLM_MODEL_NAME
):
    """ Initialize RetrievalQA with FAISS and VertexAI.
    Args:
        gcp_project (str): GCP project ID.
        gcp_region (str): GCP region.
        embedding_model_name (str): Name of the embedding model.
        llm_model_name (str): Name of the LLM model.
    Returns:
        RetrievalQA: Initialized RetrievalQA chain.
    """

    logger.info("Loading guideline document: %s", GUIDELINE_DATA_PATH)
    loader = PyPDFLoader(GUIDELINE_DATA_PATH)
    docs = loader.load()
    logger.info("Document loaded with %d pages", len(docs))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    logger.info("Document split into %d chunks", len(chunks))

    embedding = HuggingFaceEmbeddings(model_name=embedding_model_name)
    vectordb = FAISS.from_documents(chunks, embedding)
    retriever = vectordb.as_retriever()
    logger.info("FAISS retriever initialized.")

    llm = VertexAI(
        model_name=llm_model_name,
        temperature=0.3,
        max_output_tokens=2048,
        project=gcp_project,
        location=gcp_region,
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )
    logger.info("RetrievalQA chain initialized.")
    return qa_chain

def rag_llm_response_factory(qa_chain):
    """ Wrap the RetrievalQA chain as a function returning plain string result."""
    def rag_llm_response(prompt: str) -> str:
        response = qa_chain.invoke(prompt)
        return response["result"]
    return rag_llm_response

def main():
    gcp_project, gcp_region = init_environment()
    qa_chain = prepare_retrieval_qa(gcp_project, gcp_region)
    rag_llm_response = rag_llm_response_factory(qa_chain)

    df = load_data()

    df = evaluate_patients(
        df=df,
        llm_fn=rag_llm_response,
        prompt_generator_fn=generate_prompt,
        output_col=rag_output_col,
        reco_col=rag_output_col_recommendation,
        reasoning_col=rag_output_col_reasoning
    )

    df = apply_cosine_similarity(
        df,
        cosine_similarity_col=rag_cosine_similarity_col,
        output_col_reco=rag_output_col_recommendation,
        gold_standard_col=gold_standard_col
    )

    save_data(df)
    logger.info("Evaluation complete and results saved.")

if __name__ == "__main__":
    main()
