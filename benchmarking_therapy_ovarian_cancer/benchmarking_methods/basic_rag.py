# TODO possible Section-aware / Header-aware Chunking, in prompt: nur aus Quellen zitieren; kein Wissen außerhalb, als json antworten ?

from __future__ import annotations
import os
import time
from typing import Callable, Dict, Any

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_vertexai import VertexAI

from benchmarking_therapy_ovarian_cancer import config

# in-memory cache for retrievers
_CACHE: Dict[str, Dict[str, Any]] = {}


def _cache_key(pdf_path: str, emb_model: str) -> str:
    try:
        mtime = os.path.getmtime(pdf_path)
    except OSError:
        mtime = 0
    return f"{pdf_path}::{emb_model}::{mtime}"


def build_retriever(
    pdf_path: str,
    embedding_model_name: str,
    chunk_size: int = 700,
    chunk_overlap: int = 80,
):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    vectordb = FAISS.from_documents(chunks, embeddings)
    return vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 6})


def build_llm(
    model_name: str,
    temperature: float = 0.3,
    max_output_tokens: int = 2048,
) -> VertexAI:
    return VertexAI(
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        project=config.gcp_project_id,
        location=config.gcp_region,
    )


def build_rag_llm_fn(
    pdf_path: str = str(config.GUIDELINE_DATA_PATH),
    embedding_model_name: str = config.EMBEDDING_MODEL_NAME,
    llm_model_name: str = config.LLM_MODEL_NAME,
    temperature: float = 0,
    max_output_tokens: int = 2048,
) -> Callable[[str], str]:
    load_dotenv()
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(config.CREDENTIALS_PATH))

    key = _cache_key(pdf_path, embedding_model_name)
    if key in _CACHE:
        retriever = _CACHE[key]["retriever"]
    else:
        retriever = build_retriever(pdf_path, embedding_model_name)
        _CACHE[key] = {"retriever": retriever, "ts": time.time()}

    llm = build_llm(
        model_name=llm_model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type="stuff",
    )

    def llm_fn(prompt: str) -> str:
        try:
            out = qa.invoke(prompt)
        except Exception as e:
            return f"RAG error: {e}"

        if isinstance(out, str):
            return out.strip()
        if isinstance(out, dict):
            for k in ("answer", "result", "output_text"):
                v = out.get(k)
                if isinstance(v, str):
                    return v.strip()
        return (str(out) or "").strip()

    return llm_fn
