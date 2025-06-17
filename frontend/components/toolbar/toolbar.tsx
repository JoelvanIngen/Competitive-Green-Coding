/* Navigation bar at the top of the webpage. Persistent across pages. */
"use client"

import Link from "next/link"
import { ThemeToggle } from "./theme-toggle-button"
import { JWTPayload } from "jose";
import UserInfo from "./user-info"
import Image from "next/image"

export default function Toolbar ({ session }: { session: JWTPayload | null }) {
  return (
    <header className="w-full px-6 py-3 flex items-center justify-between bg-theme-bg text-theme-text shadow-md">
      <div className="flex items-center gap-6">
        <Link href="/" className="text-xl font-bold text-theme-text flex items-center gap-1">
          <Image
            src="/images/greencodehappytransp.png"
            alt="GreenCode logo"
            width={32}
            height={32}
            priority
          />
          GreenCode
        </Link>

        <nav className="flex gap-5 text-sm">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/problems">Problems</Link>
          <Link href="/leaderboards">Leaderboards</Link>
          <Link href="/discuss">Discuss</Link>
        </nav>
      </div>

      <div className="flex items-center gap-4">
        <ThemeToggle/>

        <UserInfo session={session} />

      </div>
    </header>
  )
}
