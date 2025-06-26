"use client";
/* ---------------------------------------------------------------------------
   Client widgets for the profile page  (shadcn + Tailwind)
   --------------------------------------------------------------------------- */
import React from 'react';
import {
  Card,
  CardContent,
  CardTitle,
} from "@/components/ui/card";
import type { ProfileData, RecentItem, LanguageStat } from "./types";

/* Helpers ------------------------------------------------------------------ */
const RADIUS = 56;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
function radialStroke(percent: number) {
  return CIRCUMFERENCE - (percent / 100) * CIRCUMFERENCE;
}

/* Solved Ring -------------------------------------------------------------- */
export function SolvedRing({
  easy,
  medium,
  hard,
  total,
}: ProfileData["solved"]) {
  const solved = easy + medium + hard;
  const percent = (solved / total) * 100;

  return (
    <Card className="flex flex-col items-center justify-center w-full lg:w-1/2 shadow-sm">
      <CardContent className="p-6 flex flex-col items-center">
        <svg
          width="140"
          height="140"
          viewBox="0 0 140 140"
          className="rotate-[270deg]"
        >
          <circle
            cx="70"
            cy="70"
            r={RADIUS}
            strokeWidth="12"
            className="stroke-muted/30 fill-transparent"
          />
          <circle
            cx="70"
            cy="70"
            r={RADIUS}
            strokeWidth="12"
            strokeDasharray={`${CIRCUMFERENCE} ${CIRCUMFERENCE}`}
            strokeDashoffset={radialStroke(percent)}
            className="stroke-primary transition-all duration-700 ease-out fill-transparent"
            strokeLinecap="round"
          />
        </svg>

        <div className="text-center -mt-8">
          <p className="text-4xl font-semibold">{solved}</p>
          <p className="text-xs text-muted-foreground tracking-wide">
            / {total} solved
          </p>
          <div className="flex gap-2 mt-1 text-[11px]">
            <span className="text-green-400">Easy {easy}</span>
            <span className="text-yellow-400">Med {medium}</span>
            <span className="text-red-400">Hard {hard}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/* Green Score -------------------------------------------------------------- */
export function GreenScore({ score }: { score?: number }) {
  if (score === undefined) return null;         // nothing to show

  return (
    <Card className="flex flex-col items-center justify-center w-full lg:w-1/2 bg-emerald-600/5 shadow-sm">
      <CardContent className="p-6 text-center">
        <CardTitle className="text-4xl font-black text-emerald-400">
          {score}
        </CardTitle>
        <p className="text-xs tracking-wide text-muted-foreground">
          Total&nbsp;Green&nbsp;Score
        </p>
      </CardContent>
    </Card>
  );
}

/* Recent Table ------------------------------------------------------------- */
export function RecentTable({
  items = [],
  emptyMsg,
}: {
  items?: RecentItem[];
  emptyMsg: string;
}) {
  return (
    <Card>
      <CardContent className="p-0 divide-y">
        {items.length === 0 && (
          <p className="p-4 text-sm text-muted-foreground text-center">
            {emptyMsg}
          </p>
        )}
        {items.map((item) => (
          <div key={item.id} className="p-4 flex justify-between">
            <span className="truncate max-w-[70%] text-sm">{item.title}</span>
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              {item.when}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

/* Language List ------------------------------------------------------------ */
export function LanguageList({ stats }: { stats: LanguageStat[] }) {
  return (
    <ul className="space-y-1">
      {stats.map((l) => (
        <li
          key={l.language}
          className="flex justify-between text-sm tracking-tight"
        >
          <span>{l.language}</span>
          <span className="font-medium">{l.solved}</span>
        </li>
      ))}
    </ul>
  );
}
