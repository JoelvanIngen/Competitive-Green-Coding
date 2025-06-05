import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Toolbar from "@/components/toolbar"; // ✅ Import Toolbar component

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
  description: "Competitive Green Coding is pretty cool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-theme-bg text-theme-text`}
      >
        <Toolbar /> {/* ✅ Add Toolbar so it's shown on every page */}
        <main>{children}</main> {/* Give space below the fixed toolbar */}
      </body>
    </html>
  );
}
