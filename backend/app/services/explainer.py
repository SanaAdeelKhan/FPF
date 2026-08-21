"""
Transparency layer: turns factor scores into the plain-language explanation shown
to candidates on shortlist reveal, e.g.
  "87% match: strong skill overlap, location compatible, seniority aligned."

Template-based (not LLM) — free, instant, and deterministic, which matters since
this text is shown to real candidates and should trace directly back to the scores
rather than an LLM's independent judgment call.
"""

from app.models.match import MatchFactorScore

_STRONG = 0.75
_WEAK = 0.45

_STRONG_PHRASES = {
    "skills": "strong skill overlap",
    "location": "location compatible",
    "seniority": "seniority aligned",
    "availability": "availability fits",
}
_MODERATE_PHRASES = {
    "skills": "partial skill overlap",
    "location": "location mostly compatible",
    "seniority": "seniority roughly aligned",
    "availability": "availability workable",
}
_WEAK_PHRASES = {
    "skills": "limited skill overlap",
    "location": "location mismatch",
    "seniority": "seniority gap",
    "availability": "availability mismatch",
}


def generate_explanation(overall_score: float, factor_scores: list[MatchFactorScore]) -> str:
    """
    Leads with the overall percentage, names the strongest factors, and honestly
    flags the weakest factor if it's notably low — a partial match stated plainly
    is more trustworthy than one that hides its weak points.
    """
    pct = round(overall_score * 100)

    strong = [f for f in factor_scores if f.score >= _STRONG]
    moderate = [f for f in factor_scores if _WEAK <= f.score < _STRONG]
    weak = [f for f in factor_scores if f.score < _WEAK]

    parts = [f"{pct}% match:"]

    phrase_bits = []
    for f in strong:
        phrase_bits.append(_STRONG_PHRASES.get(f.factor, f"{f.factor} strong"))
    for f in moderate:
        phrase_bits.append(_MODERATE_PHRASES.get(f.factor, f"{f.factor} moderate"))

    if phrase_bits:
        parts.append(", ".join(phrase_bits))

    if weak:
        weak_bits = [_WEAK_PHRASES.get(f.factor, f"{f.factor} weak") for f in weak]
        parts.append(f"but {', '.join(weak_bits)}")

    return " ".join(parts) if len(parts) > 1 else f"{pct}% match"
