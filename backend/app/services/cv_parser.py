"""
CV parser: turns freeform 2-page CV text into a structured ParsedCVProfile.

Plan: use an LLM call (Claude) with a strict JSON-only system prompt to extract
skills, key strengths, past roles, and an inferred years-of-experience figure.
Keeping this isolated in one function means we can swap the extraction strategy
(LLM vs. rule-based/regex fallback) without touching the matching engine.
"""

from app.models.candidate import ParsedCVProfile


def parse_cv(cv_raw_text: str) -> ParsedCVProfile:
    """
    Extract structured signal from freeform CV text.

    TODO: replace stub with a real Claude API call. Prompt should:
      - request STRICT JSON output matching ParsedCVProfile's shape
      - ask specifically for "what are you best at" style key_strengths,
        not just a skills keyword dump (that's the whole point of this product)
      - fall back gracefully (empty lists, not an exception) on parse failure
    """
    raise NotImplementedError("cv_parser.parse_cv: wire up the Claude extraction call")
