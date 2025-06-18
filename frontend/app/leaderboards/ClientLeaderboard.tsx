"use client";

import { useState } from "react";
import { Leaf } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { ProblemLeaderboard } from "@/types/api";
import { leaderboardApi } from "@/lib/api";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

interface Props {
    initialData: ProblemLeaderboard;
    problemId: string;
}

export default function ClientLeaderboard({ initialData, problemId }: Props) {
    const [problemData, setProblemData] = useState<ProblemLeaderboard>(initialData);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [page, setPage] = useState(0);
    const pageSize = 5;

    const handleLoadMore = async () => {
        try {
            setIsLoading(true);
            const nextPage = page + 1;
            const firstRow = nextPage * pageSize;
            const lastRow = firstRow + pageSize;

            const data = await leaderboardApi.getLeaderboard(problemId, firstRow, lastRow);

            setProblemData(prev => ({
                ...prev,
                scores: [...prev.scores, ...data.scores],
            }));
            setPage(nextPage);
        } catch (err) {
            console.error("Load more failed", err);
            setError(err instanceof Error ? err.message : "Unable to load more scores.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col items-center gap-10 py-12 px-4 bg-background text-foreground">
            <h1 className="flex items-center gap-2 text-4xl font-extrabold text-theme-primary-dark dark:text-theme-primary-light">
                <Leaf className="text-theme-primary dark:text-theme-primary-light" />
                GreenCode Leaderboard
            </h1>

            <div className="text-center">
                <h2 className="text-2xl font-semibold mb-1">
                    {problemData.problem_name} {problemData.problem_language}
                </h2>
            </div>

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
                                    key={entry.user_id + "-" + index}
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

                    <div className="mt-6 flex justify-center">
                        <Button
                            onClick={handleLoadMore}
                            disabled={isLoading}
                            className="bg-theme-primary hover:bg-theme-primary-dark text-white"
                        >
                            {isLoading ? "Loading..." : "Load More"}
                        </Button>
                    </div>
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
