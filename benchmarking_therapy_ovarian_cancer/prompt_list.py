

suspected_prompt_template = """
## Rolle
Fachärzt:in für Gynäkologische Onkologie im interdisziplinären Tumorboard.

## Aufgabe (Verdachtsfall)
Formuliere eine **konkrete nächste Maßnahme** bei Verdacht auf Ovarialtumor.
- Priorisiere diagnostische Sicherung (Biopsie/Punktion, Schnellschnitt) und OP-Triage (LSK vs. Laparotomie, Debulking) je nach Fall.
- Bildgebung/Abklärung präzisieren (z. B. CT-Thorax/Abdomen/Becken, Aszitespunktion), falls erforderlich.
- Benenne genetische/biomarker-Schritte nur, wenn aus Patientendaten ableitbar oder zwingend indiziert.

## Constraints
- Nutze **nur** die untenstehenden Patientendaten. Keine externen Fakten. Keine erfundenen Studien/Literatur.
- **Keine Schablonen**: Beispiele dienen nur als Stil-/Granularitätsreferenz.
- Nenne fehlende Schlüsselinformationen explizit (z. B. „Histologie ausstehend“).

## Format
**Therapieempfehlung:** <eine präzise Zeile>
**Begründung:** <kurz; klinische Plausibilität, was die nächste Entscheidung triggert>

## Beispiele (nur Stil/Granularität; nicht kopieren)
- (Verdacht) „Längslaparotomie mit Tumordebulking; intraoperativer Schnellschnitt.“
- (Verdacht) „Aszitespunktion zur Histologie; danach Wiedervorstellung im Tumorboard.“
- (Verdacht) „Diagnostische LSK zur Zystenausschälung; ggf. Adnektomie links abhängig vom Befund.“

---
### Patientendaten
{patient_info}
"""

diagnosed_prompt_template = """
## Rolle
Fachärzt:in für Gynäkologische Onkologie im interdisziplinären Tumorboard.

## Aufgabe (gesicherte Diagnose)
Formuliere eine **Primärtherapie** für Ovarialkarzinom inklusive Regime/OP-Schritte und (wo angemessen) genetische Diagnostik.
- Systemtherapie (z. B. Platinschema ± Bevacizumab) oder Primär-OP mit onkologischen Prozeduren (OmE, Peritoneal-PEs, Spülzytologie etc.) je nach Fall.
- Genetik (BRCA/HRD) **nur** nennen, wenn klinisch indiziert oder aus Daten ableitbar.

## Constraints
- Nutze **nur** die Patientendaten unten. Keine externen Quellen. Keine erfundenen Studien/Literatur.
- **Keine Schablonen**: Beispiele sind Stilanker, nicht Zieltexte.
- Fehlen Informationen → explizit benennen.

## Format
**Therapieempfehlung:** <eine präzise Zeile>
**Begründung:** <kurz; Stadium/Histologie/Komorbiditäten als Begründung>

## Beispiele (nur Stil/Granularität; nicht kopieren)
- (Diagnose) „Paclitaxel + Carboplatin + Bevacizumab; genetische Beratung/BRCA-Testung; Reevaluation bildgebend.“
- (Diagnose) „LSK mit AE links, OmE, Spülzytologie, Peritoneal-Biopsien; genetische Beratung.“

---
### Patientendaten
{patient_info}
"""



long_context_suspected_prompt_template = """
## Rolle
Fachärzt:in für Gynäkologische Onkologie im interdisziplinären Tumorboard.

## Aufgabe (Verdachtsfall, mit Leitlinienkontext)
Formuliere die **konkrete nächste Maßnahme** bei Verdacht auf Ovarialtumor.

### Verfügbare Leitlinienbasis (nur diesen Kontext verwenden)
{context_block}

## Leitplanken
- Entscheidungen **primär** aus dem Leitlinienkontext + Patientendaten ableiten (keine externen Quellen).
- Priorisiere diagnostische Sicherung (Biopsie/Punktion, Schnellschnitt) und OP-Triage (LSK vs. Laparotomie, Debulking).
- Bildgebung/Abklärung präzisieren (z. B. CT-Thorax/Abdomen/Becken, Aszitespunktion), falls sinnvoll.
- Genetik/Biomarker **nur**, wenn aus Daten/Kontext indiziert.
- Fehlen wesentlicher Infos → explizit benennen.

## Format
**Therapieempfehlung:** <eine präzise Zeile>
**Begründung:** <kurz; warum diese nächste Maßnahme auf Basis von Kontext + Patientendaten sinnvoll ist>

---
### Patientendaten
{patient_info}
"""

long_context_diagnosed_prompt_template = """
## Rolle
Fachärzt:in für Gynäkologische Onkologie im interdisziplinären Tumorboard.

## Aufgabe (gesicherte Diagnose, mit Leitlinienkontext)
Formuliere eine **Primärtherapie** für Ovarialkarzinom (Regime/OP-Schritte; ggf. Genetik).

### Verfügbare Leitlinienbasis (nur diesen Kontext verwenden)
{context_block}

## Leitplanken
- Leite Systemtherapie (z. B. Platin-basierte Regime ± Bevacizumab) **oder** Primär-OP (z. B. OmE, Peritoneal-PEs, Spülzytologie) aus Kontext + Patient:innendaten ab.
- Genetik (BRCA/HRD) nur nennen, wenn im Kontext/klinisch indiziert.
- Keine externen Fakten; Beispiele sind Stilanker, nicht Zieltexte.
- Fehlende Schlüsselinformationen explizit benennen.

## Format
**Therapieempfehlung:** <eine präzise Zeile>
**Begründung:** <kurz; Bezug auf Stadium/Histologie/Operabilität etc. **aus dem Kontext**>

---
### Patientendaten
{patient_info}
"""

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