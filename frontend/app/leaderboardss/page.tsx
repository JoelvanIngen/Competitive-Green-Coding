"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Leaf } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { leaderboardApi } from "@/lib/api";
import type { ProblemLeaderboard } from "@/types/api";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

export default function LeaderboardPage() {
    const [problemData, setProblemData] = useState<ProblemLeaderboard | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [page, setPage] = useState(0);
    const pageSize = 5;

    const searchParams = useSearchParams();
    const problemId = searchParams.get("id");

    const loadLeaderboard = async (pageNum: number) => {
        if (!problemId) return;

        try {
            setIsLoading(true);
            const firstRow = pageNum * pageSize;
            const lastRow = firstRow + pageSize;

            // Get data directly from the API
            const data = await leaderboardApi.getLeaderboard(problemId, firstRow, lastRow);

            if (pageNum === 0) {
                setProblemData(data);
            } else {
                setProblemData((prev) => {
                    if (!prev) return data;
                    return {
                        ...prev,
                        scores: [...prev.scores, ...data.scores],
                    };
                });
            }
        } catch (err: any) {
            console.error("Leaderboard fetch failed", err);
            setError("Unable to load leaderboard.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        setPage(0);
        loadLeaderboard(0);
    }, [problemId]);

    const handleLoadMore = () => {
        const nextPage = page + 1;
        setPage(nextPage);
        loadLeaderboard(nextPage);
    };

    return (
        <div className="min-h-screen flex flex-col items-center gap-10 py-12 px-4 bg-background text-foreground">
            <h1 className="flex items-center gap-2 text-4xl font-extrabold text-theme-primary-dark dark:text-theme-primary-light">
                <Leaf className="text-theme-primary dark:text-theme-primary-light" />
                GreenCode Leaderboard
            </h1>

            {problemData && (
                <div className="text-center">
                    <h2 className="text-2xl font-semibold mb-1">
                        {problemData.problem_name} {problemData.problem_language}
                    </h2>
                </div>
            )}

            {error && <p className="text-red-500 text-sm">{error}</p>}

            <Card className="w-full max-w-5xl shadow-lg">
                <CardContent className="p-6 overflow-x-auto">
                    <table className="w-full min-w-[600px] border-collapse text-left">
                        <thead className="bg-muted text-theme-primary dark:text-theme-primary-light text-xs uppercase">
                            <tr>
                                <th className="px-4 py-2">Rank</th>
                                <th className="px-4 py-2">Coder</th>
                                <th className="px-4 py-2">Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            {problemData?.scores.map((entry, index) => (
                                <tr
                                    key={entry.user_id}
                                    className={cn(
                                        "transition-colors",
                                        index % 2 === 1 ? "bg-background" : "bg-muted/30",
                                        "hover:bg-theme-primary-dark/10 dark:hover:bg-theme-primary-light/10"
                                    )}
                                >
                                    <td className="px-4 py-2 font-bold text-theme-primary dark:text-theme-primary-light">
                                        {index + 1}
                                    </td>
                                    <td className="px-4 py-2">{entry.user_name}</td>
                                    <td className="px-4 py-2">{entry.score}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {problemData?.scores.length === 0 && (
                        <p className="text-center text-sm text-muted-foreground mt-6">
                            No results for this problem.
                        </p>
                    )}

                    {problemData && problemData.scores.length > 0 && (
                        <div className="mt-6 flex justify-center">
                            <Button
                                onClick={handleLoadMore}
                                disabled={isLoading}
                                className="bg-theme-primary hover:bg-theme-primary-dark text-white"
                            >
                                {isLoading ? "Loading..." : "Load More"}
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Score Distribution Chart */}
            {problemData && problemData.scores.length > 0 && (
                <Card className="w-full max-w-5xl shadow-lg">
                    <CardContent className="p-6">
                        <h3 className="text-lg font-semibold mb-4 text-center">
                            Score Distribution
                        </h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart
                                data={problemData.scores
                                    .sort((a, b) => b.score - a.score)
                                    .map((entry) => ({
                                        name: entry.user_name,
                                        score: entry.score,
                                    }))}
                                margin={{ top: 5, right: 30, left: 20, bottom: 40 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" angle={-45} textAnchor="end" interval={0} height={60} />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="score" fill="#22c55e" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
