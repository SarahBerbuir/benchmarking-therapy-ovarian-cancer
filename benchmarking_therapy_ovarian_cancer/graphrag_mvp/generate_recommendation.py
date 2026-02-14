from benchmarking_therapy_ovarian_cancer import config
from benchmarking_therapy_ovarian_cancer.graphrag_mvp.verbalization import verbalize_subgraph_from_anchor
from benchmarking_therapy_ovarian_cancer.llm_vertex import init_vertexai_llm, get_text_llm_fn


def make_llm_fn():
    model = init_vertexai_llm(config.LLM_MODEL_NAME)
    return get_text_llm_fn(
        model = model
    )

def get_graph_recommendation(kg, pid, anchor):
    llm_fn = make_llm_fn()
    verbalized_subgraph = _get_verbalized_subgraph(kg, pid, anchor)
    prompt = _get_graph_rag_reco_prompt(verbalized_subgraph)
    full_text = llm_fn(prompt).strip()

    return full_text

def _get_verbalized_subgraph(kg, pid, anchor):
    verbalized_subgraph = verbalize_subgraph_from_anchor(kg, pid, anchor=anchor)
    print("[verbalization] " + verbalized_subgraph)
    return verbalized_subgraph

def _get_graph_rag_reco_prompt(verbalized: str) -> str:
    return f"""
        ## Rolle
        Du bist Fachärzt:in für Gynäkologische Onkologie im interdisziplinären Tumorboard.
        
        ## Quelle der Wahrheit
        Nur der folgende, verbalisierte Subgraph (inkl. erfüllter/offener Gates, benötigter Fakten und Provider) ist gültig.
        
        # Subgraph (Source of Truth)
        Im folgenden, vom aktuell fachlich weitester Status ausgehenden Subgraphen siehst du die nächsten klinisch sinnvollen Schritte mit erfüllten/offenen Gates, benötigten Fakten und zuständigen Providern—
        wobei Routing-Flags nur die Weichen stellen und nicht als Handlungsempfehlungen gelten.
        
        Subgraph:
        {verbalized}
        
        ## Aufgabe
        Formuliere eine **konkrete, umsetzbare Empfehlung** (Therapie oder nächster Schritt) **in 1–2 kurzen Sätzen**, basierend auf den Informationen im Subgraphen. 
        Es geht um die Behandlung von (vermutlichem) Eierstockkrebs oder gutartigen Zysten.
        - **Wenn Blocker/Fakten fehlen: Formuliere aktiv, was zuerst zu erledigen ist** (mit Provider) **und** hänge **konditional** den vorgesehenen Zielschritt an – ohne zu sagen „Entscheidung nicht möglich“.
        - **Wenn nichts fehlt**: Formuliere direkt den klinischen Schritt (veranlassen/initiieren/überführen).

        ## Stil
        - Klinisch-kurz, präzise, OHNE Erwähnung des Graphen/der Datenstruktur (zB keine Nennung von provider).
        - Keine Begründungsabsätze, keine Aufzählungen; maximal 2 Sätze.
        
        ## Sicherheits-Schienen
        - Wenn Informationen widersprüchlich sind: **klar sagen, dass eine Entscheidung aktuell nicht möglich ist**, und **genau** welche fehlenden Informationen/Provider zuerst benötigt werden.
        - Keine Medikamente/Protokolle erfinden; keine Off-Label-Vorschläge.
        
        ## Ausgabeformat (streng)
        Empfehlung: <ein bis zwei klinische Sätze, siehe Regeln oben>
        """
