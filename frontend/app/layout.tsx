import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { ThemeProvider } from "@/components/theme-provider"
import Toolbar from "@/components/toolbar/toolbar";
import Footer from "@/components/footer"
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
  description: "Competitive Green Coding is pretty cool"
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
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
            <Toolbar />

            {/* Main content area (page.tsx is rendered here). */}
            <main >{children}</main>

        </ThemeProvider>
        <Footer />
        <CookieConsent />
      </body>
    </html>
  );
}