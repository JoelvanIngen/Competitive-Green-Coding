// -----------------------------------------------------------------------------
// terms.tsx (TermsPage)
//
// Static “Terms of Use” page for GreenCode.
// Displays legal terms; no dynamic logic.
// -----------------------------------------------------------------------------

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 text-theme-text">
      <h1 className="text-3xl font-bold mb-6"> GreenCode Terms of Use</h1>
      <p className="mb-4 text-muted-foreground">
        By using GreenCode, you agree to the following terms and conditions...
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">1. Use of the Platform</h2>
      <p className="mb-4 text-muted-foreground">
        You may use GreenCode for personal and educational purposes only unless otherwise authorized.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">2. User Content</h2>
      <p className="mb-4 text-muted-foreground">
        By submitting code, you grant us the right to store and evaluate it for performance and quality scoring.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">3. Termination</h2>
      <p className="mb-4 text-muted-foreground">
        We reserve the right to suspend accounts or remove content that violates our guidelines.
      </p>

      <p className="text-muted-foreground mt-8">
        These terms are subject to change.
      </p>
    </div>
  )
}
