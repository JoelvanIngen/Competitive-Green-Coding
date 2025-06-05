"use client"

import Link from "next/link"

export default function Footer() {
  return (
    <footer className="w-full px-6 py-4 border-t border-muted bg-theme-bg text-sm text-muted-foreground">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="text-center md:text-left">
          © 2025 GreenCode
        </div>
        <div className="flex gap-4 justify-center md:justify-end">
          <Link href="/help" className="hover:underline">
            Help
          </Link>
          <Link href="/terms" className="hover:underline">
            Terms
          </Link>
          <Link href="/privacy" className="hover:underline">
            Privacy Policy
          </Link>
        </div>
      </div>
    </footer>
  )
}
