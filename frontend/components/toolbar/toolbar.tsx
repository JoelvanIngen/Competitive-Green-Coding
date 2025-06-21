/* Navigation bar at the top of the webpage. Persistent across pages. */
"use client";

import Link from "next/link";
import { ThemeToggle } from "./theme-toggle-button";
import { JWTPayload } from "jose";
import UserInfo from "./user-info";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function Toolbar({ session }: { session: JWTPayload | null }) {
  /* For testing the admin link */
  // if (session) {
  //   session.permission_level = "admin";
  // }
  // console.log("Session fields:", session);

  return (
    <header className="
      w-full px-6 py-3 flex items-center justify-between 
      text-theme-text shadow-md
      bg-stone-50 dark:bg-stone-900 
    ">
      <div className="flex items-stretch gap-6">
        <Link
          href="/"
          className="rounded-md text-xl font-bold text-theme-text flex items-center gap-1"
        >
          <Image
            src="/images/greencodehappytransp.png"
            alt="GreenCode logo"
            width={32}
            height={32}
            priority
          />
          GreenCode
        </Link>

        <nav className="flex gap-0">
          <ToolbarLink href="/problems">Problems</ToolbarLink>
          <ToolbarLink href="/leaderboards">Leaderboards</ToolbarLink>
          <ToolbarLink href="/discuss">Discuss</ToolbarLink>
          
        </nav>
      </div>

      <div className="flex items-center gap-4">
        {session && session.permission_level === "admin" && (
          <ToolbarLink 
            href="/admin" 
            className="
              text-lime-600 font-bold
              hover:bg-stone-200 hover:border-stone-300 
              dark:hover:bg-stone-800 dark:hover:border-stone-600"
            >
            Admin
          </ToolbarLink>
        )}

        <ThemeToggle />
        <UserInfo session={session} />
      </div>
    </header>
  );
}

function ToolbarLink({ 
  href, 
  children, 
  className = "" 
}: { 
  href: string; 
  children: React.ReactNode; 
  className?: string; 
}) {
  return (
    <Link
      href={href}
      className={cn(`
        text-m font-medium
        rounded-md px-4 py-4 transition-colors
        hover:bg-stone-200 dark:hover:bg-stone-700 
        border-1 border-transparent
        hover:border-stone-100 dark:hover:border-stone-800
        `, className)}
    >
      {children}
    </Link>
  )
}
