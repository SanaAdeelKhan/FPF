// Candidate upload flow: guided prompts on "what are you genuinely best at" —
// NOT a JD-tailoring form, since candidates never see the JD at this stage.

export default function CandidateUpload() {
  // TODO: form fields: full_name, email, location, seniority_level, years_experience,
  //   availability, open_to_remote
  // TODO: CV text input (paste or upload — 2-page guided prompts)
  // TODO: submit -> api.uploadCandidate(...)
  return (
    <div>
      <h1>Tell us what you're best at</h1>
      <p>No job description to reverse-engineer — just describe your actual strengths.</p>
      {/* form goes here */}
    </div>
  );
}
