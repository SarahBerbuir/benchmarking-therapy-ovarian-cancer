# Short, clinically meaningful one-line definitions per STEP and FACT to assist with subgraph verbalization
# Routing flags (route_*) are purely switches/gates – not independent measures.

from typing import Dict

definitions: Dict[str, Dict[str, str]] = {
    "steps": {
        # Basis & Diagnostic
        "Vorsorge/Symptome": "Erfassung von Anamnese/Symptomen als Ausgangspunkt.",
        "Gynäkologische Untersuchung & Sonographie": "Klinische Untersuchung und Ultraschallbefunde (IOTA-Basis).",
        "IOTA-Auswertung (Simple Rules)": "IOTA Simple Rules zur B/M-Einschätzung der Ovarialzyste.",
        "Zystenklassifikation (BD-Klassifikation)": "BD-Klassifikation zur Zysten-Einordnung für das OP-Planning.",
        "CT Thorax/Abdomen": "Staging-CT zur Erfassung von Ausbreitung (cFIGO).",
        "FIGO Bucketer": "Einordnung in frühes/fortgeschrittenes Stadium basierend auf cFIGO.",
        "Debulking Assessment": "Einschätzung, ob optimales Debulking primär/sekundär erreichbar ist.",
        "OP-Entscheider": "Entscheidung OP-Plan (keine OP / Zystektomie / Adnektomie).",
        "Verlaufskontrolle": "Kontrolltermin nach konservativem oder benignem Verlauf.",
        "Zystenausschälung": "Operative Zystektomie (Zystenausschälung).",
        "Adnektomie": "Ein-/beidseitige Adnektomie (Ovar +/- Tube).",

        # Resectability/Tumorboard
        "Beurteilung Resektabilität im Tumorboard": "Interdisziplinäre Einschätzung der Operabilität.",
        "Laparotomie, SS": "Primäre Laparotomie zur Tumorresektion/Probengewinnung.",
        "Laparotomie, Pathologie Auswertung": "Patho-Auswertung (Grad/FIGO path) nach Laparotomie.",
        "Laparoskopie oder Minilaparotomie": "Diagnostisch/therapeutische LSK/Minilaparotomie.",
        "Laparoskopie, Pathologie Auswertung": "Patho-Auswertung (Grad/FIGO path) nach LSK.",
        "Interdisziplinäres Tumorboard": "Therapieentscheidungen im Tumorboard.",

        # HRD / BRCA
        "Humangenetische Beratung (gBRCA)": "Genetische Beratung & Keimbahn-BRCA-Test.",
        "HRD Testung (sBRCA & sHRD)": "Tumor-basiertes HRD/sBRCA-Testing.",
        "HRD/BRCA Resolver": "Zusammenführung gBRCA/sBRCA/HRD → HRD/BRCA-Status.",

        # Neoadjuvant
        "Neoadjuvante Therapie Mapping": "Planung des neoadjuvanten Regimes und nächsten Schritts.",
        "Neoadjuvante Therapie": "Tatsächlich verabreichte neoadjuvante Systemtherapie.",
        "Next Step Mapping Neoadjuvant": "Bestimmung des nächsten Systemtherapie-Schritts nach NACT.",
        "Reevaluation nach 3 Zyklen, CT Thorax Abdomen, CA125, Operabilität Assessment":
            "Zwischenstaging (nach ~3 Zyklen) inkl. Operabilität.",
        "Wechsel Therapieprotokoll & Komplementierung Chemotherapie (3x)":
            "Switch/Completion der neoadjuvanten Chemo.",
        "Optimales Debulking & Komplementierung Chemotherapie (3x)":
            "OP mit optimalem Debulking + Chemo-Komplementierung.",
        "Wiederholung Debulking Assessment": "Erneute Operabilitätsprüfung nach neoadjuvanter Therapie/Interims-Staging.",
        "Therapie Reevaluation": "Gesamttherapie-Review nach Zwischenstaging/Protokollwechsel (Wirksamkeit, Toxizität, nächster Schritt).",

        # Adjuvant
        "Adjuvante Therapie Mapping": "Planung der adjuvanten Systemtherapie.",
        "Adjuvante Therapie": "Tatsächlich verabreichte adjuvante Systemtherapie.",
        "Next Step Mapping Adjuvant": "Bestimmung des nächsten Schritts nach Adjuvanz.",

        # Parallel & Maintenance
        "Parallel Join": "Synchronisations-Knoten für parallele Pfade: alle Gates müssen erfüllt sein (Systemtherapie abgeschlossen – adjuvant/neoadjuvant – UND humangenetische Beratung/HRD-BRCA-Resolver abgeschlossen). Nur dann geht es weiter zur Nachsorge oder Erhaltungstherapie.",
        "Erhaltungs Therapie Mapping": "Planung der Erhaltungstherapie (Optionen/Gates).",
        "Erhaltungs Therapie": "Durchgeführte Erhaltungstherapie.",
        "Nachsorge": "Regelmäßige Nachsorge/Follow-up nach abgeschlossener Systemtherapie oder nach Erhaltungstherapie.",


        # Routing
        "Route Verlaufskontrolle (Keine OP)": "Routing zur Verlaufskontrolle/Follow-up, wenn der OP-Plan 'keine Operation' (no_op) vorsieht.",
        "Route Verlaufskontrolle (Histologie Zystenausschälung benigne)": "Routing zur Verlaufskontrolle nach Zystektomie mit benigner Histologie.",
        "Route Verlaufskontrolle (Histologie Adnektomie benigne)": "Routing zur Verlaufskontrolle nach Adnektomie mit benigner Histologie.",
        "Route Verlaufskontrolle (Histologie Laparotomie benigne)": "Routing zur Verlaufskontrolle nach Laparotomie mit benigner Histologie.",
        "Route Verlaufskontrolle (Histologie Laparoskopie benigne)": "Routing zur Verlaufskontrolle nach Laparoskopie mit benigner Histologie.",
        "Route Adnektomie (Op Plan Adnektomie)": "Routing zur Adnektomie bei entsprechendem OP-Plan.",
        "Route Adnektomie (cFIGO early)": "Routing zur Adnektomie im frühen klinischem FIGO Stadium.",
        "Route Debulking Assessment (FIGO Bucket advanced)": "Routing zum Debulking-Assessment bei fortgeschrittenem klinischem FIGO Stadium.",
        "Route Debulking Assessment (Histologie Zystenausschälung maligne)": "Routing zum Debulking-Assessment nach Zystektomie mit maligner Histologie.",
        "Route Debulking Assessment (Histologie Adnektomie maligne)": "Routing zum Debulking-Assessment nach Adnektomie mit maligner Histologie.",
        "Route Interdisziplinäres Tumorboard (Laparotomie)": "Routing zum Tumorboard nach Laparotomie.",
        "Route Interdisziplinäres Tumorboard (Laparoskopie)": "Routing zum Tumorboard nach LSK.",
        "Route HRD/BRCA Resolver (HRD Testung)": "Routing zum Resolver basierend auf sBRCA/sHRD.",
        "Route HRD/BRCA Resolver (Humangenetische Beratung gBRCA1/2)":
            "Routing zum Resolver basierend auf gBRCA.",
        "Route Optimales Debulking & Komplementtierung Chemotherapie (3x) (Interim Restaging)":
            "Routing zu optimalem Debulking und Komplementtierung der Chemotherapie nach Interim-Operabilität (OP+Completion vs. Weiterbehandlung).",
        "Route Optimales Debulking & Komplementtierung Chemotherapie (3x) (Repeated Debulking Assessment)":
            "Routing zu optimalem Debulking und Komplementtierung der Chemotherapie nach erneutem Debulking-Assessment.",
        "Route Next Step (Neoadjuvant)": "Routing zum nächsten Schritt im neoadjuvantem Pfad.",
        "Route Systemtherapie Done (Neoaduvant)": "Routing zum Abschluss der Systemtherapie von neoadjuvanten Therapie kommend.",
        "Route Next Step (Adjuvant)": "Routing zum nächsten Schritt im adjuvantem Pfad.",
        "Route Systemtherapie Done (Adjuvant)": "Routing zum Abschluss der Systemtherapie von adjuvanten Therapie kommend.",
        "Route Nachsorge (Systemtherapie)": "Routing zur Nachsorge nach Systemtherapie.",
        "Route Nachsorge (Erhaltungstherapie)": "Routing zur Nachsorge nach Erhaltungstherapie.",
    },

    "facts": {
        # Sonography / IOTA
        "B1_unilokulaer": "Unilokuläre (einkammerige) Zyste.",
        "B2_solide_lt7mm": "Solide Komponenten <7mm.",
        "B3_schallschatten": "Schallschatten.",
        "B4_glatt_multilok_lt10cm": "Glattee multilokulärer Tumor <10cm.",
        "B5_keine_doppler_flow": "Kein Blutfluss in der farbkodierten Duplexsonografie.",
        "M1_unreg_solid": "Unregelmäßiger solider Tumor.",
        "M2_ascites": "Aszites vorhanden.",
        "M3_ge4_papillae": "Mindestens 4 papilläre Strukturen.",
        "M4_unreg_multilok_solid_gt10cm": "Unregelmäßiger multilokulärer solider Tumor >10cm.",
        "M5_hoher_doppler_flow": "Hoher Blutfluss in der farbkodierten Duplexsonografie.",
        "ca125_u_ml": "Numerischer CA-125-Wert (U/ml).",
        "size_cm": "Maximaldurchmesser der Zyste (cm).",
        "praemenopausal": "Prä-/Postmenopausen-Status.",
        "symptoms_present": "Symptome vorhanden (ja/nein).",
        "growth": "Größenzunahme im Verlauf (ja/nein).",
        "persistence": "Persistenz im Verlauf (ja/nein).",
        "complex_multiloculaer": "Komplexe/multilokuläre Morphologie (ja/nein).",
        "psychic_unsure": "Unsicherheit/Belastung der Patientin (ja/nein).",
        "iota_res": "IOTA Simple Rules Ergebnis (benigne/maligne).",

        # OP-Plan & OP-Histology
        "cyst_bd": "BD-Klassifikationsergebnis.",
        "op_plan": "Geplanter OP-Typ (keine OP / Zystektomie / Adnektomie).",
        "histology_cystectomy": "Histologie aus Zystektomie (benigne/maligne).",
        "histology_adnexectomy": "Histologie aus Adnektomie (benigne/maligne).",

        # Clinical/Pathological Staging
        "figo_clinical": "Klinisches FIGO-Stadium (cFIGO, aus CT).",
        "figo_bucket": "Stadium-Bucket (early/advanced).",
        "histology_laparotomy": "Histologie aus Laparotomie (benigne/maligne).",
        "grade_laparotomy": "Tumorgrading nach Laparotomie (low/high).",
        "figo_path_laparotomy": "Pathologisches FIGO nach Laparotomie.",
        "histology_laparoscopy": "Histologie aus Laparoskopie (benigne/maligne).",
        "grade_laparoscopy": "Tumorgrading nach Laparoskopie (low/high).",
        "figo_path_laparoscopy": "Pathologisches FIGO nach Laparoskopie.",

        # HRD/BRCA
        "gBRCA1/2": "Keimbahn-BRCA1/2 (gBRCA).",
        "sBRCA1/2": "Somatische BRCA1/2 im Tumor (sBRCA).",
        "sHRD": "Tumorale HRD (sHRD).",
        "hrd_status": "Zusammengefasster HRD-Status.",
        "brca_status": "Zusammengefasster BRCA-Status.",

        # Mapping/Strategy/Next Steps – Neoadjuvant
        "plan_strategy_neoadjuvant": "Geplantes NACT-Regime (Plan).",
        "plan_next_step_neoadjuvant": "Geplanter nächster Schritt im NACT-Pfad.",
        "strategy_neoadjuvant": "Tatsächlich verabreichtes NACT-Regime.",
        "next_step_neoadjuvant": "Nächster Schritt nach NACT-Mapping.",
        "operabel_interim_neoadjuvant": "Operabilität im Interim-Restaging (ja/nein).",

        # Mapping/Strategy/Next Steps – Adjuvant
        "plan_strategy_adjuvant": "Geplantes adjuvantes Regime (Plan).",
        "plan_next_step_adjuvant": "Geplanter nächster Schritt im Adjuvanz-Pfad.",
        "strategy_adjuvant": "Tatsächlich verabreichtes adjuvantes Regime.",
        "next_step_adjuvant": "Nächster Schritt nach Adjuvanz-Mapping.",

        # Maintenance
        "plan_strategy_maintenance": "Geplante Erhaltungstherapie (Plan).",
        "strategy_maintenance": "Tatsächlich verabreichte Erhaltungstherapie.",

        "next_step_system_therapy": "Globaler nächster Schritt nach Systemtherapie(Erhaltung vs. Nachsorge).",
        "repeated_debulking_possible": "Ergebnis der Wiederholungs-Operabilität.",

        # Parallel
        "parallel_starting": "Gate: Startsignal für parallele Pfade (gesetzt) (true/false).",
        "parallel_done": "Gate: Alle parallelen Pfade sind abgeschlossen (true/false).",

        # Routing-Flags
        "route_follow_up_care": "Gate: Route zu Nachsorge freigeschaltet (true/false).",
        "route_opt_debulking": "Gate: Route zu optimalem Debulking freigeschaltet (true/false).",
        "route_system_therapy_done": "Gate: Systemtherapie abgeschlossen, weiterer Weg möglich (true/false).",
        "route_follow_up": "Gate: Route zu Verlaufskontrolle freigeschaltet (true/false).",
        "route_adnexectomy": "Gate: Route zu Adnektomie freigeschaltet (true/false).",
        "route_interdisciplinary_tumorboard": "Gate: Route zum Tumorboard freigeschaltet (true/false).",
        "route_laparotomy": "Gate: Route zu Laparotomie freigeschaltet (true/false).",
        "route_laparoscopy": "Gate: Route zu Laparoskopie freigeschaltet (true/false).",
        "route_hrd_brca_resolver": "Gate: Route zu HRD/BRCA-Resolver freigeschaltet (true/false).",
        "route_debulking_assessment": "Gate: Route zu Debulking-Assessment freigeschaltet (true/false).",

        # Evidence-/Completion-Flags
        "debulking_possible": "Ergebnis Debulking-Assessment (true/false/unknown).",

        # Evidence-Flags
        "ev_sonography_present": "EVIDENZ: Gynakologische Untersuchung und Sonographie durchgeführt/vorhanden (true/false).",
        "ev_ct_present": "EVIDENZ: CT Thorax/Abdomen durchgeführt/vorhanden (true/false).",

        "ev_cystectomy_done": "EVIDENZ: Zystektomie durchgeführt (true/false).",
        "ev_adnexectomy_done": "EVIDENZ: Adnektomie durchgeführt (true/false).",
        "ev_laparotomy_done": "EVIDENZ: Laparotomie durchgeführt (true/false).",
        "ev_laparoscopy_done": "EVIDENZ: Laparoskopie durchgeführt (true/false).",

        "ev_genetic_counseling_done": "EVIDENZ: humangenetische Beratung erfolgt (true/false).",
        "ev_hrd_test_done": "EVIDENZ: HRD/sBRCA-Test durchgeführt (true/false).",

        "ev_adjuvant_therapy_done": "EVIDENZ: adjuvante Systemtherapie durchgeführt/erhalten (true/false).",

        "ev_neoadjuvant_therapy_done": "EVIDENZ: neoadjuvante Systemtherapie durchgeführt/erhalten (true/false).",
        "ev_interim_restaging_3_done": "EVIDENZ: Interim-Restaging (~3 Zyklen) erfolgt (true/false).",
        "ev_chemo_protocol_switch_completion_done": "EVIDENZ: Protokollwechsel/Komplementierung (NACT) durchgeführt (true/false).",
        "ev_optimal_debulking_completion_done": "EVIDENZ: Optimales Debulking + Chemo-Komplementierung komplett (true/false).",

        "ev_maintenance_therapy_done": "EVIDENZ: Erhaltungstherapie durchgeführt (true/false).",

    }
}
