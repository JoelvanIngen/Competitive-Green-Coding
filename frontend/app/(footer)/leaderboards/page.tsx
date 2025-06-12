"use client";

import { useEffect, useMemo, useState } from "react";
import { Leaf, Search } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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

/* --------------------------------------------------------------------------
   Component
   --------------------------------------------------------------------------*/
export default function LeaderboardPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [langFilter, setLangFilter] = useState<string>("All");
  const [challengeQuery, setChallengeQuery] = useState<string>("");

  /* ----------------------------------------------------------------------
     Mock data – replace with real API
     ----------------------------------------------------------------------*/
  useEffect(() => {
    setEntries([
      { id: 1, name: "EcoEnthusiast", score: 98, solved: 42, language: "Python", challenge: "Array Manipulation" },
      { id: 2, name: "GreenGuru",      score: 93, solved: 38, language: "C",      challenge: "Graph Traversal"   },
      { id: 3, name: "CodeConserver",  score: 90, solved: 35, language: "Python", challenge: "Dynamic Programming" },
      { id: 4, name: "SustainSam",     score: 88, solved: 30, language: "C",      challenge: "Sorting"           },
      { id: 5, name: "ByteBonsai",     score: 85, solved: 28, language: "Python", challenge: "Matrix Operations"  },
      { id: 6, name: "EnviroDev",      score: 82, solved: 26, language: "C",      challenge: "Path Finding"       },
    ]);
  }, []);

  const languages = ["All", "Python", "C"];

  const filtered = useMemo(() =>
    entries.filter((e) =>
      (langFilter === "All" || e.language === langFilter) &&
      (challengeQuery.trim() === "" || e.challenge.toLowerCase().includes(challengeQuery.trim().toLowerCase()))
    ), [entries, langFilter, challengeQuery]);

  const renderLangButtons = () => (
    <div className="flex flex-wrap items-center gap-2">
      <span className="font-medium text-sm">Language:</span>
      {languages.map((opt) => (
        <Button
          key={opt}
          size="sm"
          variant={langFilter === opt ? "default" : "outline"}
          className="text-xs"
          onClick={() => setLangFilter(opt)}
        >
          {opt}
        </Button>
      ))}
    </div>
  );

  const renderChallengeSearch = () => (
    <div className="flex items-center gap-2">
      <Search className="text-muted-foreground" size={16} />
      <Input
        placeholder="Search challenges..."
        value={challengeQuery}
        onChange={(e) => setChallengeQuery(e.target.value)}
        className="h-8 w-48"
      />
    </div>
  );

  return (
    <div className="h-[calc(100vh-128px)] flex flex-col items-center gap-10 py-12 px-4 bg-background text-foreground">
      {/* Title */}
      <h1 className="flex items-center gap-2 text-4xl font-extrabold text-theme-primary-dark dark:text-theme-primary-light">
        <Leaf className="text-theme-primary dark:text-theme-primary-light" />
        GreenCode Leaderboard
      </h1>

      {/* Filters */}
      <div className="w-full max-w-5xl flex flex-col md:flex-row justify-between gap-4">
        {renderLangButtons()}
        {renderChallengeSearch()}
      </div>

      {/* Table */}
      <Card className="w-full max-w-5xl shadow-lg">
        <CardContent className="p-6 overflow-x-auto">
          <table className="w-full min-w-[800px] border-collapse text-left">
            <thead className="bg-muted text-theme-primary dark:text-theme-primary-light text-xs uppercase">
              <tr>
                <th className="px-4 py-2">Rank</th>
                <th className="px-4 py-2">Coder</th>
                <th className="px-4 py-2">Green Score</th>
                <th className="px-4 py-2">Solved</th>
                <th className="px-4 py-2">Language</th>
                <th className="px-4 py-2">Challenge</th>
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
                  <td className="px-4 py-2 font-bold text-theme-primary dark:text-theme-primary-light">{i + 1}</td>
                  <td className="px-4 py-2">{u.name}</td>
                  <td className="px-4 py-2">{u.score}</td>
                  <td className="px-4 py-2">{u.solved}</td>
                  <td className="px-4 py-2">{u.language}</td>
                  <td className="px-4 py-2">{u.challenge}</td>
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