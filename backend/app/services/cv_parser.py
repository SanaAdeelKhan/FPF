"""
CV parser: turns freeform 2-page CV text into a structured ParsedCVProfile using
Gemini's free tier (Google AI Studio). Uses Gemini's structured-output mode
(response_schema) so the model is constrained to the exact shape we need instead
of just being asked nicely for JSON — fewer parse failures than prompt-only JSON
mode. A broad try/except still guards the endpoint against any API-side failure
(rate limit, network, malformed response).
"""

import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.models.candidate import ParsedCVProfile

_client: genai.Client | None = None

MODEL_NAME = "gemini-2.0-flash"

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "skills": {"type": "array", "items": {"type": "string"}},
        "years_experience_inferred": {"type": "number", "nullable": True},
        "key_strengths": {"type": "array", "items": {"type": "string"}},
        "past_roles": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
    "required": ["skills", "years_experience_inferred", "key_strengths", "past_roles", "summary"],
}

SYSTEM_PROMPT = """You extract structured information from freeform CVs/resumes.

Rules:
- "skills": concrete technical/professional skills mentioned or clearly implied (tools, languages, domains).
- "key_strengths": what this person is GENUINELY best at, in their own framing — not a keyword
  dump. Look for what they emphasize, elaborate on, or show impact/results for. 2-5 items.
- "past_roles": job titles held, most recent first.
- "years_experience_inferred": your best numeric estimate of total professional experience from
  dates/roles mentioned. Use null if you truly cannot tell.
- "summary": one or two plain sentences capturing who this candidate is professionally.
- If the text is too sparse to extract something, use an empty list/string rather than guessing wildly.
"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com/apikey "
                "and add it to backend/.env"
            )
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def parse_cv(cv_raw_text: str) -> ParsedCVProfile:
    """
    Extract structured signal from freeform CV text via Gemini.
    Falls back to an empty-but-valid ParsedCVProfile on any API or parse failure,
    so one bad LLM response never 500s the candidate upload flow.
    """
    if not cv_raw_text or not cv_raw_text.strip():
        return ParsedCVProfile()

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=cv_raw_text[:12000],  # keep well within context limits
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0.2,
            ),
        )
        data = json.loads(response.text)
        return ParsedCVProfile(
            skills=data.get("skills", []) or [],
            years_experience_inferred=data.get("years_experience_inferred"),
            key_strengths=data.get("key_strengths", []) or [],
            past_roles=data.get("past_roles", []) or [],
            summary=data.get("summary", "") or "",
        )
    except Exception as exc:  # noqa: BLE001 — deliberately broad: any failure degrades gracefully
        print(f"[cv_parser] Gemini extraction failed, returning empty profile: {exc}")
        return ParsedCVProfile(summary="(CV parsing failed — please review manually)")
