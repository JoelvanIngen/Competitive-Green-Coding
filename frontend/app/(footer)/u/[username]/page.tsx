// -----------------------------------------------------------------------------
// User Profile page (Server Component)
//
// This page displays a compact user profile, including avatar, rank, solved problems,
// language stats, and recent submissions. It fetches user data and renders the profile
// using modular UI components. Used for viewing individual user stats and activity.
// -----------------------------------------------------------------------------
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { formatDistanceToNowStrict } from "date-fns";

import {
  Card,
  CardHeader,
  CardContent,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import type { ProfileData } from "./types";
import {
  SolvedRing,
  GreenScore,
  RecentTable,
  LanguageList,
} from "./Components";
import { profileApi } from "@/lib/api";

/* ---------------------------------------------------------------------------
   Metadata
--------------------------------------------------------------------------- */
export const metadata: Metadata = {
  title: "User Profile – Competitive Green Coding",
};

/* ---------------------------------------------------------------------------
   Page
--------------------------------------------------------------------------- */
interface PageProps {
  params: Promise<{ username: string }>;
}

export default async function ProfilePage({ params }: PageProps) {
  const { username } = await params;
  let profileResponse: import("@/types/api").ProfileResponse;
  try {
    profileResponse = await profileApi.getUserProfile(username);
  } catch (error) {
    return notFound();
  }
  // Convert ProfileResponse to ProfileData, for avatarUrl and recentSubmissions
  const profile: ProfileData = {
    ...profileResponse,
    avatarUrl:
      profileResponse.avatarUrl ||
      `https://api.dicebear.com/8.x/identicon/svg?seed=${profileResponse.username}`,
    recentSubmissions: profileResponse.recentSubmissions.map((s, idx) => {
      const date = new Date(s.createdAt);
      return {
        id: s.submission_id || `${idx}-${s.title}`,
        title: s.title,
        when: isNaN(date.getTime()) ? '' : formatDistanceToNowStrict(date, { addSuffix: true }),
      };
    }),
    ...(profileResponse.recentDiscussions && {
      recentDiscussions: profileResponse.recentDiscussions.map((d, idx) => {
        const date = new Date(d.createdAt);
        return {
          id: d.id || `${idx}-${d.title}`,
          title: d.title,
          when: isNaN(date.getTime()) ? '' : formatDistanceToNowStrict(date, { addSuffix: true }),
        };
      }),
    }),
  };

  return (
    <div className="container mx-auto grid lg:grid-cols-[280px_1fr] gap-6 py-6">
      {/* -------------------------------------------------------------------
         Sidebar
      -------------------------------------------------------------------- */}
      <aside className="space-y-6">
        {/* Avatar + rank */}
        <Card>
          <CardHeader className="flex flex-col items-center gap-2">
            <Avatar className="w-24 h-24">
              <AvatarImage src={profile.avatarUrl} alt={profile.username} />
              <AvatarFallback>
                {profile.username.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <CardTitle className="text-lg">{profile.username}</CardTitle>
            {profile.rank !== undefined && (
              <p className="text-xs text-muted-foreground">
                Rank&nbsp;∼{profile.rank.toLocaleString()}
              </p>
            )}
          </CardHeader>
        </Card>

        {/* Language stats */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Solved by Language</CardTitle>
          </CardHeader>
          <CardContent>
            <LanguageList stats={profile.languageStats} />
          </CardContent>
        </Card>
      </aside>

      {/* -------------------------------------------------------------------
         Main
      -------------------------------------------------------------------- */}
      <section className="space-y-6">
        {/* Top bar: Solved ring */}
        <div className="flex flex-col lg:flex-row gap-6">
          <SolvedRing {...profile.solved} />
          <GreenScore score={profile.greenScore} />
        </div>

        {/* Recent submissions only */}
        <RecentTable
          items={profile.recentSubmissions}
          emptyMsg="You haven't solved any problems yet."
        />
      </section>
    </div>
  );
}
