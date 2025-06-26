/* Button to switch between light and dark mode. Part of navbar. */

"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

// Shared style variables
const themeComponentStyle = "border-1 border-stone-300 dark:border-stone-600"
const dropdownColor = "bg-white dark:bg-stone-800"
const dropdownItemStyle = "data-[highlighted]:bg-stone-200 dark:hover:bg-stone-700 cursor-pointer"

export function ThemeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="icon" 
          className={cn(themeComponentStyle, "cursor-pointer bg-stone-50 dark:bg-stone-900 hover:bg-stone-200 dark:hover:bg-stone-700" )}
        >
          <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent 
        align="end"
        className={cn(dropdownColor, themeComponentStyle)}
      >
        <DropdownMenuItem 
          onClick={() => setTheme("light")}
          className={dropdownItemStyle}
        >
          Light
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => setTheme("dark")}
          className={dropdownItemStyle}
        >
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => setTheme("system")}
          className={dropdownItemStyle}
        >
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}