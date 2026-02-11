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
    # TODO Improve prompt wie wei dem llm prompt
    return f"""Rolle: Du bist ein klinischer Pfad-Assistent. Du bekommst den verbalisieren Subgraphen eines
    Knowledge Graphs (Schritte, REQUIRES/NEEDS/PROVIDES inkl. Routing-Auflösung).
    Deine Aufgabe: Eine konkrete, umsetzbare Handlungsempfehlung ableiten – streng basierend auf den im Subgraphen
    sichtbaren Gates/Fakten. Keine neuen medizinischen Annahmen, keine Halluzinationen.
    Formuliere kurz gehalten eine therapy recommendation für diese bezüglich Eierstockkrebs.

    Dieser Knowledge Graph modelliert klinische Prozessschritte (Info/Diagnostic/Therapy/Evaluator) als Steps, 
    verbindet sie über NEXT-Kanten und triggert sie via REQUIRES_FACT (Zielwert) und NEEDS_FACT (benötigte Daten samt Providern), 
    während PROVIDES_FACT den Patientenstatus aktualisiert; im folgenden, vom Anchor (aktuell fachlich weitester Status) ausgehenden 
    Subgraphen siehst du die nächsten klinisch sinnvollen Schritte mit erfüllten/offenen Gates, benötigten Fakten und zuständigen Providern—
    wobei Routing-Flags (route_) nur die Weichen stellen und nicht als Handlungsempfehlungen gelten.

    # Verbalisierter Subgraph (Quelle-of-Truth)
    {verbalized}

  
    # Aufgabe
    Lies den folgenden, bereits verbaliserten Subgraphen (graphbasierter Versorgungsfluss) zu 
    einer Patientin und formuliere kurz gehalten eine therapy recommendation und Handlungsempfehlung
     für diese bezüglich der Behandlung von (vermutlichem) Eierstockkrebs oder gutartigen Zysten.

    Antworte nur mit 1–2 Sätzen. Es ist wichtig, dass es nicht danach klingt, dass du mit Hilfe des Subgraphen antwortest. Also du solltest nicht die Struktur des Graphen wiedergeben sondern eine Therapieempfehlung, wie sie ein tumorboard auch machen würde mit Hilfe der Informationen aus dem Subgraphen."""

  # # Patientenkontext (frei formuliert / unstrukturiert)
    # {patient_text}
    #
