from benchmarking_therapy_ovarian_cancer.graphrag_mvp.inference import start_inference

import logging

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.utils import load_neo4j

logging.basicConfig(
    level=logging.INFO,                    # oder DEBUG
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


kg = load_neo4j()
pid = "PDEMO1"
patient_text = "Sono: Aszites im Abdomen; Kein CT" # . CT Abdomen liegt vor" # unilokuläre Zyste.

res = start_inference(kg, pid, patient_text)
print(res)
