// This is the "wow moment" screen: match % + plain-language explanation, with the
// full JD unlocked only once shortlisted. Keep the explanation prominent — it's
// what makes the match feel earned rather than arbitrary.

export default function ShortlistReveal() {
  // TODO: fetch MatchResult via api.runMatch or a stored result
  // TODO: if shortlisted, call api.revealJd to show the full description
  // TODO: render factor_scores as a simple breakdown (skills/location/seniority/availability)
  return (
    <div>
      <h1>Match result</h1>
      {/* score + explanation + (conditionally) unlocked JD go here */}
    </div>
  );
}
