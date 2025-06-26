import { NextResponse, NextRequest } from "next/server";
import { formatDistanceToNowStrict } from "date-fns";

import type { ProfileData, RecentItem } from "@/app/(footer)/u/[username]/types";
import type { UserProfileBackendResponse } from "@/types/api";

const BACKEND_URL = process.env.BACKEND_API_URL || "http://server:8080/api";

// helper: ISO → “3 h ago”
function toRelative(iso: string): string {
  return formatDistanceToNowStrict(new Date(iso), { addSuffix: true });
}

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ username: string }> }
) {
  try {
    const { username } = await params;
    const res = await fetch(`${BACKEND_URL}/profile/${username}`);

    if (!res.ok) {
      const text = await res.text();
      console.error("Profile back-end error:", text);
      return NextResponse.json(
        { error: "Failed to fetch profile" },
        { status: res.status }
      );
    }

    /* ---------- transform back-end → front-end shape ---------- */
    const raw: UserProfileBackendResponse = await res.json();

    const profile: ProfileData = {
      username: raw.username,
      avatarUrl: `/images/avatars/${raw.avatar_id}.png`, // pick your path
      rank: undefined,           // not supplied – leave empty for now
      greenScore: undefined,     // "
      solved: raw.solved,
      languageStats: raw.language_stats,
      recentSubmissions: raw.recent_submissions.map<RecentItem>((s) => ({
        id: s.id,
        title: s.title,
        when: toRelative(s.created_at),
      })),
      recentDiscussions: [],     // API doesn’t supply this (yet)
    };

    return NextResponse.json(profile);
  } catch (err) {
    console.error("Profile route error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}


// // -----------------------------------------------------------------------------
// // Mock profile API route  –  GET /api/profile/:username
// // -----------------------------------------------------------------------------

// import { NextResponse, NextRequest } from "next/server";
// import type { ProfileData } from "@/app/(footer)/u/[username]/types";

// // Mock version - commented out to use database version
// /*
// export async function GET(
//   _req: Request,
//   { params }: { params: { username: string } }
// ) {
//   const { username } = params;

//   // -------------------------------------------------------------------------
//   // Mock data – replace with real DB call later
//   // -------------------------------------------------------------------------
//   const data: ProfileData = {
//     username,
//     avatarUrl: `https://api.dicebear.com/8.x/identicon/svg?seed=${username}`,
//     rank: Math.floor(Math.random() * 5_000_000) + 1,
//     greenScore: Math.floor(Math.random() * 1000),

//     solved: {
//       easy: 3,
//       medium: 0,
//       hard: 0,
//       total: 580, // pretend there are 580 total problems in your DB
//     },


//     recentSubmissions: [
//       { id: "1", title: "Check if The Number is Fascinating", when: "8 months ago" },
//       { id: "2", title: "Root Equals Sum of Children", when: "1 year ago" },
//       { id: "3", title: "Add Two Integers", when: "1 year ago" },
//     ],

//     recentDiscussions: [
//       { id: "d1", title: "Why is my DFS LLVM-Optimized?", when: "3 weeks ago" },
//       { id: "d2", title: "Energy-efficient solutions ranking idea", when: "2 months ago" },
//     ],

//     languageStats: [
//       { language: "C", solved: 2 },
//       { language: "Python3", solved: 1 },
//     ],
//   };

//   return NextResponse.json(data, { status: 200 });
// }
// */

// // -----------------------------------------------------------------------------
// // Database-connected profile API route  –  GET /api/profile/:username
// // -----------------------------------------------------------------------------

// const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';

// export async function GET(_req: NextRequest, { params }: { params: Promise<{ username: string }> }) {
//   try {
//     const { username } = await params;

//     const backendUrl = `${BACKEND_URL}/profile/${username}`;

//     try {
//       const response = await fetch(backendUrl, {
//         method: 'GET',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//       });

//       if (!response.ok) {
//         const text = await response.text();
//         console.error('Backend error response:', {
//           status: response.status,
//           statusText: response.statusText,
//           body: text
//         });
//         return NextResponse.json(
//           { error: 'Failed to fetch profile' },
//           { status: response.status }
//         );
//       }

//       const data = await response.json();
//       return NextResponse.json(data);
//     } catch (fetchError) {
//       console.error('Fetch error:', fetchError);
//       throw fetchError;
//     }
//   } catch (error) {
//     console.error('API request error:', error);
//     return NextResponse.json(
//       { error: 'Internal server error' },
//       { status: 500 }
//     );
//   }
// }
