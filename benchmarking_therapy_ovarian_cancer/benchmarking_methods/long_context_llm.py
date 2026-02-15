import logging

from pathlib import Path
from typing import Optional

import pymupdf


_GUIDELINE_CACHE: Optional[str] = None
def _load_guideline_text(path: Path, max_chars: int = 100_000) -> str:
    # TODO make it more dynamic
    """Extract and return text from a PDF file up to a character limit."""
    global _GUIDELINE_CACHE
    if _GUIDELINE_CACHE is None:
        doc = pymupdf.open(str(path))
        _GUIDELINE_CACHE = "\n".join(page.get_text() for page in doc)[:max_chars]
    return _GUIDELINE_CACHE
