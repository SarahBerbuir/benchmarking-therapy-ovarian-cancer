
judge_prompt = """\
Du bist Fachärzt:in für Gynäkologische Onkologie. Beurteile, ob die KANDIDAT-Empfehlung
inhaltlich eine akzeptable Alternative/Deckung zum GOLDSTANDARD darstellt.

Kriterien (kurz):
- Leitliniennähe/Sequenz: passt Maßnahme/Timing?
- Keine Wortlautprüfung; klinische Äquivalenz zählt.
- Bei Unsicherheit: konservativ als inkorrekt werten.

Gib ausschließlich folgendes JSON zurück (ohne weitere Worte):
{{
  "label": "korrekt" | "inkorrekt",
  "score": <Zahl 0.0 bis 1.0>,
  "rationale": "<1 kurzer Satz>"
}}

GOLDSTANDARD:
{gold}

KANDIDAT:
{cand}
"""