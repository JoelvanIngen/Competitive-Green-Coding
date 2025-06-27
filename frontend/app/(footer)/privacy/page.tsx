// -----------------------------------------------------------------------------
// privacy.tsx (PrivacyPolicyPage)
//
// Static “Privacy Policy” page for GreenCode.
// Purely presentational: renders legal copy, no props or data fetching.
// -----------------------------------------------------------------------------

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 text-theme-text">
      <h1 className="text-3xl font-bold mb-6"> GreenCode Privacy Policy</h1>
      <p className="mb-4 text-muted-foreground">
        This Privacy Policy describes how GreenCode collects, uses, and protects your information when you use our website.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">1. Information We Collect</h2>
      <p className="mb-4 text-muted-foreground">
        We may collect limited personal information necessary to provide our services, such as functional cookies, login data, and code submissions.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">2. How We Use Your Information</h2>
      <p className="mb-4 text-muted-foreground">
        We use your information to operate the site, personalize your experience, and improve service quality.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">3. Cookie Usage</h2>
      <p className="mb-4 text-muted-foreground">
        We use functional cookies to remember your preferences and keep you logged in. You can learn more about cookies on our homepage.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">4. Data Retention</h2>
      <p className="mb-4 text-muted-foreground">
        We retain user data only as long as necessary to fulfill our service obligations or legal requirements.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">5. Your Rights</h2>
      <p className="mb-4 text-muted-foreground">
        You may request access to or deletion of your data by contacting us. We comply with applicable data protection laws.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-2">6. Contact</h2>
      <p className="text-muted-foreground">
        If you have questions about this policy, please contact us at support@greencode.com.
      </p>
    </div>
  )
}
