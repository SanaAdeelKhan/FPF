// Employer posting flow: title + seniority + years ONLY on the visible form.
// The hidden JD fields exist in the data model (see api.ts / backend) but should
// be collected in a separate, clearly-labeled "internal, hidden from candidates"
// section — the UI itself should reinforce the product's core promise.

export default function EmployerPost() {
  // TODO: form state for title, seniority_level, years_experience_required, company_name
  // TODO: separate collapsed/labeled section for hidden_requirements
  // TODO: submit -> api.createPosting(...)
  return (
    <div>
      <h1>Post a role</h1>
      <p>Candidates will only ever see the title, seniority, and years required.</p>
      {/* form goes here */}
    </div>
  );
}
