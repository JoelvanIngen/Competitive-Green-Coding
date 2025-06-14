/**
 * This file contains the UserInfo component,
 * which shows a login button if the user is not logged in,
 * or a dropdown menu with user options if the user is logged in.
 */

"use client";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "./button-toolbar"
import { JWTPayload } from "jose";
import Link from "next/link"

/* 
  Returns Login button if the user is not logged in,
  and a dropdown menu with user options if the user is logged in. 
*/
export default function UserInfo({ session }: { session: JWTPayload | null }) {
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
                <DropdownMenuItem 
                    onClick={() => {
                        // Call logout endpoint
                        fetch('/api/auth/logout', { 
                        method: 'GET', 
                        credentials: 'include'
                        }).then(() => {
                        // Force a full page reload after logout completes
                        window.location.href = '/login';
                        });
                    }}
                >
                Log out
                </DropdownMenuItem>

            </DropdownMenuContent>
        </DropdownMenu>
  )
}