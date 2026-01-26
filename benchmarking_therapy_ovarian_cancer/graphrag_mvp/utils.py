import json
from pathlib import Path

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.knowledge_graph import KG


def load_neo4j(path: str | Path = "credentials_neo4j.json") -> KG:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    return KG(cfg["uri"], cfg["user"], cfg["password"], database=cfg.get("database","neo4j"))
