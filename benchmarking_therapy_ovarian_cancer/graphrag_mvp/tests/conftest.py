from pathlib import Path


from benchmarking_therapy_ovarian_cancer import config
from ..utils import load_neo4j
import os
import pytest

from ...llm_vertex import get_json_llm_fn, init_vertexai_llm


@pytest.fixture(scope="session")
def llm_json():
    cred_path = getattr(config, "CREDENTIALS_PATH", None)
    if not cred_path or not os.path.exists(str(cred_path)):
        pytest.skip("credentials.json not found – skipping integration tests")
    model = init_vertexai_llm(config.LLM_MODEL_NAME)
    return get_json_llm_fn(model)


@pytest.fixture(scope="session")
def kg():

    kg = load_neo4j()

    kg.delete_all()
    kg.ensure_constraints()
    kg.ensure_constraints()
    # TODO
    cypher = Path(
        "/benchmarking_therapy_ovarian_cancer/graphrag_mvp/graph_cypher/subgraph_v1.cypher").read_text(encoding="utf-8")
    kg.run_write(cypher)
    yield kg

    kg.delete_all()
    kg.close()
