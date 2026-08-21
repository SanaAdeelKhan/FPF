# Architecture

## Data flow

```
Employer                                Candidate
   |                                        |
   | POST /employers/postings               | POST /candidates
   | (title, seniority, years,               | (name, location, seniority,
   |  hidden_requirements)                   |  years, availability, cv_raw_text)
   v                                        v
[JobPosting stored]                    [cv_parser.parse_cv]
   |                                        |
   |                                        v
   |                                  [ParsedCVProfile stored]
   |                                        |
   +---------------> POST /matching/run/{candidate_id}/{posting_id}
                              |
                              v
                    [matching_engine.compute_match]
                     scores: skills, location,
                     seniority, availability
                              |
                              v
                    [explainer.generate_explanation]
                    "87% match: strong skill overlap..."
                              |
                              v
                    [MatchResult stored + returned]
                              |
                     if shortlisted:
                              v
                    GET /matching/reveal/{candidate_id}/{posting_id}
                    -> full hidden_requirements unlocked
```

## Key design decisions

- **Hidden requirements never leave the backend** until a candidate is explicitly
  marked `shortlisted=True` on a `MatchResult`. The `/employers/postings` public
  response model (`JobPostingPublic`) structurally excludes the hidden fields —
  it's not just a UI choice, the field doesn't exist on that response type.
- **Factor scores are independent and explainable.** `compute_match` returns both
  an overall score and the list of per-factor scores, so the explanation layer has
  real numbers to describe rather than generating plausible-sounding text
  disconnected from the actual scoring.
- **CV parsing is isolated behind one function** (`cv_parser.parse_cv`) so the
  extraction strategy (LLM prompt vs. rule-based fallback) can change without
  touching the matching engine's interface.

## Roadmap: fair-interview layer

Not built for this submission. Planned approach: live video interview session,
transcribed in real time, with an LLM generating unscripted follow-up questions
based on the candidate's actual answers — making it far harder to have pre-scripted
or AI-fed responses ready, unlike typed/async interview formats.
