# Short, clinically meaningful one-line definitions per STEP and FACT
# Routing flags (route_*) are purely switches/gates – not independent measures.

from typing import Dict

definitions: Dict[str, Dict[str, str]] = {
    "steps": {
        # Basis & Diagnostik
        "Vorsorge/Symptome": "Ausgangspunkt: Anamnese/Symptome erfassen; liefert klinischen Verdacht.",
        "Gynäkologische Untersuchung & Sonographie": "Klinische Untersuchung + Ultraschall nach IOTA; liefert Basisbefunde.",
        "IOTA-Auswertung (Simple Rules)": "IOTA Simple Rules zur benign/malign-Einschätzung; liefert IOTA-Ergebnis.",
        "Zystenklassifikation (BD-Klassifikation)": "BD-Klassifikation der Zyste zur OP-Planung; liefert BD-Kategorie.",
        "CT Thorax/Abdomen": "Staging-CT; liefert cFIGO-Hinweise und Ausbreitung.",
        "FIGO Bucketer": "Einstufung in ‚early‘ vs ‚advanced‘ anhand cFIGO; leitet nächsten Pfad ab.",
        "Debulking Assessment": "Operabilität/erreichbares Debulking einschätzen.",
        "OP-Entscheider": "OP-Plan festlegen (keine OP/Zystektomie/Adnektomie); liefert OP-Plan.",
        "Verlaufskontrolle": "Kontrolle bei konservativ/benignem Verlauf; entscheidet Beobachtung/Ende.",
        "Zystenausschälung": "Zystektomie durchführen; liefert Histologie (Zystektomie).",
        "Adnektomie": "Adnexentfernung durchführen; liefert Histologie (Adnektomie).",

        # Resektabilität/Tumorboard
        "Beurteilung Resektabilität im Tumorboard": "Interdisziplinäre Operabilitäts-Einschätzung; liefert Empfehlung zum operativen Vorgehen.",
        "Laparotomie, SS": "Primäre Laparotomie/Debulking/Proben; liefert OP-Befunde.",
        "Laparotomie, Pathologie Auswertung": "Patho-Befund nach Laparotomie; liefert Grad & pFIGO.",
        "Laparoskopie oder Minilaparotomie": "Diagnostisch/therapeutische LSK/Minilaparotomie; liefert intraop. Befunde.",
        "Laparoskopie, Pathologie Auswertung": "Patho-Befund nach LSK; liefert Grad & pFIGO.",
        "Interdisziplinäres Tumorboard": "Therapieentscheidung aus allen Befunden; legt Gesamtplan fest.",

        # HRD / BRCA
        "Humangenetische Beratung (gBRCA)": "Genetische Beratung + Keimbahn-BRCA testen; liefert gBRCA-Status.",
        "HRD Testung (sBRCA & sHRD)": "Tumorbasierte HRD/sBRCA-Testung; liefert sBRCA/sHRD.",
        "HRD/BRCA Testung": "Fasst gBRCA, sBRCA und sHRD zusammen; liefert BRCA-/HRD-Gesamtstatus.",

        # Neoadjuvant
        "Neoadjuvante Therapie Mapping": "Neoadjuvantes Regime planen; legt nächsten Schritt fest.",
        "Neoadjuvante Therapie": "Neoadjuvante Chemotherapie durchführen; liefert Therapieverlauf.",
        "Next Step Mapping Neoadjuvant": "Nächsten Schritt nach NACT bestimmen; plant OP/Weiterbehandlung.",
        "Reevaluation nach 3 Zyklen, CT Thorax Abdomen, CA125, Operabilität Assessment":
            "Zwischenstaging (~3 Zyklen) inkl. Operabilität; liefert Interim-Operabilität/Response.",
        "Wechsel Therapieprotokoll & Komplementierung Chemotherapie (3x)":
            "Protokollwechsel/Komplementierung bei NACT; dokumentiert Durchführung.",
        "Optimales Debulking & Komplementierung Chemotherapie (3x)":
            "OP mit optimalem Debulking + Chemo-Komplementierung; dokumentiert Vollständigkeit.",
        "Wiederholung Debulking Assessment": "Operabilität nach NACT erneut prüfen; liefert aktualisierte Einschätzung.",
        "Therapie Reevaluation": "Gesamt-Review (Wirksamkeit/Toxizität/Next Step); konsolidiert Entscheidung.",

        # Adjuvant
        "Adjuvante Therapie Mapping": "Adjuvantes Regime planen; legt Sequenz fest.",
        "Adjuvante Therapie": "Adjuvante Chemotherapie durchführen; liefert Abschluss/Regime.",
        "Next Step Mapping Adjuvant": "Nächsten Schritt nach Adjuvanz bestimmen; entscheidet Erhaltung vs. Nachsorge.",

        # Parallel & Maintenance
        "Parallel Join": "Synchronisation: Systemtherapie **und** Genetik/Resolver müssen abgeschlossen sein; erst dann Erhaltung/Nachsorge.",
        "Erhaltungs Therapie Mapping": "Erhaltungstherapie planen (Optionen, Voraussetzungen).",
        "Erhaltungs Therapie": "Erhaltungstherapie durchführen; dokumentiert Start/Verlauf.",
        "Nachsorge": "Regelmäßiges Follow-up nach System-/Erhaltungstherapie; legt Kontrollintervalle fest.",

        # Routing (freundliche, klinische Kurztexte)
        "Route Verlaufskontrolle (Keine OP)": "Weichenstellung: Verlaufskontrolle bei ‚keine OP‘.",
        "Route Verlaufskontrolle (Histologie Zystenausschälung benigne)": "Weichenstellung: Verlaufskontrolle nach benigner Zystektomie-Histologie.",
        "Route Verlaufskontrolle (Histologie Adnektomie benigne)": "Weichenstellung: Verlaufskontrolle nach benigner Adnektomie-Histologie.",
        "Route Verlaufskontrolle (Histologie Laparotomie benigne)": "Weichenstellung: Verlaufskontrolle nach benigner Laparotomie-Histologie.",
        "Route Verlaufskontrolle (Histologie Laparoskopie benigne)": "Weichenstellung: Verlaufskontrolle nach benigner LSK-Histologie.",
        "Route Adnektomie (Op Plan Adnektomie)": "Weichenstellung: Adnektomie bei entsprechendem OP-Plan.",
        "Route Adnektomie (cFIGO early)": "Weichenstellung: Adnektomie im frühen Stadium.",
        "Route Debulking Assessment (FIGO Bucket advanced)": "Weichenstellung: Debulking-Assessment bei fortgeschrittenem Stadium.",
        "Route Debulking Assessment (Histologie Zystenausschälung maligne)": "Weichenstellung: Debulking-Assessment nach maligner Zystektomie.",
        "Route Debulking Assessment (Histologie Adnektomie maligne)": "Weichenstellung: Debulking-Assessment nach maligner Adnektomie.",
        "Route Interdisziplinäres Tumorboard (Laparotomie)": "Weichenstellung: Tumorboard nach Laparotomie.",
        "Route Interdisziplinäres Tumorboard (Laparoskopie)": "Weichenstellung: Tumorboard nach LSK.",
        "Route HRD/BRCA Testung (HRD Testung)": "Weichenstellung: Resolver nach sBRCA/sHRD.",
        "Route HRD/BRCA Testung (Humangenetische Beratung gBRCA1/2)": "Weichenstellung: Resolver nach gBRCA.",
        "Route Optimales Debulking & Komplementtierung Chemotherapie (3x) (Interim Restaging)":
            "Weichenstellung: OP+Komplementierung nach Interim-Operabilität.",
        "Route Optimales Debulking & Komplementtierung Chemotherapie (3x) (Repeated Debulking Assessment)":
            "Weichenstellung: OP+Komplementierung nach erneutem Operabilitäts-Check.",
        "Route Next Step (Neoadjuvant)": "Weichenstellung: Nächster Schritt im neoadjuvanten Verlauf.",
        "Route Systemtherapie Done (Neoaduvant)": "Weichenstellung: Systemtherapie (neoadjuvant) abgeschlossen.",
        "Route Next Step (Adjuvant)": "Weichenstellung: Nächster Schritt im adjuvanten Verlauf.",
        "Route Systemtherapie Done (Adjuvant)": "Weichenstellung: Systemtherapie (adjuvant) abgeschlossen.",
        "Route Nachsorge (Systemtherapie)": "Weichenstellung: Nachsorge nach Systemtherapie.",
        "Route Nachsorge (Erhaltungstherapie)": "Weichenstellung: Nachsorge nach Erhaltungstherapie.",
    },

    "facts": {
        # Sonographie / IOTA
        "B1_unilokulaer": "Unilokuläre (einkammerige) Zyste (IOTA-B).",
        "B2_solide_lt7mm": "Solide Komponente <7 mm (IOTA-B).",
        "B3_schallschatten": "Akustischer Schallschatten (IOTA-B).",
        "B4_glatt_multilok_lt10cm": "Glatte multilokuläre Struktur <10 cm (IOTA-B).",
        "B5_keine_doppler_flow": "Kein starker Dopplerfluss (IOTA-B).",
        "M1_unreg_solid": "Unregelmäßige solide Läsion (IOTA-M).",
        "M2_ascites": "Aszites vorhanden (IOTA-M).",
        "M3_ge4_papillae": "≥4 Papillen (IOTA-M).",
        "M4_unreg_multilok_solid_gt10cm": "Unregelm. multilok./solide Struktur >10 cm (IOTA-M).",
        "M5_hoher_doppler_flow": "Starker Dopplerfluss (IOTA-M).",
        "ca125_u_ml": "Numerischer CA-125-Wert (U/ml).",
        "size_cm": "Größter Zystendurchmesser (cm).",
        "praemenopausal": "Menopausenstatus (prä/post).",
        "symptoms_present": "Symptome vorhanden (ja/nein).",
        "growth": "Größenzunahme (ja/nein).",
        "persistence": "Persistenz (ja/nein).",
        "complex_multiloculaer": "Komplexe/multilokuläre Morphologie (ja/nein).",
        "psychic_unsure": "Unsicherheit/Belastung der Patientin (ja/nein).",
        "iota_res": "IOTA-Simple-Rules-Ergebnis (benigne/maligne/unklar).",

        # OP-Plan & OP-Histologie
        "cyst_bd": "BD-Klassifikation (für OP-Plan).",
        "op_plan": "Geplanter OP-Typ (keine OP/Zystektomie/Adnektomie).",
        "histology_cystectomy": "Histologie nach Zystektomie (benigne/maligne).",
        "histology_adnexectomy": "Histologie nach Adnektomie (benigne/maligne).",

        # Klinisches / Pathologisches Staging
        "figo_clinical": "Klinisches FIGO-Stadium (cFIGO; CT).",
        "figo_bucket": "Stadium-Bucket (early/advanced) aus cFIGO.",
        "histology_laparotomy": "Histologie nach Laparotomie (benigne/maligne).",
        "grade_laparotomy": "Tumorgrading nach Laparotomie (low/high).",
        "figo_path_laparotomy": "Pathologisches FIGO nach Laparotomie.",
        "histology_laparoscopy": "Histologie nach Laparoskopie (benigne/maligne).",
        "grade_laparoscopy": "Tumorgrading nach Laparoskopie (low/high).",
        "figo_path_laparoscopy": "Pathologisches FIGO nach Laparoskopie.",

        # HRD/BRCA Testung
        "gBRCA1/2": "Keimbahn-BRCA1/2 (gBRCA) – Ergebnis.",
        "sBRCA1/2": "Somatische BRCA1/2 im Tumor (sBRCA) – Ergebnis.",
        "sHRD": "Tumorale HRD (sHRD) – Ergebnis.",
        "hrd_status": "Gesamt-HRD-Status (aus gBRCA/sBRCA/sHRD).",
        "brca_status": "Gesamt-BRCA-Status (aus gBRCA/sBRCA).",

        # Mapping/Strategy/Next Steps – Neoadjuvant
        "plan_strategy_neoadjuvant": "Geplantes NACT-Regime.",
        "plan_next_step_neoadjuvant": "Geplanter nächster NACT-Schritt.",
        "strategy_neoadjuvant": "Tatsächlich verabreichtes NACT-Regime.",
        "next_step_neoadjuvant": "Nächster Schritt nach NACT-Mapping.",
        "operabel_interim_neoadjuvant": "Operabilität im Interim-Restaging (ja/nein).",

        # Mapping/Strategy/Next Steps – Adjuvant
        "plan_strategy_adjuvant": "Geplantes adjuvantes Regime.",
        "plan_next_step_adjuvant": "Geplanter nächster Schritt Adjuvanz.",
        "strategy_adjuvant": "Tatsächlich verabreichtes adjuvantes Regime.",
        "next_step_adjuvant": "Nächster Schritt nach Adjuvanz-Mapping.",

        # Erhaltung
        "plan_strategy_maintenance": "Geplante Erhaltungstherapie.",
        "strategy_maintenance": "Tatsächlich verabreichte Erhaltungstherapie.",

        # Merging / globaler Next Step
        "next_step_system_therapy": "Globaler nächster Schritt nach Systemtherapie (Erhaltung vs. Nachsorge).",
        "repeated_debulking_possible": "Ergebnis der erneuten Operabilitätsprüfung.",

        # Parallel (Gates)
        "parallel_starting": "Gate: Parallele Pfade gestartet .",
        "parallel_done": "Gate: Parallele Pfade abgeschlossen .",

        # Routing-Flags (Gates)
        "route_follow_up_care": "Gate: Nachsorge-Route offen .",
        "route_opt_debulking": "Gate: Route ‚optimales Debulking‘ offen .",
        "route_system_therapy_done": "Gate: Systemtherapie abgeschlossen → Weiterweg möglich .",
        "route_follow_up": "Gate: Verlaufskontrolle-Route offen .",
        "route_adnexectomy": "Gate: Adnektomie-Route offen .",
        "route_interdisciplinary_tumorboard": "Gate: Tumorboard-Route offen .",
        "route_laparotomy": "Gate: Laparotomie-Route offen .",
        "route_laparoscopy": "Gate: Laparoskopie-Route offen .",
        "route_hrd_brca_resolver": "Gate: HRD/BRCA Testung-Resolver-Route offen .",
        "route_debulking_assessment": "Gate: Debulking-Assessment-Route offen .",

        # Evidence-/Completion-Flags (Nachweise)
        "debulking_possible": "Nachweis Operabilität/Debulking-Einschätzung.",

        # Evidence-Flags (Diagnostik/OP/Therapie durchgeführt?)
        "ev_sonography_present": "Nachweis: Gynäkologische Untersuchung/Sonographie vorhanden .",
        "ev_ct_present": "Nachweis: CT Thorax/Abdomen vorhanden .",

        "ev_cystectomy_done": "Nachweis: Zystektomie durchgeführt .",
        "ev_adnexectomy_done": "Nachweis: Adnektomie durchgeführt .",
        "ev_laparotomy_done": "Nachweis: Laparotomie durchgeführt .",
        "ev_laparoscopy_done": "Nachweis: Laparoskopie durchgeführt .",

        "ev_genetic_counseling_done": "Nachweis: Humangenetische Beratung erfolgt .",
        "ev_hrd_test_done": "Nachweis: HRD/sBRCA-Test durchgeführt .",

        "ev_neoadjuvant_therapy_done": "Nachweis: Neoadjuvante Systemtherapie erhalten .",
        "ev_adjuvant_therapy_done": "Nachweis: Adjuvante Systemtherapie erhalten .",
        "ev_interim_restaging_3_done": "Nachweis: Interim-Restaging (~3 Zyklen) erfolgt .",
        "ev_chemo_protocol_switch_completion_done": "Nachweis: Protokollwechsel/Komplementierung (NACT) erfolgt .",
        "ev_optimal_debulking_completion_done": "Nachweis: Optimales Debulking + Chemo-Komplementierung komplett .",

        "ev_maintenance_therapy_done": "Nachweis: Erhaltungstherapie durchgeführt .",
    }
}
