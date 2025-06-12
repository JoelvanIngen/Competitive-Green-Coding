"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Leaf, Search } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface Entry {
  id: number;
  name: string;
  score: number;
  solved: number;
  language: string;
  challenge: string;
}

export default function LeaderboardPage() {
  const searchParams = useSearchParams();
  const title = searchParams.get("title");

  const [entries, setEntries] = useState<Entry[]>([]);
  const [coderQuery, setCoderQuery] = useState<string>("");

  useEffect(() => {
    setEntries([
      { id: 1, name: "EcoEnthusiast", score: 98, solved: 42, language: "Python", challenge: "Sum of Two Numbers" },
      { id: 2, name: "GreenGuru",      score: 93, solved: 38, language: "C",      challenge: "Longest Increasing Subsequence" },
      { id: 3, name: "CodeConserver",  score: 90, solved: 35, language: "Python", challenge: "Minimum Spanning Tree" },
      { id: 4, name: "SustainSam",     score: 88, solved: 30, language: "C",      challenge: "Palindrome Check" },
      { id: 5, name: "ByteBonsai",     score: 85, solved: 28, language: "Python", challenge: "Dijkstra's Algorithm" },
      { id: 6, name: "EnviroDev",      score: 82, solved: 26, language: "C",      challenge: "Longest Increasing Subsequence" },
    ]);
  }, []);

  const filtered = useMemo(() =>
    entries.filter((e) =>
      (title ? e.challenge.toLowerCase() === decodeURIComponent(title).toLowerCase() : true) &&
      (coderQuery.trim() === "" || e.name.toLowerCase().includes(coderQuery.trim().toLowerCase()))
    ), [entries, title, coderQuery]);

  const renderCoderSearch = () => (
    <div className="flex items-center gap-2">
      <Search className="text-muted-foreground" size={16} />
      <Input
        placeholder="Search coder..."
        value={coderQuery}
        onChange={(e) => setCoderQuery(e.target.value)}
        className="h-8 w-48"
      />
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col items-center gap-6 py-12 px-4 bg-background text-foreground">
      {/* Title */}
      <h1 className="flex items-center gap-2 text-4xl font-extrabold text-theme-primary-dark dark:text-theme-primary-light">
        <Leaf className="text-theme-primary dark:text-theme-primary-light" />
        {title ? `Leaderboard: ${decodeURIComponent(title)}` : "Global Leaderboard"}
      </h1>

      {/* Coder Search */}
      <div className="w-full max-w-2xl flex justify-left">
        {renderCoderSearch()}
      </div>

      {/* Leaderboard Table */}
      <Card className="w-full max-w-2xl shadow-lg">
        <CardContent className="p-6 overflow-x-auto">
          <table className="w-full min-w-[400px] border-collapse text-left">
            <thead className="bg-muted text-theme-primary dark:text-theme-primary-light text-xs uppercase">
              <tr>
                <th className="px-4 py-2 text-center">Rank</th>
                <th className="px-4 py-2">Coder</th>
                <th className="px-4 py-2 text-center">Green Score</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u, i) => (
                <tr
                  key={u.id}
                  className={cn(
                    "transition-colors",
                    i % 2 === 0 ? "bg-background" : "bg-muted/30",
                    "hover:bg-theme-primary-dark/10 dark:hover:bg-theme-primary-light/10",
                  )}
                >
                  <td className="px-4 py-2 text-center font-bold text-theme-primary dark:text-theme-primary-light">
                    {i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : i + 1}
                  </td>
                  <td className="px-4 py-2">{u.name}</td>
                  <td className="px-4 py-2 text-center">{u.score}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <p className="text-center text-sm text-muted-foreground mt-6">No results match your filters.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
