import { leaderboardApi } from "@/lib/api";
import ClientLeaderboard from "./ClientLeaderboard";
import { Suspense } from "react";

export default async function LeaderboardPage({ searchParams }: { searchParams: { id?: string } }) {
    const params = await Promise.resolve(searchParams);
    const problemId = params.id;

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