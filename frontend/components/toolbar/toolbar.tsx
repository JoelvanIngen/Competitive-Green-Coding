/**
 * Navigation bar at the top of the webpage. Persistent across pages.
 * On mobile, it collapses into a hamburger menu.
 */

"use client";

import Link from "next/link";
import { ThemeToggle } from "./theme-toggle-button";
import UserInfo from "./user-info";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { useState } from "react";

import type { JWTPayload } from "@/lib/session";

/* Navigation links for the toolbar (factored out to use for both desktop and mobile) */
const navigationLinks = [
  { href: "/problems", label: "Problems" },
  // { href: "/leaderboards", label: "Leaderboards" },
  // { href: "/discuss", label: "Discuss" },
];

export default function Toolbar({ session }: { session: JWTPayload | null }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  /* For testing the admin link */
  // if (session) {
  //   session.permission_level = "admin";
  // }
  // console.log("Session fields:", session);

  return (
    <header className="
      relative w-full px-3 sm:px-6 py-3 flex items-center justify-between 
      text-theme-text shadow-md
      bg-stone-50 dark:bg-stone-900
    ">
      {/* Left Side - Logo on Desktop, Hamburger on Mobile */}
      <div className="flex items-center gap-6">
        {/* Desktop Logo & Navigation */}
        <Link
          href="/"
          className="hidden md:flex rounded-md text-xl font-bold text-theme-text items-center gap-1"
        >
          <Image
            src="/images/greencodehappytransp.png"
            alt="GreenCode logo"
            width={32}
            height={32}
            priority
          />
          <span className="inline">GreenCode</span>
        </Link>

        {/* Mobile Hamburger Menu */}
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="flex md:hidden p-2 rounded-md hover:bg-stone-200 dark:hover:bg-stone-700 transition-colors"
          aria-label="Toggle menu"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {isMobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex gap-0">
          {navigationLinks.map((link) => (
            <ToolbarLink key={link.href} href={link.href}>
              {link.label}
            </ToolbarLink>
          ))}
        </nav>
      </div>

      {/* Right Side */}
      <div className="flex items-center gap-4">
        {session && session.permission_level === "admin" && (
          <ToolbarLink
            href="/admin"
            className="
              hidden md:flex
              text-lime-600 font-bold
              hover:bg-stone-200 hover:border-stone-300 
              dark:hover:bg-stone-800 dark:hover:border-stone-600
              "
            >
            Admin
          </ToolbarLink>
        )}

        <ThemeToggle />
        <UserInfo session={session} />
      </div>

      {/* Mobile Menu */}
      <div className={`
        absolute top-full left-0 right-0 md:hidden
        bg-stone-50 dark:bg-stone-900 shadow-lg border-t border-stone-200 dark:border-stone-700 z-50
        transition-all duration-300 ease-in-out
        ${isMobileMenuOpen 
          ? 'opacity-100 transform translate-y-0' 
          : 'opacity-0 transform -translate-y-2 pointer-events-none'
        }
      `}>
        <nav className="flex flex-col p-4 gap-2">
          <MobileToolbarLink href="/" onClick={() => setIsMobileMenuOpen(false)}>
            Home
          </MobileToolbarLink>
          {navigationLinks.map((link) => (
            <MobileToolbarLink 
              key={link.href} 
              href={link.href} 
              onClick={() => setIsMobileMenuOpen(false)}
            >
              {link.label}
            </MobileToolbarLink>
          ))}
          
          {session && session.permission_level === "admin" && (
            <MobileToolbarLink 
              href="/admin" 
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-lime-600 font-bold"
            >
              Admin
            </MobileToolbarLink>
          )}
        </nav>
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

function MobileToolbarLink({ 
  href, 
  children, 
  onClick,
  className = "" 
}: { 
  href: string; 
  children: React.ReactNode; 
  onClick?: () => void;
  className?: string; 
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(`
        text-m font-medium
        rounded-md px-4 py-3 transition-colors
        hover:bg-stone-200 dark:hover:bg-stone-700 
        border-1 border-transparent
        hover:border-stone-100 dark:hover:border-stone-800
        block w-full text-left
        `, className)}
    >
      {children}
    </Link>
  )
}
