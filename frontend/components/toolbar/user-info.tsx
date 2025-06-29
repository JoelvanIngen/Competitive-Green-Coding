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
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "./button-toolbar"
import Link from "next/link"

import type { JWTPayload } from "@/lib/session";

// Import avatar variants from JSON file
import avatarVariantsData from '@/public/images/avatars/avatar_id.json'
const avatarVariants: string[] = avatarVariantsData;

// Shared style variables
const dropdownItemStyle = "h-12 sm:h-auto px-4 sm:px-2 flex items-center text-xl sm:text-sm cursor-pointer data-[highlighted]:bg-stone-100 dark:hover:bg-stone-800"

/*
  Returns Login button if the user is not logged in,
  and a dropdown menu with user options if the user is logged in.
*/
export default function UserInfo({ session }: { session: JWTPayload | null }) {
    /* Not logged in -> just a login button */
    if (!session) {
        return (
            <Button className="text-theme-text"><Link href="/login">Log in</Link></Button>
        )
    }

    /* Get username */
    const username = session.username as string;
    const firstLetter = username?.charAt(0) || 'U';

    /* Get avatar src from the avatar_id */
    const avatarIndex = session.avatar_id as number; // Get the avatar index from the session
    const avatarName: string = avatarVariants[avatarIndex]
    const avatarSrc: string = `/images/avatars/${avatarName}/full.png`

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <button
                    className="
                  flex items-center gap-2 p-2 rounded-md
                  select-none
                  cursor-pointer

                bg-stone-50  dark:bg-stone-950
                  transition-colors
                hover:bg-stone-300 dark:hover:bg-stone-800
                  border-1 border-stone-300 dark:border-stone-600
              ">

                    <Avatar className="h-10 w-10">
                        <AvatarImage src={avatarSrc} />
                        <AvatarFallback>{firstLetter}</AvatarFallback>
                    </Avatar>

                    <span className="hidden sm:inline text-base font-bold">{username}</span>

                </button>
            </DropdownMenuTrigger>

            <DropdownMenuContent
                align="end"
                className="
    bg-white dark:bg-stone-950
    border-1 border-stone-300 dark:border-stone-600
    p-1 sm:p-1
    text-base sm:text-sm
  "
            >
                <DropdownMenuItem asChild>
                    <Link
                        href={`/u/${username}`}
                        className={dropdownItemStyle}
                    >
                        Profile
                    </Link>
                </DropdownMenuItem>

                <DropdownMenuItem asChild>
                    <Link href="/settings" className={dropdownItemStyle}>
                        Settings
                    </Link>
                </DropdownMenuItem>

                <DropdownMenuItem
                    className={dropdownItemStyle}
                    onClick={() => {
                        fetch('/api/auth/logout', {
                            method: 'GET',
                            credentials: 'include'
                        }).then(() => {
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
