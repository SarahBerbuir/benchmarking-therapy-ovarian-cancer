from benchmarking_therapy_ovarian_cancer.graphrag_mvp.inference import start_inference

import logging

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.utils import load_neo4j

logging.basicConfig(
    level=logging.INFO,                    # oder DEBUG
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


kg = load_neo4j()
kg.rebuild_from_cypher("graph_cypher/subgraph_v1_1.cypher")


pid = "PDEMO1"
patient_text = "Sono: unilokuläre Zyste, keine soliden Anteile <7mm, Schallschatten vorhanden, glatte multilokuläre Struktur <10 cm, kein starker Dopplerfluss. Kein Aszites. Kein CT vorhanden."#Kein Sono und kein CT"#"Sono: Aszites im Abdomen; CT" # . CT Abdomen liegt vor" # unilokuläre Zyste.

res = start_inference(kg, pid, patient_text)
print(res)
