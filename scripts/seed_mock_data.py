"""
Seeds a handful of mock job postings and candidate CVs so matching quality can be
validated before the demo — this should be one of the earliest things run once the
matching engine is wired up, not left until UI polish (see project notes: demo
narrative risk depends on match explanations looking smart on real-ish data).

TODO: once backend persistence is implemented, populate:
  - 3-4 JobPosting records across different seniority levels, at least one on_site=True
  - 6-8 Candidate records with varied skills/locations/seniority, including some
    deliberate near-misses (wrong seniority, wrong location) to sanity-check that
    the matching engine actually discriminates rather than scoring everyone high
"""

def main():
    raise NotImplementedError("seed_mock_data: implement once backend persistence layer exists")


if __name__ == "__main__":
    main()
