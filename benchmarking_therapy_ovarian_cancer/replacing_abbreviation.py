import re
import pandas as pd
from typing import Iterable

def _flex_token_regex(token: str) -> re.Pattern:
    """
    Flexible token matcher:
    - strip to alnum (incl. umlauts)
    - allow optional dots/spaces between letters
    - optional trailing dot
    - no match inside larger words (word-boundary guards)
    """
    letters = re.sub(r"[^0-9A-Za-zÄÖÜäöü]", "", token)
    mid = r"[.\s]*".join(map(re.escape, letters))
    pat = rf"(?<!\w){mid}\.?(?!\w)"
    return re.compile(pat, re.IGNORECASE)

# Abbreviation → expansion (tokens that may appear with dots/spaces)
ABBR_MAP = {
    "v.a.": "Verdacht auf",
    "a.e.": "am ehesten",
    "mb.": "Morbus",
    "klin. ro": "klinisch RO",
    "ggf.": "gegebenenfalls",
    "lt. pat.": "Laut Patientin",
    "o.b.": "ohne Befund",
    "l.p.": "Letzte Periode",
    "v. cava": "Vena cava",
    "bds": "beidseitig",
    "tps": "Tumor Proportion Score",
    "cps": "Combined Positive Score",
    "dd": "Differentialdiagnose",
    "ub": "Unterbauch",
    "rf": "Raumforderung",
    "lk": "Lymphknoten",
    "gr": "groß",
    "az": "Allgemeinzustand",
    "spec": "Spekulum",
    "vu": "Vaginale Untersuchung",
    "sas": "Scheidenabschluss",
    "dj": "Double-J-Schiene",
    "lsk": "Laparoskopie",
    "fa": "Frauenärzt_in",
    "bzw": "beziehungsweise",
    "pst": "primär-systemische Therapie",
    "hrd": "homologe Rekombinationsdefizienz",
    "ome": "Omentektomie",
    "wv": "Wiedervorstellung",
    "he": "Hysterektomie",
}

# Compile patterns
ABBR_PATTERNS = [(_flex_token_regex(k), v) for k, v in ABBR_MAP.items()]

# Plural and singular
ABBR_PATTERNS += [
    (re.compile(r"(?<!\w)pe'?s(?!\w)", re.IGNORECASE), "Probenexzisionen"),
    (re.compile(r"(?<!\w)pe(?!\w)", re.IGNORECASE), "Probenexzision"),
]

def expand_abbreviations_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text
    out = text
    for pat, repl in ABBR_PATTERNS:
        out = pat.sub(repl, out)
    return out

def expand_abbreviations_df(df: pd.DataFrame, columns: Iterable[str] | None = None) -> pd.DataFrame:
    cols = list(columns) if columns else [c for c in df.columns if df[c].dtype == object]
    for c in cols:
        df[c] = df[c].map(expand_abbreviations_text)
    return df


