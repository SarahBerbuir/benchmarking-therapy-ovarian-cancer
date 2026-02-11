from pathlib import Path

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.graph_cypher.cypher_graph.names_nodes import names
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.inference import run_inference

import logging

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.utils import load_neo4j

logging.basicConfig(
    level=logging.INFO,                    # oder DEBUG
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


# Rebuild graph
kg = load_neo4j()
kg.rebuild_from_cypher("graph_cypher/cypher_graph/01_create_names.cypher", names=names)
kg.run_script(Path("graph_cypher/cypher_graph/02_evidence_flow.cypher").read_text(encoding="utf-8"), names=names)
kg.run_script(Path("graph_cypher/cypher_graph/03_facts.cypher").read_text(encoding="utf-8"), names=names)



pid = "PDEMO1"
patient_text = "Adjuvante Therapie abgeschlossen mit Carboplatin 6x. Laparotomie mit low grade Ovarialkarzinom FIGO III"#"Adjuvante Therapie abgeschlossen mit Carboplatin 6x. gBRCA-. sBRCA- sHRD-. Laparotomie mit low grade Ovarialkarzinom FIGO III"
    #"CT FIGO IA"#Carboplatin adjuvante Therapie abgeschlossen. 6 Zyklen"#"Sono: unilokuläre Zyste, keine soliden Anteile <7mm, Schallschatten vorhanden, glatte multilokuläre Struktur <10 cm, kein starker Dopplerfluss. Kein Aszites. Kein CT vorhanden. Zystenausschälung ist gemacht worden und seine histologie wahrscheinlich benign"
#patient_text= #"Sono: unilokuläre Zyste, keine soliden Anteile <7mm, Schallschatten vorhanden, glatte multilokuläre Struktur <10 cm, kein starker Dopplerfluss. Kein Aszites. Kein CT vorhanden."
    # "Keine Sonographie. Kein CT. Keine OP. Keine Verlaufskontrolle." #"Adjuvante Therapie abgeschlossen mit Carboplatin 6x. gBRCA-. sBRCA- sHRD-. Laparotomie mit low grade Ovarialkarzinom FIGO III" # CT Thorax/Abdomen vorliegend, klinisch FIGO IIIA. Laparoskopie mit anschließender Laparotomie, Histologie maligne, Grading high, FIGO pathologisch IIIA2. Adjuvante Systemtherapie (Carboplatin 6×) komplett verabreicht; kein Protokollwechsel. Aktuell Nachsorge geplant."
    #"Keine Sonographie. Kein CT. Keine OP. Keine Verlaufskontrolle."
    #"Sono: unilokuläre Zyste, keine soliden Anteile <7mm, Schallschatten vorhanden, glatte multilokuläre Struktur <10 cm, kein starker Dopplerfluss. Kein Aszites. Kein CT vorhanden."#Kein Sono und kein CT"#"Sono: Aszites im Abdomen; CT" # . CT Abdomen liegt vor" # unilokuläre Zyste.
#CT FIGO IA
res = run_inference(kg, pid, patient_text)
