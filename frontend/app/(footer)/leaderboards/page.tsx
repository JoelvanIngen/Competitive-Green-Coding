// -----------------------------------------------------------------------------
// Leaderboard page
//
// This page displays the main leaderboard UI for the platform. It shows user or
// problem leaderboards, allowing users to see rankings, scores, and compare their
// performance with others. Integrates the ClientLeaderboard component and handles
// data fetching and display logic for the leaderboard view.
// -----------------------------------------------------------------------------
import { leaderboardApi } from "@/lib/api";
import ClientLeaderboard from "./ClientLeaderboard";
import { Suspense } from "react";
const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

export default async function LeaderboardPage({ searchParams }: { searchParams: Promise<{ id?: string }> }) {
    const params = await searchParams;
    const problemId = params.id;

    console.log("problemId: ", problemId);
    console.log("baseUrl: ", baseUrl);

    if (!problemId) return <p>No problem ID provided.</p>;

    try {
        const initialData = await leaderboardApi.postLeaderboard(problemId, 0, 5);
        return (
            <ClientLeaderboard
                initialData={initialData}
                problemId={problemId}
            />
        );
    } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
        return <p>Failed to load leaderboard data. Please try again later.</p>;
    }
}