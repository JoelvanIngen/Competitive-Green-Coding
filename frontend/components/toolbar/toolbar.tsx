"use client"

import Link from "next/link"
import { Button } from "@/components/toolbar/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"

export default function Toolbar() {
  return (
    <header className="w-full px-6 py-3 flex items-center justify-between bg-theme-bg text-theme-text shadow-md">
      <div className="flex items-center gap-6">
        <Link href="/" className="text-xl font-bold text-theme-text flex items-center gap-1">
          🦉 GreenCode
        </Link>

        <nav className="flex gap-5 text-sm">
          {/* <Link href="/explore">Explore</Link> */}
          <Link href="/problems">Problems</Link>
          <Link href="/contest">Leaderboards</Link>
          <Link href="/discuss">Discuss</Link>
        </nav>
      </div>

      <div className="flex items-center gap-4">
        <span>🔔</span>
        <span>🔥 0</span>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Avatar>
              <AvatarFallback>U</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button className="text-theme-text"><Link href="/login">Log in</Link></Button>
      </div>
    </header>
  )
}
