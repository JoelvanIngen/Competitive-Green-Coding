// ─────────────────────────────────────────────────────────────
// LEADERBOARD IMPLEMENTATION GUIDE  (T-A-R-R workflow)
// ─────────────────────────────────────────────────────────────
// T  = add / confirm **T**ypes            (types/api.ts)
// A  = add / confirm **A**PI helper       (lib/api.ts)
// R1 = create proxy **R**oute             (app/api/leaderboard/route.ts)
// R2 = build **R**eact page               (server component + optional client)
// ─────────────────────────────────────────────────────────────
// Mini tutorial over hoe ik het had gedaan met leaderboard kijk to-do 1 t/m 3 zijn het belangrijkst
// Als je 1 t/m 3 hebt gedaan dan ben je verbonden en kan je de gepakte json verwerken hoe je wil in de pages. 



// TODO-1  ✏️  Confirm / add TypeScript models
// --------------------------------------------------
// 🔸 File:  frontend/types/api.ts
//
// • Voeg de verwachte json toe zoals hier onder voor leaderbpoard is gedaan:

export interface ScoreEntry {
  user_id: string;
  user_name: string;
  score: number;
}

export interface ProblemLeaderboard {
  problem_id: number;
  problem_name: string;
  problem_language: string;
  problem_difficulty: number;
  scores: ScoreEntry[];
}


// TODO-2  ⚡  Add a typed helper that hits *our own* NEXT route
// -----------------------------------------------------------
// 🔸 File:  frontend/lib/api.ts
// Hier shcrijf je de API die verwijst naar de route, hij moet simpelweg de route pakken naar
// de api folder waar route.ts staat en hij wacht op een antwoord van die route.ts om een json te ontvangen.

import type { ProblemLeaderboard } from '@/types/api';

const base = process.env.NEXT_PUBLIC_API_URL ?? '';   // works on server & browser

export const leaderboardApi = {
  /**
   * Fetch a slice of the leaderboard.
   * @param id         Problem ID
   * @param firstRow   inclusive
   * @param lastRow    exclusive
   */
  getLeaderboard: (id: number, firstRow = 0, lastRow = 20) =>
    fetchApi<ProblemLeaderboard>(
      `${base}/api/leaderboard?problem_id=${id}&first_row=${firstRow}&last_row=${lastRow}`,
    ),
};


// TODO-3  🔄  Create the proxy route (server-only)
// -----------------------------------------------
// 🔸 File:  src/app/api/leaderboard/route.ts
// Die api die net is gedaan naar de route.ts pakt nu dus van deze file de daadwerkelijke data van de backend
// Deze route.ts file verbind daadwerkelijk met de backend en stuurt het terug naar de api die verbond met deze route

import { NextRequest, NextResponse } from 'next/server';

const BACKEND = process.env.BACKEND_URL;         // e.g. http://backend:8080
const AUTH = process.env.BACKEND_JWT ?? '';   // secret stays on the server

export async function GET(req: NextRequest) {
  const url = req.nextUrl;
  const id = url.searchParams.get('problem_id');
  const first = url.searchParams.get('first_row');
  const last = url.searchParams.get('last_row');

  if (!id) {
    return NextResponse.json({ error: 'problem_id is required' }, { status: 400 });
  }

  const upstream = await fetch(
    `${BACKEND}/leaderboard/${id}?first_row=${first}&last_row=${last}`,
    { headers: { Authorization: AUTH } },
  );

  if (!upstream.ok) {
    return NextResponse.json({ error: 'Backend failure' }, { status: 502 });
  }

  // Optional edge-cache for 30 s
  const data = await upstream.json();
  return NextResponse.json(data, {
    status: 200,
    headers: { 'Cache-Control': 's-maxage=30, stale-while-revalidate=30' },
  });
}

// todo 4 en 5 zijn implementatie voorbeelden hoe in de page en clientpage de json data is verwerkt in een leaderboard
// TODO-4  🖥️  Fetch in a **server component** first
// ------------------------------------------------
// 🔸 File:  src/app/(routes)/leaderboard/page.tsx

import { leaderboardApi } from '@/lib/api';

export default async function LeaderboardPage({ searchParams }: {
  searchParams: { id?: string };
}) {
  const id = Number(searchParams.id);
  if (!id) return <p>Missing problem id</p>;

  // Fetch first 5 rows on the server for instant paint (SSR)
  const initial = await leaderboardApi.getLeaderboard(id, 0, 5);

  return (
    <ClientLeaderboard
      problemId={id}
      initialData={initial}
      pageSize={5}
    />
  );
}


// TODO-5  🛠️  (Optional) Build the client component for interactivity
// ------------------------------------------------------------------
// 🔸 File:  src/app/(routes)/leaderboard/ClientLeaderboard.tsx
'use client';
import { useState } from 'react';
import type { ProblemLeaderboard } from '@/types/api';
import { leaderboardApi } from '@/lib/api';

export default function ClientLeaderboard({
  initialData,
  problemId,
  pageSize,
}: {
  initialData: ProblemLeaderboard;
  problemId: number;
  pageSize: number;
}) {
  const [data, setData] = useState(initialData);
  const [page, setPage] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadMore() {
    setBusy(true);
    try {
      const next = await leaderboardApi.getLeaderboard(
        problemId,
        page * pageSize,
        (page + 1) * pageSize,
      );
      setData(prev => ({
        ...prev,
        scores: [...prev.scores, ...next.scores],
      }));
      setPage(p => p + 1);
    } catch (e) {
      setError('Could not load more scores');
    } finally {
      setBusy(false);
    }
  }

  /* ---------- Render ---------- */
  return (
    <div className="space-y-4">
      {/* Table of scores */}
      <table className="w-full text-sm border">
        <thead><tr><th>User</th><th>Score</th></tr></thead>
        <tbody>
          {data.scores.map((s, i) => (
            <tr key={i}>
              <td>{s.user_name}</td>
              <td>{s.score}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <button
        onClick={loadMore}
        disabled={busy}
        className="rounded bg-blue-600 px-3 py-1 text-white disabled:opacity-50"
      >
        {busy ? 'Loading…' : 'Load more'}
      </button>

      {error && <p className="text-red-600">{error}</p>}
    </div>
  );
}
