/**
 * Root layout for the Next.js application.
 * This layout wraps the entire application and provides global styles, fonts, and components.
 */

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { getSession } from "@/lib/session";
import { ThemeProvider } from "@/components/theme-provider"
import Toolbar from "@/components/toolbar/toolbar";
import { Toaster } from "@/components/ui/sonner"
import CookieConsent from "@/components/cookie-consent"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Competitive Green Coding",
  description: "Saving the world, one line of code at a time.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  /* JWT session cookie is fetched here and passed to toolbar. */
  const session = await getSession()

  return (

    /* suppressHydrationWarning was added because it is a best practice for ThemeProvider. */
    <html lang="en" suppressHydrationWarning>
      {/* Our Tailwind classes for body should be applied at the bottom of globals.css.
      They function as our default settings.
      The classes below were set by shadcn to ensure correct behavior. */}
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        {/* Theme provider handles management of light and dark theme. */}
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >

          {/* Toolbar component is persistent across pages. */}
          <Toolbar session={session} />

          {/* Main content area (page.tsx is rendered here). */}
          <main >{children}</main>

          {/* Sonner toast notifications can be called on any page. */}
          <Toaster position="top-center" richColors />
          
          {/* Cookie consent pop-up. */}
          <CookieConsent />

        </ThemeProvider>
      </body>
    </html>
  );
}