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