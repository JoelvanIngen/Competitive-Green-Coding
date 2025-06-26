// -----------------------------------------------------------------------------
// User Profile page (Server Component) – compact layout
// -----------------------------------------------------------------------------
import type { Metadata } from "next";
import { notFound } from "next/navigation";

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
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_SITE_URL}/api/profile/${username}`,
    { cache: "no-store" }
  );
  if (!res.ok) return notFound();

  const profile: ProfileData = await res.json();

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
