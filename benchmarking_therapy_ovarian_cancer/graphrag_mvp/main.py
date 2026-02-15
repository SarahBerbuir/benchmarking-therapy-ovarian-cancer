from pathlib import Path

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.inference import run_inference

import logging

from benchmarking_therapy_ovarian_cancer.graphrag_mvp.utils import load_neo4j, rebuild_graph

logging.basicConfig(
    level=logging.INFO,                    # oder DEBUG
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

pid = "PDEMO1"
patient_text = """ 
Anlass des heutigen Tumorboards:
Überweisung vom Facharzt bei V.a. Ovarialkarzinom und auffälligem Ovarialbefund
Bildgebung:
CT: 2 größere Zysten, eine 6 cm messend. Die Andere 3,2 cm messend. Sediment am Boden hyperintens, erscheinen wie zwei mehrzeitig eingeblutete Ovarialzysten DD Endometriome, daneben reaktive KM-Aufnahmen. 
Gyn. Befund:
Spec: Portio und äußeres Genitale unauffällig.
VU: Scheidenwände glatt, kein Portioschiebe- oder Lüftungschmerz. Sono: großer solider Tumor. Reichlich Aszites. V. a. peritonealen Befall.
Labor: CEA und CA125 noch ausstehend
Anamnese:
0G/0P, Menstruation regelmäßig, PAP-Abstrich unauffällig, Voroperation: LSK mit Adnektomie bei Stieldrehung rechts, partielle Thyreoidektomie, sonst keine Vorerkrankungen, keine Allergien. 
Aktuell: Druck im Unterbauch links seit 6 Monaten. Im extern durchgeführten MRT zeigt sich der V.a. ein Ovarialkarzinom. Es besteht Gewichtsverlust von 8 kg in 8 Monaten. Sonst keine Auffälligkeiten. 
"""

kg = rebuild_graph()
res = run_inference(kg, pid, patient_text)

# Testfälle
# "High-grade seröses Karzinom des Corpus uteri (ED 01/23) pT3b pNX pM1 (PER) G3 R1 (klinisch R2) L1 V1 Pn0 FIGO IVB MMRp/MSS und p53-abn"
# "Laparotomie erfolgreich und histologie maligne. high grade"
# "Aszites prämenopausal"
# "Adjuvante Therapie abgeschlossen mit Carboplatin 6x. Laparotomie mit low grade Ovarialkarzinom FIGO III"
# "Adjuvante Therapie abgeschlossen mit Carboplatin 6x. Laparotomie mit high grade Ovarialkarzinom FIGO III"
# "CT durchgeführt FIGO IA"
# "postmenopausal Sono: unilokuläre Zyste, keine soliden Anteile <7mm, Schallschatten vorhanden, glatte multilokuläre Struktur <10 cm, kein starker Dopplerfluss. Kein Aszites. Kein CT vorhanden."
# "CT FIGO IIC debulking nicht möglich"
# "Adjuvante Therapie abgeschlossen mit Carboplatin 6x. gBRCA-. sBRCA- sHRD-. Laparotomie mit low grade Ovarialkarzinom FIGO III"
# "Adjuvante Therapie abgeschlossen mit Carboplatin 6x. gBRCA-. sBRCA- sHRD-. Laparotomie mit high grade Ovarialkarzinom FIGO III"
# "Neodjuvante Therapie abgeschlossen mit Carboplatin 6x. gBRCA-. sBRCA- sHRD-. Laparoskopie mit high grade Ovarialkarzinom FIGO III"
# "Carboplatin adjuvante Therapie abgeschlossen. 6 Zyklen"
# "Sono: unilokuläre Zyste, keine soliden Anteile <7mm, Schallschatten vorhanden, glatte multilokuläre Struktur <10 cm, kein starker Dopplerfluss. Kein Aszites. Kein CT vorhanden. Zystenausschälung ist gemacht worden und seine histologie wahrscheinlich benign"
# "Keine Sonographie. Kein CT. Keine OP. Keine Verlaufskontrolle."
# "Laparotomie mit low grade Ovarialkarzinom FIGO III"+
# "CT Thorax/Abdomen vorliegend, klinisch FIGO IIIA. Laparoskopie mit anschließender Laparotomie, Histologie maligne, Grading high, FIGO pathologisch IIIB. Adjuvante Systemtherapie (Carboplatin 6×) komplett verabreicht; kein Protokollwechsel. Aktuell Nachsorge geplant."
#  "CT Thorax/Abdomen vorliegend, klinisch FIGO IIIA. gBRCA +. Laparoskopie mit anschließender Laparotomie, Histologie maligne, Grading high, FIGO pathologisch IIIB. Adjuvante Systemtherapie (Carboplatin 6×) komplett verabreicht; kein Protokollwechsel. Aktuell Nachsorge geplant."
# """
# Gyn. Befund:
# Spec: Portio und äußeres Genitale unauffällig.
# VU: Scheidenwände glatt, kein Portioschiebe- oder Lüftungschmerz. Sono: großer solider Tumor. Reichlich Aszites. V. a. peritonealen Befall.
# Labor: CEA und CA125 noch ausstehend
# """

# """
# Prämenopausal. Virgo intacta, Palpatorisch unauffällig, Sono anal: Uterus ante, 8x3,6 cm unauffällig, Endometrium flach, keine Frei Flüssigkeit. Ovar links mit Zyste 6,5x6 cm a.e. Endometriom. Keine verstärkte Durchblutung.
# """
