/**
 * Footer Layout
 * 
 * This nested layout adds the footer to all pages that use it.
 */

import Footer from "@/components/footer"

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex flex-col flex-1">{children}</main>
      <Footer />
    </div>
  );
}
