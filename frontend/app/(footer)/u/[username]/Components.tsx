/* -----------------------------------------------------------------------------
   Profile page components (widgets)

   This file contains reusable React components/widgets for the user profile page,
   such as the solved ring, green score, recent submissions table, and language list.
   These components are used to display various sections of the user profile in a
   modular and visually appealing way.
   ----------------------------------------------------------------------------- */

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
const RADIUS = 64;
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
}: ProfileData['solved']) {
  /* ---------------- maths ---------------- */
  const solved = easy + medium + hard;
  const safeSolved = solved === 0 ? 1 : solved;  // avoid /0

  const pctEasy = easy / safeSolved;           // ► use solved!
  const pctMed = medium / safeSolved;
  const pctHard = hard / safeSolved;

  /* helper: return { dasharray, dashoffset } for an SVG circle
     len is a fraction   0 – 1  (e.g. 0.33 === 33 %)                */
  const arc = (len: number) => ({
    strokeDasharray: `${len * CIRCUMFERENCE} ${CIRCUMFERENCE}`,
    strokeDashoffset: 0,                      // always start at 0°
  });

  return (
    <Card className="flex flex-col items-center justify-center flex-1 min-w-0 shadow-sm">
      <CardContent className="p-6 flex flex-col items-center">
        {/* ---------- Ring + centred numbers ---------- */}
        <div className="relative w-40 h-40">
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 160 160"
            className="-rotate-90"            /* start at top */
          >
            {/* thin grey base */}
            <circle
              cx="80" cy="80" r={RADIUS}
              strokeWidth="12"
              className="stroke-muted/30 fill-none"
            />

            {/* ─── three coloured arcs (drawn bottom-up) ─────────────────────────── */}

            {/* hard  – full ring (bottom layer) */}
            <circle
              cx="80" cy="80" r={RADIUS}
              strokeWidth="12"
              className="stroke-red-400 fill-none transition-all duration-700"
              strokeLinecap="round"
              style={arc(1)}                             // 100 %
            />

            {/* medium – cumulative easy+medium (middle layer) */}
            <circle
              cx="80" cy="80" r={RADIUS}
              strokeWidth="12"
              className="stroke-yellow-400 fill-none transition-all duration-700"
              strokeLinecap="round"
              style={arc(pctEasy + pctMed)}              // easy + medium
            />

            {/* easy   – only easy (top layer) */}
            <circle
              cx="80" cy="80" r={RADIUS}
              strokeWidth="12"
              className="stroke-green-400 fill-none transition-all duration-700"
              strokeLinecap="round"
              style={arc(pctEasy)}                       // easy only
            />

          </svg>

          {/* centred text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <p className="text-5xl font-extrabold leading-none">{solved}</p>
            <p className="text-xs text-muted-foreground">/ {total}</p>
          </div>
        </div>

        {/* legend */}
        <div className="flex gap-2 mt-3 text-[11px]">
          <span className="text-green-400">Easy&nbsp;{easy}</span>
          <span className="text-yellow-400">Med&nbsp;{medium}</span>
          <span className="text-red-400">Hard&nbsp;{hard}</span>
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
import Link from "next/link";

export function RecentTable({
  items = [],
  emptyMsg,
}: {
  items?: RecentItem[];
  emptyMsg: string;
}) {
  const showItems = items.slice(0, 3);   // show at most 3 most-recent

  return (
    <Card className="w-full shadow-sm">           {/* ⬅ matching width */}
      <CardContent className="p-0 divide-y">
        {showItems.length === 0 && (
          <p className="p-4 text-sm text-muted-foreground text-center">
            {emptyMsg}
          </p>
        )}

        {showItems.map((item) => (
          <Link                                                 /* ⬅ clickable row */
            key={item.id}
            href={`/submission?id=${item.id}`}
            className="p-4 flex justify-between hover:bg-muted/10 transition-colors"
          >
            <span className="truncate max-w-[70%] text-sm">{item.title}</span>
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              {item.when}
            </span>
          </Link>
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
