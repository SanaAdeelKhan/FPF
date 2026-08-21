"""
Transparency layer: turns factor scores into the plain-language explanation shown
to candidates on shortlist reveal, e.g.
  "87% match: strong skill overlap, location compatible, seniority aligned."

Keep this template-based first (fast, deterministic, free) — only reach for an LLM
call here if template output feels too robotic in the demo. Judges are scoring
"Presentation & Demo" (15%) partly on how convincing this text sounds.
"""

from app.models.match import MatchFactorScore


def generate_explanation(overall_score: float, factor_scores: list[MatchFactorScore]) -> str:
    """
    TODO: build a template that:
      - leads with the overall percentage
      - names the 2-3 strongest factors in plain language
      - flags the weakest factor honestly if it's below ~0.5, rather than hiding it
        (an honest partial match is more trustworthy than a falsely glowing one)
    """
    raise NotImplementedError("explainer.generate_explanation: build the template")
