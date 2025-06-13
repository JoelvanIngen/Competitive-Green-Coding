// -----------------------------------------------------------------------------
// Mock profile API route  –  GET /api/profile/:username
// -----------------------------------------------------------------------------


import { NextResponse } from "next/server";
import type { ProfileData } from "@/app/(footer)/u/[username]/types";

export async function GET(
  _req: Request,
  { params }: { params: { username: string } }
) {
  const { username } = params;

  // -------------------------------------------------------------------------
  // Mock data – replace with real DB call later
  // -------------------------------------------------------------------------
  const data: ProfileData = {
    username,
    avatarUrl: `https://api.dicebear.com/8.x/identicon/svg?seed=${username}`,
    rank: Math.floor(Math.random() * 5_000_000) + 1,
    greenScore: Math.floor(Math.random() * 1000),

    solved: {
      easy: 3,
      medium: 0,
      hard: 0,
      total: 580, // pretend there are 580 total problems in your DB
    },


    recentSubmissions: [
      { id: "1", title: "Check if The Number is Fascinating", when: "8 months ago" },
      { id: "2", title: "Root Equals Sum of Children", when: "1 year ago" },
      { id: "3", title: "Add Two Integers", when: "1 year ago" },
    ],

    recentDiscussions: [
      { id: "d1", title: "Why is my DFS LLVM-Optimized?", when: "3 weeks ago" },
      { id: "d2", title: "Energy-efficient solutions ranking idea", when: "2 months ago" },
    ],

    languageStats: [
      { language: "C",        solved: 2 },
      { language: "Python3",  solved: 1 },
    ],
  };

  return NextResponse.json(data, { status: 200 });
}
