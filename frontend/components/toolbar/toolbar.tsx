/* Navigation bar at the top of the webpage. Persistent across pages. */
"use client"

import Link from "next/link"
import { Button } from "./button-toolbar"
import { ThemeToggle } from "./theme-toggle-button"
import { JWTPayload } from "jose";
import { logout } from "@/app/(footer)/login/actions";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export default function Toolbar ({ session }: { session: JWTPayload | null }) {
  return (
    <header className="w-full px-6 py-3 flex items-center justify-between bg-theme-bg text-theme-text shadow-md">
      <div className="flex items-center gap-6">
        <Link href="/" className="text-xl font-bold text-theme-text flex items-center gap-1">
          🦉 GreenCode
        </Link>

        <nav className="flex gap-5 text-sm">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/problems">Problems</Link>
          <Link href="/leaderboards">Leaderboards</Link>
          <Link href="/discuss">Discuss</Link>
        </nav>
      </div>

      <div className="flex items-center gap-4">
        <span>🔔</span>
        <span>🔥 0</span>

        <ThemeToggle/>
        
        <UserInfo session={session} />
        
      </div>
    </header>
  )
}

/* 
  Returns Login button if the user is not logged in,
  and a dropdown menu with user options if the user is logged in. 
*/
async function UserInfo({ session }: { session: JWTPayload | null }) {
  if (!session) {
    return (
      <Button className="text-theme-text"><Link href="/login">Log in</Link></Button>
    )
  }

  const username = session.username as string;
  const firstLetter = username?.charAt(0) || 'U';

  return (
    <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Avatar>
                <AvatarFallback>{firstLetter}</AvatarFallback>
                </Avatar>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="end">
                <DropdownMenuItem>Profile</DropdownMenuItem>
                <DropdownMenuItem>Settings</DropdownMenuItem>
                
                <DropdownMenuItem onClick={() => logout()}>
                  Log out
                </DropdownMenuItem>

            </DropdownMenuContent>
        </DropdownMenu>
  )
}