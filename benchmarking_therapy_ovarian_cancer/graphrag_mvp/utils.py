import json
from pathlib import Path

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.graph_cypher.cypher_graph.names_nodes import names
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.knowledge_graph import KG

ROOT_STEP = "Vorsorge/Symptome"

# Rebuild graph
def rebuild_graph(
        neo4j_path: str | Path = "credentials_neo4j.json",
        create_nodes_path: Path = Path("graph_cypher/cypher_graph/01_create_names.cypher"),
        create_flow_evidence_path: Path = Path("graph_cypher/cypher_graph/02_evidence_flow.cypher"),
        create_facts: Path = Path("graph_cypher/cypher_graph/03_facts.cypher")
    ):
    kg = load_neo4j(neo4j_path)
    kg.rebuild_from_cypher(create_nodes_path, names=names)
    kg.run_script(create_flow_evidence_path.read_text(encoding="utf-8"), names=names)
    kg.run_script(create_facts.read_text(encoding="utf-8"), names=names)
    return kg

def load_neo4j(path: str | Path = "credentials_neo4j.json") -> KG:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    return KG(cfg["uri"], cfg["user"], cfg["password"], database=cfg.get("database","neo4j"))
