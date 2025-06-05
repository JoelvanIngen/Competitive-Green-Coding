import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Toolbar from "@/components/toolbar/toolbar"; // ✅ Import Toolbar component

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
    <html lang="en" className="dark">
      
      {/* Our Tailwind classes for body should be applied at the bottom of globals.css. 
      They function as our default settings. 
      The classes below were set by shadcn to ensure correct behavior. */}
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* Toolbar component is persistent across pages. */}
        <Toolbar />

        {/* Main content area (page.tsx is rendered here). It's size is constrained by the classes below: padding at the top and margins on the left and right. */}
        <main className="pt-16 mx-8">{children}</main>
      </body>
    </html>
  );
}
