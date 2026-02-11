from typing import Any, Sequence

# TODO I, II und so weg
FIGO_I = ["IA", "IB", "IC1", "IC2", "IC3"]
FIGO_II = ["IIA", "IIB", "IIC"]
FIGO_III = ["IIIA", "IIIA1", "IIIA2", "IIIB", "IIIC"]
FIGO_IV = ["IVA", "IVB"]
FIGO_STAGES: Sequence[str] = FIGO_I + FIGO_II + FIGO_III + FIGO_IV

FACT_SCHEMA = {
    "B1_unilokulaer": {
        "role": "input", "type": "bool3",
        "title": "Unilokuläre Zyste",
        "definition": "Unilokuläre (einkammerige) Zyste ohne Septen in der Sonographie. TRUE bei klarer Nennung ('unilokulär', 'einkammerig'); FALSE bei multilokulär/komplex; UNKNOWN wenn nicht beschrieben.",
        "pos_examples": ["unilokulär"],
        "neg_examples": ["nicht unilokulär", "multilokulär"],
        "producer": ["llm"],
    },
    "B2_solide_lt7mm": {
        "role": "input", "type": "bool3",
        "title": "Solide Komponenten < 7mm",
        "definition": "Solide Komponente innerhalb der Läsion mit maximalem Durchmesser < 7 mm. TRUE bei < 7 mm. Gemessen bei Sonografie. FALSE bei ≥ 7 mm oder 'keine solide Komponente'; UNKNOWN wenn Größe nicht angegeben.",
        "producer": ["llm"],
    },
    "B3_schallschatten": {
        "role": "input", "type": "bool3",
        "title": "Schallschatten",
        "definition": "Hinter dem Tumor liegender Schallschatten in der Sonographie. TRUE bei explizitem Nachweis; FALSE bei expliziter Negation; UNKNOWN wenn unklar.",
        "producer": ["llm"],
    },
    "B4_glatt_multilok_lt10cm": {
        "role": "input", "type": "bool3",
        "title": "Glatt, multilokulär, <10 cm",
        "definition": "Glatt begrenzte, multilokuläre Zyste mit Maximaldurchmesser < 10 cm. Gemessen bei Sonografie. TRUE nur wenn alle Kriterien erfüllt; sonst FALSE; UNKNOWN wenn Angaben fehlen.",
        "producer": ["llm"],
    },
    "B5_keine_doppler_flow": {
        "role": "input", "type": "bool3",
        "title": "Kein Blutfluss",
        "definition": "Kein Blutfluss in der farbkodierten Duplexsonographie (Farbdopplerscore 1). TRUE bei kein Fluss; FALSE bei Score ≥ 2 oder bei Blutfluss in der farbkodierten Duplexsonografie; UNKNOWN wenn nicht erhoben.",
        "producer": ["llm"],
    },
    "M1_unreg_solid": {
        "role": "input", "type": "bool3",
        "title": "Unregelmäßiger solider Tumor",
        "definition": "Unregelmäßiger solider Tumor in der Sonographie (irreguläre Konturen/inhomogen). TRUE bei Nennung; FALSE bei klar regulär/nicht-solide; UNKNOWN wenn nicht dokumentiert.",
        "producer": ["llm"],
    },
    "M2_ascites": {
        "role": "input", "type": "bool3",
        "title": "Aszites",
        "definition": "Freie Flüssigkeit/Aszites über physiologische Mengen hinaus. Gemessen bei Sonografie. TRUE bei Nennung; FALSE bei expliziter Verneinung; UNKNOWN wenn nicht erwähnt.",
        "pos_examples": ["Aszites vorhanden", "moderater Aszites", "free fluid/ascites"],
        "neg_examples": ["kein Aszites", "kein Nachweis von Aszites", "no ascites"],
        "producer": ["llm"],
    },
    "M3_ge4_papillae": {
        "role": "input", "type": "bool3",
        "title": "Mindestens vier papilläre Strukturen",
        "definition": "(Mindestens) ≥4 papilläre Projektionen bzw. Strukturen in die Zystenhöhle. Gemessen bei Sonografie. TRUE bei ≥4; FALSE bei <4 oder 'keine Papillen'; UNKNOWN wenn nicht quantifiziert.",
        "producer": ["llm"],
    },
    "M4_unreg_multilok_solid_gt10cm": {
        "role": "input", "type": "bool3",
        "title": "Unregelmäßiger multilokulärer solider Tumor ≥ 10 cm",
        "definition": "Multilokulär-solider Tumor mit unregelmäßiger Morphologie und Maximaldurchmesser ≥ 10 cm. Gemessen bei Sonografie. TRUE wenn beides zutrifft; sonst FALSE; UNKNOWN wenn Größe/Morphologie fehlen.",
        "producer": ["llm"],
    },
    "M5_hoher_doppler_flow": {
        "role": "input", "type": "bool3",
        "title": "Sehr starker Blutfluss",
        "definition": "Sehr starker Blutfluss in der Farbdoppler-Sonographie (Score 4). TRUE bei starker Perfusion; FALSE bei explizit genannten niedrig/kein Fluss; UNKNOWN wenn keine Angabe.",
        "producer": ["llm"],
    },
    "praemenopausal": {
        "role": "input",
        "type": "bool2",
        "title": "Prämenopausal",
        "definition": "Menstruationsstatus prämenopausal (regelmäßige Blutungen oder dokumentiert prämenopausal). FALSE bei Postmenopause (Amenorrhoe ≥12 Monate, bilaterale Oophorektomie oder explizit postmenopausal)",
        "producer": ["llm"],
    },
    "symptoms_present": {
        "role": "input", "type": "bool2",
        "title": "Symptome vorhanden",
        "definition": "Beschwerden im Zusammenhang mit der Adnexläsion (z. B. Unterbauchschmerz, Druckgefühl, Blähbauch, Blutungsstörung, akutes Abdomen). TRUE bei dokumentierten Symptomen; FALSE wenn explizit asymptomatisch oder keine Hinweise",
        "producer": ["llm"],
    },
    "growth": {
        "role": "input", "type": "bool2",
        "title": "Größenzunahme",
        "definition": "Zunahme der Läsionsgröße im zeitlichen Verlauf (Serienbildgebung/Verlauf). TRUE bei dokumentiertem Wachstum; FALSE sonst. Falls unklar/nicht erwähnt: FALSE.",
        "producer": ["llm"],
    },
    "persistence": {
        "role": "input", "type": "bool2",
        "title": "Persistenz",
        "definition": "Persistenz der Läsion über einen längeren Beobachtungszeitraum (typisch >6–12 Wochen). TRUE bei dokumentierter Persistenz; FALSE sonst. Falls nicht erwähnt: FALSE.",
        "producer": ["llm"],
    },
    "complex_multiloculaer": {
        "role": "input", "type": "bool2",
        "title": "Komplex multilokulär",
        "definition": "Komplexe, multilokuläre Läsion (Septen/heterogener Inhalt). TRUE bei Nennung von 'komplex' und/oder 'multilokulär'; FALSE sonst. Falls nicht erwähnt: FALSE.",
        "producer": ["llm"],
    },
    "psychic_unsure": {
        "role": "input", "type": "bool2",
        "title": "Psychische Unsicherheit",
        "definition": "Dokumentierte Unsicherheit/Angst/Entscheidungsschwierigkeit der Patientin, die die Therapieentscheidung beeinflusst (z. B. expliziter OP-Wunsch aus Sorge). TRUE bei Erwähnung; sonst FALSE (auch wenn nicht erwähnt).",
        "producer": ["llm"],
    },
    "ca125_u_ml": {
        "role": "input", "type": "number",
        "title": "CA125 (U/ml)",
        "definition": "Numerischer CA-125-Wert (U/ml), möglichst prätherapeutisch und am Entscheidungszeitpunkt. Bei mehreren Werten den aktuellsten vor Therapie wählen. Wenn kein Wert dokumentiert: -1.",
        "pos_examples": ["CA-125 38", "Ca125: 8,1"],
        "neg_examples": ["kein CA-125 bestimmt"],
        "producer": ["llm"],
    },
    "size_cm": {
        "role": "input",
        "type": "number",
        "title": "Größe (cm)",
        "definition": "Maximaldurchmesser der Läsion in Zentimetern (Bildgebung/OP). Bei mehreren Maßangaben den größten Einzeldurchmesser verwenden. Wenn in mm dann in cm umrechnen. Wenn nicht berichtet: -1.",
        "pos_examples": ["Größe 8,5 cm", "Durchmesser ca. 6 cm", "ca. 8-9cm", "20x50 mm"],
        "producer": ["llm"],
    },
    "cyst_bd": {
        "role": "output", "type": "enum",
        "allowed": ["BD1", "BD2", "BD3", "BD4", "unknown"],
        "definition": (
            "" # TODO
        ),
        "producer": ["bd_classification"],
    },
    "figo_clinical": {
        "role": "input", "type": "enum",
        "title": "FIGO clinical",
        "allowed": FIGO_STAGES + ["unknown"],
        # TODO#  TODO TNM Tabelle
        "definition": "Klinisches FIGO-Stadium basierend auf Anamnese, Untersuchung und Bildgebung. Gib genau einen Wert aus FIGO_STAGES zurück. Bei Mehrfachnennung das höchste Stadium wählen. UNKNOWN, wenn kein Stadium dokumentiert.",
        "producer": ["llm"],
    },
    "figo_path_laparotomy": {
        "role": "input", "type": "enum",
        "title": "FIGO pathologisch (Laparotomie)",
        # TODO TNM Tabelle
        "definition": "Pathologisches FIGO-Stadium aus dem Laparotomie-Präparat. Wert aus FIGO_STAGES (höchstes bei Mehrfachnennung). UNKNOWN, wenn nicht angegeben oder Befund benign.",
        "allowed": FIGO_STAGES + ["unknown"],
        "producer": ["llm"],
    },
    "figo_path_laparoscopy": {
        "role": "input", "type": "enum",
        "title": "FIGO pathologisch (Laparoskopie)",
        # TODO TNM Tabelle
        "definition": "Pathologisches FIGO-Stadium aus Laparoskopie/Minilaparotomie. Wert aus FIGO_STAGES (höchstes bei Mehrfachnennung). UNKNOWN, wenn nicht angegeben oder Befund benign.",
        "allowed": FIGO_STAGES + ["unknown"],
        "producer": ["llm"],
    },
    "grade_laparotomy": {
        "role": "input",
        "type": "enum",
        "title": "Grading (Laparotomie)",
        "definition": "Histologisches Grading Nach Laparotomie (nur diese OP berücksichtigen). Mappe: G1 → 'low'; G2/G3 oder 'high-grade' → 'high'. UNKNOWN, wenn nicht angegeben.",
        "allowed": ["low", "high", "unknown"],
        "producer": ["llm"],
    },
    "histology_laparotomy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Laparotomie)",
          "definition": (
                "ZIEL: Endgültige Gesamt-Histologie **aus dem Laparotomie-Präparat**.\n"
                "RÜCKGABE: 'maligne' | 'benigne' | 'unknown'.\n\n"
            
                "PRIORISIERTE QUELLEN (in dieser Reihenfolge auswerten):\n"
                "  (1) Pathologie/Histologie mit explizitem Laparotomie-Bezug "
                "      (z. B. 'Histologie nach Laparotomie', 'Laparotomiepräparat').\n"
                "  (2) OP-Bericht/TB-Anlass mit klarem Laparotomie-Bezug und histologischer Aussage.\n"
                "  (3) **Fallback**: Wenn imText **Laparotomie durchgeführt** (auch LSK->Laporotomie dann gilt dass eine Laparotomie gemacht wurde"
                "      und im Text genau **eine** globale Histologie ohne OP-Spezifikation genannt ist, "
                "      diese übernehmen.\n\n"
            
                "AUSSCHLUSS / ABGRENZUNG:\n"
                "  • Befunde anderer Eingriffe (Laparoskopie/Minilaparotomie, Zystektomie, Adnektomie, "
                "    Biopsie/Punktion) **nicht** verwenden, wenn zugleich ein Laparotomie-Befund existiert.\n"
                "  • Reine Verdachts-/Planungsangaben oder bildgebungsbasierte Formulierungen ohne "
                "    Pathologie zählen nicht.\n\n"
            
                "MAPPING DER FORMULIERUNGEN:\n"
                "  → 'maligne' bei Wahrscheinlichkeit auf Malignität (muss nicht komplett explizit aufgeführt sein auch interpretieren): "
                "     'Ovarialkarzinom', 'Karzinom', 'high-grade', 'HGSC', 'invasiv', "
                "     'vereinbar mit Karzinom', 'malign', 'borderline/low malignant potential'.\n"
                "  → 'benigne' bei klarer Gutartigkeit: 'kein Anhalt für Malignität', 'benigne Zyste', "
                "     'Endometriom', 'z. n. benigner Befund'.\n"
                "  → 'unknown', wenn keine eindeutige Zuordnung **mit (1)–(3)** möglich.\n\n"
            
                "TIE-BREAKER:\n"
                "  • Wenn mehrere Laparotomie-bezogene Aussagen vorhanden sind, nimm die "
                "    **zuletzt datierte** bzw. die **endgültige** Pathologie.\n"
                "  • Bei gleichzeitiger Laparoskopie- und Laparotomie-Histologie hat **Laparotomie Vorrang**."
              ),
        "allowed": ["benigne", "maligne", "unknown"],
        "producer": ["llm"],
    },
    "grade_laparoscopy": {
        "role": "input", "type": "enum",
        "title": "Grading (Laparoskopie)",
        "definition": "Histologisches Grading Nach Laparoskopie (nur diese OP berücksichtigen). Mappe: G1 → 'low'; G2/G3 oder 'high-grade' → 'high'. UNKNOWN, wenn nicht angegeben.",
        "allowed": ["low", "high", "unknown"],
        "producer": ["llm"],
    },
    "histology_laparoscopy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Laparoskopie)",
        "definition": "Gesamthistologie nach Laparoskopie (nur diese OP berücksichtigen). 'benigne' vs. 'maligne' gemäß Pathologie. 'maligne' bei eindeutiger oder hochwahrscheinlicher Malignität (z. B. 'Ovarialkarzinom', 'high-grade', 'vereinbar mit Karzinom'); 'benigne' bei klarer Gutartigkeit (z. B. 'kein Anhalt für Malignität'); 'unknown', wenn keine Zuordnung möglich oder keine Histologie dokumentiert ist.",
        "allowed": ["benigne", "maligne", "unknown"],
        "producer": ["llm"],
    },
    "histology_cystectomy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Zystektomie)",
        "definition": "Gesamthistologie nach Zystektomie/Zystenausschälung (nur diese OP berücksichtigen). 'benigne' vs. 'maligne' gemäß Pathologie. 'maligne' bei eindeutiger oder hochwahrscheinlicher Malignität (z. B. 'Ovarialkarzinom', 'high-grade', 'vereinbar mit Karzinom'); 'benigne' bei klarer Gutartigkeit (z. B. 'kein Anhalt für Malignität'); 'unknown', wenn keine Zuordnung möglich oder keine Histologie dokumentiert ist.",
        "allowed": ["benigne", "maligne", "unknown"],
        "producer": ["llm"],
    },
    "histology_adnexectomy": {
        "role": "input", "type": "enum",
        "title": "Histologie (Adnektomie)",
        "definition": "Gesamthistologie nach Adnektomie (nur diese OP berücksichtigen). 'benigne' vs. 'maligne' gemäß Pathologie. 'maligne' bei eindeutiger oder hochwahrscheinlicher Malignität (z. B. 'Ovarialkarzinom', 'high-grade', 'vereinbar mit Karzinom'); 'benigne' bei klarer Gutartigkeit (z. B. 'kein Anhalt für Malignität'); 'unknown', wenn keine Zuordnung möglich oder keine Histologie dokumentiert ist.",
        "allowed": ["benigne", "maligne",  "unknown"],
        "producer": ["llm"],
    },
    "gBRCA1/2": {
        "role": "input", "type": "enum",
        "title": "gBRCA1/2",
        "definition": (
            "Keimbahn-BRCA1/2 (≙ gBRCA, germline BRCA). "
            "Nur KEIMBAHN-Befund erfassen (somatische/tumorale BRCA = sBRCA NICHT übernehmen). "
            "Normalisierung: Groß/Kleinschreibung, Leerzeichen und Satzzeichen (.,;:) ignorieren. "
            "Akzeptiere Kurzformen wie 'gBRCA+', 'gBRCA-', 'gBRCA  +', 'gBRCA : -', sowie deutsch/englische Worte: "
            "'positiv', 'negativ', 'pathogen', 'likely pathogenic', 'wildtyp/wild-type', 'keine Mutation'. "
            "'VUS' oder 'unklar' ⇒ '-' (nicht pathogen). "
            "Wenn nur 'BRCA' ohne Präfix erwähnt wird, übernimm NUR als gBRCA, wenn im gleichen Satz explizit "
            "Keimbahn/Germline steht (z. B. 'Keimbahn-BRCA negativ'). " # TODO
            "Ausgabe: '+' bei pathogen/likely pathogenic; '-' bei negativ/wildtyp/VUS; "
            "'unknown' wenn kein Keimbahn-Befund erkennbar."
        ),
        "definition": "Keimbahn-BRCA1/2-Ergebnis oder aucg gBRCA genannt: '+' bei pathogen/likely pathogenic; '-' bei negativ oder VUS ohne klare Pathogenität.",
        "allowed": ["+", "-", "unknown"],
        "producer": ["llm"],
    },
    "sBRCA1/2": {
        "role": "input", "type": "enum",
        "title": "sBRCA1/2",
        "definition": "Somatisches BRCA1/2 im Tumor. Somatisch (als sBRCA gespeichert): '+' bei pathogen/likely pathogenic; '-' bei negativ/VUS ohne klare Pathogenität.",
        "allowed": ["+", "-",  "unknown"],
        "producer": ["llm"],
    },
    "sHRD": {
        "role": "input", "type": "enum",
        "title": "sHRD",
        "definition": "Tumor-HRD-Status gemäß Assay/Score. Somatisch (als sHRD gespeichert): '+' bei HRD-positiv (z. B. genomischer Scar über Schwelle, BRCA-pathogen); '-' bei HRD-negativ.",
        "allowed": ["+", "-",  "unknown"],
        "producer": ["llm"],
    },
    "strategy_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Strategie (Adjuvant)",
        "definition": (
            "EXTRAHIERE NUR ADJUVANT TATSÄCHLICH VERABREICHTE REGIME (nicht geplant/erwogen). Nach einer Laparotomie. "
            "Ordne anhand der im Text dokumentierten Gaben zu. Hinweise wie 'erhielt', 'gab', "
            "'Zyklus', 'C1/2/3', 'Therapie begonnen/fortgeführt' zählen als Verabreichung. "
            "Nur präoperative (adjuvante) Gaben berücksichtigen; neoadjuvante oder Erhaltungshinweise ignorieren. "
            "Suffix '_6x' bezeichnet die typische 6-Zyklen-ADJUVANZ; die exakte Zykluszahl muss im Text NICHT stehen. "
              "Synonyme/Notation: 'Carboplatin/Paclitaxel', 'Carbo+Ptx', 'Carboplatin & Paclitaxel' → beide gemeinsam; "
              "'… und Bevacizumab' kennzeichnet zusätzliches Bevacizumab.\n"
              "Mapping:\n"
              "• 'carboplatin_6x' → wenn ausschließlich Carboplatin adjuvant gegeben wurde (KEIN Paclitaxel, KEIN Bevacizumab).\n"
              "• 'carboplatin_and_paclitaxel_6x' → wenn Carboplatin UND Paclitaxel adjuvant gemeinsam gegeben wurden (ohne Bevacizumab).\n"
              "• 'carboplatin_and_paclitaxel_and_bevacizumab_6x' → wenn Carboplatin UND Paclitaxel UND Bevacizumab adjuvant gemeinsam gegeben wurden.\n"
              "• 'op_only' → wenn ausdrücklich KEINE adjuvante Systemtherapie erfolgte (nur OP). Aber trotzdem eben eine adjuvante Therapie genannt wird. \n" # TODO
              "Gib 'unknown' zurück, wenn keine eindeutige adjuvante Gabe dokumentiert ist oder nur Pläne/Optionen ohne tatsächliche Verabreichung genannt sind."
        ),
        "allowed": [
            "op_only",
            "carboplatin_6x",
            "carboplatin_and_paclitaxel_6x",
            # TODO Klärung Begriff
            "carboplatin_and_paclitaxel_and_bevacizumab_6x",
            "unknown"
        ],
        "producer": ["llm"],  # Step-Output
    },
    "strategy_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Strategie (Neoadjuvant)",
        "definition": (
            "EXTRAHIERE NUR NEOADJUVANT TATSÄCHLICH VERABREICHTE REGIME (nicht geplant/erwogen). Nach einer Laparoskopie oder MINIlaparotomie. "
            "Ordne anhand der im Text dokumentierten Gaben zu. Hinweise wie 'erhielt', 'gab', "
            "'Zyklus', 'C1/2/3', 'Therapie begonnen/fortgeführt' zählen als Verabreichung. "
            "Nur präoperative (neoadjuvante) Gaben berücksichtigen; adjuvante oder Erhaltungshinweise ignorieren. "
            "Suffix '_3x' bezeichnet die typische 3-Zyklen-NEOADJUVANZ; die exakte Zykluszahl muss im Text NICHT stehen. "
              "Synonyme/Notation: 'Carboplatin/Paclitaxel', 'Carbo+Ptx', 'Carboplatin & Paclitaxel' → beide gemeinsam; "
              "'… und Bevacizumab' kennzeichnet zusätzliches Bevacizumab.\n"
              "Mapping:\n"
              "• 'carboplatin_3x' → wenn ausschließlich Carboplatin neoadjuvant gegeben wurde (KEIN Paclitaxel, KEIN Bevacizumab).\n"
              "• 'carboplatin_and_paclitaxel_3x' → wenn Carboplatin UND Paclitaxel neoadjuvant gemeinsam gegeben wurden (ohne Bevacizumab).\n"
              "• 'carboplatin_and_paclitaxel_and_bevacizumab_3x' → wenn Carboplatin UND Paclitaxel UND Bevacizumab neoadjuvant gemeinsam gegeben wurden.\n"
              "• 'op_only' → wenn ausdrücklich KEINE neoadjuvante Systemtherapie erfolgte (nur OP). Aber trotzdem eben eine neoadjuvante Therapie genannt wird. \n" # TODO
              "Gib 'unknown' zurück, wenn keine eindeutige neoadjuvante Gabe dokumentiert ist oder nur Pläne/Optionen ohne tatsächliche Verabreichung genannt sind."
        ),
        "allowed": [
            "op_only",
            "carboplatin_3x",
            "carboplatin_and_paclitaxel_3x",
            "carboplatin_and_paclitaxel_and_bevacizumab_3x",
            "unknown"
        ],
        "producer": ["llm"],  # Step-Output
    },
    "strategy_maintenance": {
        "role": "output", "type": "enum",
        "title": "Strategie (Erhaltung)",
        "definition": (
            "Gib die **explizit dokumentierte Erhaltungs-Strategie** wieder (keine Ableitung). "
            "Token: 'bevac' = Bevacizumab, 'olap' = Olaparib, 'nirap' = Niraparib, 'bevacolap' = **Kombination** Bevacizumab+Olaparib.\n\n"
            "Mapping-Regeln (deterministisch):\n"
            "  • **Nur Olaparib erwähnt/ggegeben** → `bevacolap_olap_bevac_nirap` (enthält 'olap').\n"
            "  • **Nur Bevacizumab ODER nur Niraparib** (ohne Olaparib, ohne Kombi) → `bevac_nirap`.\n"
            "  • **Bevacizumab+Olaparib Kombination** explizit (ohne Olaparib-Monotherapie als Option) → `bevacolap_bevac_nirap`.\n"
            "  • Wenn sowohl Kombination **und** Olaparib-Monotherapie als Optionen genannt sind → `bevacolap_olap_bevac_nirap`.\n"
            "  • Wenn nichts Eindeutiges zur Erhaltung steht → `unknown`.\n\n"
            "Qualifikatoren:\n"
            "  • Nur als Maintenance werten, wenn Erhaltungs-Kontext klar ist ('Erhaltung', 'maintenance', nach Abschluss der Induktion/Systemtherapie). "
            "  • Nenne **keine** Neo-/Adjuvanz als Maintenance-Strategie."
            "Gib 'unknown' zurück, wenn keine Erhaltungsstrategie/Optionen dokumentiert sind."
),
        "allowed": [
        "bevacolap_olap_bevac_nirap",
        "bevacolap_bevac_nirap",
        "bevac_nirap",
        "unknown"
        ],
        "producer": ["llm"],
    },


    # --- Evidence ---
    "ev_sonography_present": {
        "role": "evidence", "type": "bool2",
        "title": "Sonographie in Akte vorhanden",
        "definition": (
            "EVIDENZ, dass eine gynäkologische Sonographie durchgeführt und im Text dokumentiert wurde. "
            "AUSWERTUNGS-SCOPE: Keine Inhalte der Spalten 'Histologie'/'Pathologie'/'Bildgebung' miteinbeziehen "
            "andere Abschnitte (CT/MRT/Befunde/Labor) ignorieren. "
            "TRUE, wenn mindestens einer der folgenden Hinweise vorliegt: "
            "(1) explizite Nennung einer Sonographie (z. B. 'Sonographie', 'US', 'Sono', 'Ultraschall', 'TVUS', 'transvaginaler Ultraschall'); "
            "(2) dokumentierte IOTA-Merkmale (B- oder M-Kriterien, z. B. B1–B5, M1–M5); "
            "(3) typische sonographische Befundsprache (z. B. 'multilokulär', 'Papillen', 'Dopplerfluss', 'Aszites' im Sono-Kontext) "
            "oder ovarielle Messangaben (Durchmesser/Läsionsgröße) mit eindeutigem Sono-Bezug. "
            "FALSE, wenn in 'Körperliche Untersuchung' kein solcher Hinweis steht. "
            "Hinweis: Reine CT-/MRT-Formulierungen oder Laborwerte gelten nicht als Sonographie-Evidenz."
            "Planung/Anforderung ohne Ergebnis zählt NICHT als TRUE."
        ),
        "producer": ["llm"],
    },
    "ev_ct_present": {
        "role": "evidence", "type": "bool2",
        "title": "CT-Befund in Akte vorhanden",
        "definition": (
            "EVIDENZ, dass ein CT Thorax/Abdomen (ggf. CT Abdomen/Becken) durchgeführt UND im Text dokumentiert wurde. Spalte 'Bildgebung' ist dafür am wichtigsten."
            "TRUE bei expliziter CT-Nennung (z. B. 'CT', 'CT Abdomen/Thorax', 'Kontrastmittel-CT') oder bei eindeutigem CT-Befundzitat."
            "MRI/Ultraschall/Laparoskopie NICHT mitzählen. Planung/Anforderung ohne Ergebnis zählt NICHT als TRUE."
        ),
        "producer": ["llm"],
    },
    "ev_cystectomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Zystenausschälung durchgeführt",
        "definition": (
            "EVIDENZ, dass eine Zystektomie (Zystenausschälung) TATSÄCHLICH durchgeführt und im Text dokumentiert wurde. "
            "AUSWERTUNGS-SCOPE: OP-Bericht, Pathologie/Histologie MIT eindeutigem Bezug auf Zystektomie. "
            "Nur Durchführung, KEINE Planung/Indikation. "
            "TRUE NUR wenn mindestens einer der folgenden starken Hinweise vorliegt: "
            "(1) Operationsformulierung: 'Zystektomie', 'Zystenausschälung', 'Zystenexstirpation', 'cystectomy' (inkl. 'Z.n./s/p Zystektomie'); "
            "(2) Pathologie ausdrücklich: 'Zystektomiepräparat', 'Zyste (Zystektomie)'. "
            "FALSE bei: reiner Adnektomie/Laparotomie/Debulking ohne Zystektomie-Bezug; adjuvante/neoadjuvante Therapieangaben; "
            "allgemeiner Ovarialkarzinom-/FIGO-/Grading-Text ohne OP-Bezug; bloße Planung/Anforderung. "
            "Bevorzugung: Falls sowohl Zystektomie als auch Adnektomie genannt werden, sind BEIDE separat nur dann TRUE, wenn jeweils explizit als durchgeführt dokumentiert." # TODO
        ),
        "producer": ["llm"],
    },
    "ev_adnexectomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Adnektomie durchgeführt",
        "definition": (
            "EVIDENZ, dass eine (ein- oder beidseitige) Adnektomie TATSÄCHLICH durchgeführt und dokumentiert wurde. "
            "AUSWERTUNGS-SCOPE: OP-Bericht, Pathologie/Histologie MIT eindeutigem Adnektomie-Bezug. "
            "TRUE NUR bei klaren Adnex-Tokens oder entsprechenden Pathologie-Bezeichnungen. "
            "ZULÄSSIGE FORMULIERUNGEN (Synonyme/Akronyme): "
            "'Adnektomie', 'Adnexektomie', 'Oophorektomie', 'Salpingo-Oophorektomie', 'SOE', "
            "'USO' (unilaterale Salpingo-Oophorektomie), 'BSO' (bilaterale …), 'TAH-BSO' (Hysterektomie + BSO), "
            "sowie 'Z.n./s/p Adnektomie/BSO/USO'. "
            "PATHOLOGIE-HINWEISE: 'Adnektomiepräparat', 'Ovar + Tube (Adnektomie)'. "
            "FALSE bei: allgemeiner Laparotomie/Debulking ohne Adnex-Tokens; reinem Karzinom-/FIGO-/Grading-Text; "
            "Chemo-Angaben (adjuvant/neoadjuvant); bloßer Planung/Indikation ohne Durchführung. "
            "WICHTIG: Das Wort 'Laparotomie' allein reicht NICHT; es ist nur der Zugang. Es muss eine Adnex-Entfernung explizit benannt sein."
        ),
        "producer": ["llm"],
    },
    "ev_laparotomy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Laparotomie durchgeführt",
        "definition": (
            "BEGRIFF: Laparotomie = offener operativer Zugang (Bauchschnitt); NICHT verwechseln mit Laparoskopie (LSK). "
            "KRITERIUM (TRUE/FALSE): TRUE, wenn eine Laparotomie als endgültiger operativer Zugang durchgeführt und dokumentiert wurde. "
            "Bei 'laparoskopisch begonnen, konvertiert zur Laparotomie' → TRUE (finaler Zugang offen). "
            "AUSWERTUNGS-SCOPE (Priorität nicht ausschließlich die folgenden Abschnitte in den Patientendaten): "
            "(1) 'Histologie/Pathologie', (2) 'Befund / Anlass des heutigen Tumorboards'. "
            "Histologie/Pathologie darf als Indiz dienen, WENN der offene Zugang explizit genannt ist "
            "(z. B. 'Laparotomiepräparat', 'offenes Debulking'). "
            "WICHTIG: Diese Evidence erfasst NUR den durchgeführten Zugang. Inhalte wie Histologie/FIGO werden separat extrahiert. "
            "FALSE bei reiner Planung/Indikation ohne Durchführung oder wenn ausschließlich eine Laparoskopie dokumentiert ist."
        ),
        "producer": ["llm"],
    },
    "ev_laparoscopy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Laparoskopie durchgeführt",
        "definition": (
            "BEGRIFF: Laparoskopie = minimal-invasiver Zugang (LSK), ggf. inkl. laparoskopisch-assistierter Minilaparotomie; "
            "NICHT verwechseln mit offener Laparotomie (Bauchschnitt). "
            "KRITERIUM (TRUE/FALSE): TRUE nur, wenn eine Laparoskopie als endgültiger operativer Zugang durchgeführt und dokumentiert wurde. "
            "Bei 'laparoskopisch begonnen, konvertiert zur Laparotomie' → FALSE (keine LSK als finaler Zugang). "
            "AUSWERTUNGS-SCOPE (Priorität nicht ausschließlich die folgenden Abschnitte in den Patientendaten): "
            "(1) 'Histologie/Pathologie', (2) 'Befund / Anlass des heutigen Tumorboards'. "
            "Histologie/Pathologie darf als Indiz dienen, WENN der laparoskopische Zugang explizit genannt ist "
            "(z. B. 'laparoskopische Adnektomie', 'Laparoskopiepräparat'). "
            "WICHTIG: Diese Evidence erfasst NUR den durchgeführten Zugang. Inhalte wie Histologie (benigne/maligne) oder FIGO "
            "werden separat über ihre Fakt-Keys extrahiert und sind keine Voraussetzung für TRUE. "
            "FALSE bei reiner Planung/Indikation ohne Durchführung oder wenn ausschließlich eine offene Laparotomie dokumentiert ist."
        ),
        "producer": ["llm"],
    },
    "ev_genetic_counseling_done": {
        "role": "evidence", "type": "bool2",
        "title": "Humangenetische Beratung durchgeführt",
        "definition": (
            "TRUE, wenn eine **Keimbahn-/humangenetische Beratung** tatsächlich stattgefunden hat "
        "oder der Keimbahn-Prozess klar dokumentiert ist (z. B. Beratung erfolgt, Einwilligung/Blutabnahme für Keimbahn-Test, "
        "oder **gBRCA**-Befund vorliegend/berichtete). "
        "Nur **Keimbahn** (gBRCA), **nicht** somatisch (sBRCA/HRD). "
        "FALSE bei reiner Planung/Überweisung ohne erfolgte Beratung oder bei ausschließlich somatischen Angaben."

        ),
        "producer": ["llm"],
    },
    "ev_hrd_test_done": {
        "role": "evidence", "type": "bool2",
        "title": "HRD-Test durchgeführt",
        "definition": (
        "EVIDENZ, dass ein HRD-bezogener Tumortest durchgeführt wurde UND ein BEFUND/ERGEBNIS vorliegt "
        "sHRD und sBRCA (1/2) Wert als +/- im Text zu finden. Bloße Testanmeldung/Planung ohne Befund NICHT mitzählen. "
        "TRUE bei dokumentierter Durchführung/Ergebnis; FALSE sonst."
    ),
        "producer": ["llm"],
    },
    "ev_neoadjuvant_therapy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Neoadjuvante Therapie durchgeführt",
        "definition": (
            "TRUE nur bei **präoperativer** systemischer Therapie (NACT) mit **explizitem neoadjuvant-Kontext** "
            "Typische NACT ≈ 3 Zyklen, die exakte Zykluszahl muss NICHT im Text stehen). "
            "Minimalkriterien (eines reicht):\n"
            "  • Wortlaut ähnlich wie 'neoadjuvant', 'NACT', 'präoperativ' + Gabe/Applikation (z. B. Carboplatin/Paclitaxel/Bevacizumab).\n"
            "  • Zyklenangaben (C1/C2/…) **vor** OP oder 'vor geplanter OP gegeben'.\n"
            "Ausschlüsse (dann FALSE):\n"
            "  • Adjuvant/postoperativ, Erhaltung/Maintenance, Planung/Indikation ohne Gabe, reine PARP-Erhaltung "
            "  • OP-only (keine systemische Gabe vor OP) ist TRUE wenn trotzdem explizit von neoadjuvant geredet wird."
            "(Olaparib/Niraparib) **ohne** expliziten neoadjuvanten Kontext.\n"
            "Hinweis: PARP-Inhibitoren sind i. d. R. Maintenance – **nur** als neoadjuvant zählen, wenn der Text das klar so benennt ('neoadjuvantes Olaparib')."
          ),
        "producer": ["llm"],
    },
    "ev_adjuvant_therapy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Adjuvante Therapie durchgeführt",
        "definition": (
            "TRUE nur bei **postoperativer** systemischer Therapie (adjuvant) mit **explizitem adjuvant-Kontext** "
            "Typische NACT ≈ 6 Zyklen, die exakte Zykluszahl muss NICHT im Text stehen. Minimalkriterien (eines reicht):\n"
            "  • Wortlaut ähnlich wie 'adjuvant', 'postoperativ' + Gabe/Applikation (z. B. Carboplatin/Paclitaxel/Bevacizumab).\n"
            "  • Zyklenangaben nach OP ('nach Laparotomie C1 begonnen', 'postoperativ C1/C2/…', 'vor geplanter OP gegeben).\n"
            "OP-only (keine systemische Gabe vor OP) ist TRUE wenn trotzdem explizit von adjuvant geredet wird. "
            "Nur präoperative (ADJUVANTE) Gaben zählen. Ausschlüsse (dann FALSE):\n"
            "  • Neoadjuvant/präoperativ, Erhaltung/Maintenance, Planung/Indikation ohne Gabe.\n"
            "  • Reine PARP-Erhaltung (Olaparib/Niraparib) zählt **nicht** als adjuvant, außer der Text benennt es ausdrücklich als adjuvante Gabe (ungewöhnlich)."
        ),
        "producer": ["llm"],
    },
    "ev_interim_restaging_3_done": {
        "role": "evidence", "type": "bool2",
        "title": "Interim Restaging (Zyklus 3) durchgeführt",
        "definition": (
        "EVIDENZ, dass nach ~3 Zyklen neoadjuvanter Therapie ein Interims-Restaging durchgeführt wurde. "
        "Reevaluation nach 3 Zyklen, CT Thorax wurde erneut durchgeführt, der CA-125-Verlauf wurde erneut gemessen"
        "und es wurde ein erneutes Operabilität Assessment durchgeführt"
        "Dieser Schritt kommt wenn die neoadjuvante Therapie mit 3 Zyklen durchlaufen wurde. "
        "Vor allem geht es darum dass nun nach dem Start der neoadjuvanten Therapie geprüft wird, ob nun operiert werden kann. "
        "AUSWERTUNGS-SCOPE (Priorität): CT Thorax/Abdomen (oder gleichwertige Bildgebung), CA-125-Verlauf, "
        "und/oder dokumentierte Operabilitätsbewertung EXPLIZIT im Kontext 'nach C3'/'Interim/Restaging'. "
        "TRUE, wenn eine dieser Maßnahmen als tatsächlich durchgeführt und zeitlich C3-bezogen dokumentiert ist. "
        "FALSE bei bloßer Planung ('vorgesehen'), ausstehendem Termin oder postoperativem Restaging ohne Bezug zu C3."
        ),
        "producer": ["llm"],
    },
    "ev_chemo_protocol_switch_completion_done": {
        "role": "evidence", "type": "bool2",
        "title": "Wechsel/Komp.-Chemotherapie durchgeführt",
        "definition": (
        "EVIDENZ, dass NACH der C3-Interim-Reevaluation, da nach der neoadjuvanten Therapie der Tumor Debulking nicht möglich war."
        "(a) ein Protokollwechsel tatsächlich erfolgt ist (z. B. Wechsel des Regimes) UND (b) die Chemotherapie bis zur "
        "vorgesehenen Komplettierung (vermutlich 3 Zyklen) fortgesetzt/abgeschlossen wurde "
        "(typisch weitere Zyklen C4–C6, ggf. mit unverändertem Regime). "
        "('Wechsel auf …', 'Komplettierung bis C6'), "
        "TRUE, wenn Wechsel und dokumentierte Fortführung mit real verabreichten zusätzlichen Zyklen vorliegt. "
        "FALSE bei bloßer Absicht/Planung ohne Gabe."
    ),
        "producer": ["llm"],
    },
    "ev_optimal_debulking_completion_done": {
        "role": "evidence", "type": "bool2",
        "title": "Optimales Debulking + Chemo abgeschlossen",
        "definition": (
            "TRUE **nur** im neoadjuvanten Setting, **wenn beide** Bedingungen **explizit** erfüllt und dokumentiert sind: "
            "(1) Operation mit *optimalem Debulking* (z. B. 'optimales Debulking', 'R0', 'complete/complete macroscopic cytoreduction'); "
            "(2) **Komplementierung** der Chemotherapie **nach** der OP (typisch die restlichen 3 Zyklen: 'C4–C6', 'weitere drei Zyklen', 'Komplementierung/Komplettierung abgeschlossen'), "
            "und insgesamt wird eine Sequenz 'C1–C3 neoadjuvant → OP → C4–C6' kenntlich. "
            "AUSWERTUNGS-SCOPE: Therapie-/OP-Dokumentation, Interims-Restaging, TB-Protokolle. "
            "FALSE, wenn: "
            "• rein **adjuvante** 6 Zyklen ohne vorherige neoadjuvante Gabe vorliegen; "
            "• OP nicht 'optimal' ist (kein R0/keine klare Optimal-Formulierung) **oder** die postoperativen Zyklen nicht als *Komplementierung* eindeutig abgeschlossen sind; "
            "• nur Planung/Intention ohne Durchführung; "
            "• unklar, ob die präoperativen Zyklen tatsächlich vor der OP gegeben wurden. "
            "Beispiele TRUE: 'nach 3× neoadjuvant OP mit R0, anschließend C4–C6 komplettiert', 'Optimales Debulking, Komplementierung abgeschlossen (C4–C6)'. "
            "Beispiele FALSE: 'adjuvante Chemotherapie 6× abgeschlossen', 'OP mit Resttumor, weitere Chemo geplant', 'nur OP, keine Komplementierung', 'Formulierung unklar/ohne Sequenz C1–C3 → OP → C4–C6'."
        ),
    "producer": ["llm"],
    },
    "ev_maintenance_therapy_done": {
        "role": "evidence", "type": "bool2",
        "title": "Erhaltungstherapie durchgeführt",
        "definition": (
        "EVIDENZ, dass eine Erhaltungstherapie tatsächlich verabreicht wurde "
        "(z. B. Niraparib, Bevacizumab, Olaparib oder Kombinationen). "
        "TRUE bei dokumentierter Verabreichung; "
        "FALSE bei reiner Planung/Option ohne tatsächliche Gabe."
    ),
        "producer": ["llm"],
    },
    # --- Evaluator-Output  ---
    # TODO Definitionen eventuell für verbalization
    "iota_res": {
        "role": "output", "type": "enum",
        "allowed": ["benigne_wahrscheinlich","maligne_wahrscheinlich","nicht_klassifizierbar"],
        "producer": ["iota_simple_rules"],
    },
    "op_plan": {
        "role": "output", "type": "enum",
        "allowed": ["no_op","Zystenausschälung","Adnektomie","unknown"], # TODO unknown ?
        "producer": ["set_op_plan"],
    },
    "figo_bucket": {
        "role": "output", "type": "enum",
        "allowed": ["early", "advanced"],
        "producer": ["set_figo_bucket"],
    },
    "debulking_possible": {
        "role": "output", "type": "bool3",
        "producer": ["set_debulking_possible"],
    },
    "plan_strategy_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Strategie (Adjuvant)",
        "definition": "TBD",
        "allowed": [
            "op_only",
            "carboplatin_optional_6x",
            "carboplatin_6x",
            "carboplatin_and_paclitaxel_6x",
            "carboplatin_and_paclitaxel_and_bevacizumab_6x",
        ],
        "producer": ["set_planning_adjuvant_therapy"],
    },
    "plan_next_step_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Next Step (Adjuvant)",
        "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_planning_adjuvant_therapy"],
    },
    "next_step_adjuvant": {
        "role": "output", "type": "enum",
        "title": "Next Step (Adjuvant)", "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_adjuvant_next_step"],
    },
    "plan_strategy_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Strategie (Neoadjuvant)",
        "definition": "TBD",
        "allowed": [
            "op_only",
            "carboplatin_optional_3x",
            "carboplatin_3x",
            "carboplatin_and_paclitaxel_3x",
            "carboplatin_and_paclitaxel_and_bevacizumab_3x",
        ],
        "producer": ["set_planning_neoadjuvant_therapy"],
    },
    "plan_next_step_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Plan Next Step (Neoadjuvant)",
        "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_planning_neoadjuvant_therapy"],
    },
    "next_step_neoadjuvant": {
        "role": "output", "type": "enum",
        "title": "Next Step (Neoadjuvant)", "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_neoadjuvant_next_step"],
    },
    "next_step_system_therapy": {
        "role": "output", "type": "enum",
        "title": "Next Step (Systemtherapie)",
        "definition": "TBD",
        "allowed": ["Nachsorge", "Erhaltungstherapie"],
        "producer": ["set_next_step_therapy"],
    },
    "plan_strategy_maintenance": {
        "role": "output", "type": "enum",
        "title": "Plan Strategie (Erhaltung)", "definition": "TBD",
        "allowed": [
            "bevacolap_olap_bevac_nirap",
            "bevacolap_bevac_nirap",
            "bevac_nirap"
        ],

        "producer": ["set_maintenance_therapy"],
    },
    "hrd_status": {
        "role": "output", "type": "enum",
        "title": "HRD Status", "definition": "TBD",
        "allowed": ["+", "-"], "producer": ["set_hrd_brca_status"],
    },
    "brca_status": {
        "role": "output", "type": "enum",
        "title": "BRCA Status", "definition": "TBD",
        "allowed": ["+", "-"], "producer": ["set_hrd_brca_status"],
    },
}


def schema_for_bool2(key: str) -> dict:
    return {
        "type": "OBJECT",
        "properties": { key: { "type": "STRING", "enum": ["true","false"] } },
        "required": [key],
    }

def schema_for_bool3(key: str) -> dict:
    return {
        "type": "OBJECT",
        "properties": {
            key: {
                "type": "STRING",
                "enum": ["true", "false", "unknown"]
            }
        },
        "required": [key],
    }

def schema_for_enum(key: str, allowed: list[str]) -> dict:
    return {
        "type": "OBJECT",
        "properties": { key: { "type": "STRING", "enum": allowed } },
        "required": [key],
    }

def schema_for_number(key: str) -> dict:
    return {
        "type": "OBJECT",
        "properties": { key: { "type": "NUMBER" } },
        "required": [key],
    }

def schema_for_key(key: str) -> dict:
    spec = FACT_SCHEMA[key]
    t = spec["type"]
    if t == "bool2":
        return schema_for_bool2(key)
    if t == "bool3":
        return schema_for_bool3(key)
    if t == "enum":
        return schema_for_enum(key, spec.get("allowed", []))
    if t == "number":
        return schema_for_number(key)
    return {"type":"OBJECT","properties":{key:{"type":"STRING"}}, "required":[key]}

_TRUE  = {"true","wahr","ja","yes","1"}
_FALSE = {"false","falsch","nein","no","0"}
_UNK   = {"unknown","unk","na","n/a",""}


def validate_and_normalize(key: str, value: Any):
    if "route" in key.lower() or key == "parallel_starting" or key == "parallel_done":
        spec = None
        type_value = "bool2"
    else:
        spec = FACT_SCHEMA.get(key)
        if not spec:
            raise KeyError(f"Unknown FactKey: {key}")
        type_value = spec["type"]
    s = str(value).strip().lower() if value is not None else ""

    if type_value == "bool2":
        if s in _TRUE or value is True:  return True
        if s in _FALSE or value is False: return False
        return False

    if type_value == "bool3":
        if s in _TRUE or value is True:   return True
        if s in _FALSE or value is False: return False
        if s in _UNK:                     return "unknown"
        return "unknown"

    if type_value == "enum":
        allowed = set(spec.get("allowed", []))
        return value if isinstance(value, str) and value in allowed else "unknown"

    if type_value == "number":
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    return value
