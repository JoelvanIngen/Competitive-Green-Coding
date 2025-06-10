"use client";

import Link from "next/link";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const dummyProblems = [
  {
    id: 1,
    title: "Sum of Two Numbers",
    description: "Write a function that returns the sum of two integers.",
    difficulty: "Easy",
  },
  {
    id: 2,
    title: "Longest Increasing Subsequence",
    description: "Find the length of the longest increasing subsequence in an array.",
    difficulty: "Medium",
  },
  {
    id: 3,
    title: "Minimum Spanning Tree",
    description: "Implement Kruskal's or Prim's algorithm to find MST.",
    difficulty: "Hard",
  },
  {
    id: 4,
    title: "Palindrome Check",
    description: "Check whether a given string is a palindrome.",
    difficulty: "Easy",
  },
  {
    id: 5,
    title: "Dijkstra's Algorithm",
    description: "Find the shortest path in a weighted graph.",
    difficulty: "Medium",
  },
];

export default function ProblemsPage() {
  const [difficultyFilter, setDifficultyFilter] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredProblems = dummyProblems.filter((problem) => {
    const matchesDifficulty =
      difficultyFilter === "All" || problem.difficulty === difficultyFilter;
    const matchesSearch =
      problem.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      problem.description.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesDifficulty && matchesSearch;
  });

  return (
    <main className="p-8">
      <h1 className="text-4xl font-bold mb-6">Available Problems</h1>

      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-2 sm:space-y-0">
        <div>
          <label className="block text-sm font-medium mb-1">Filter by Difficulty</label>
            <select
            value={difficultyFilter}
            onChange={(e) => setDifficultyFilter(e.target.value)}
            className="border rounded px-3 py-2 bg-white text-black"
            >
            <option value="All">All</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
            </select>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium mb-1">Search</label>
          <input
            type="text"
            placeholder="Search problems..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProblems.map((problem) => (
          <Card key={problem.id}>
            <CardHeader>
              <CardTitle>{problem.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-2 text-muted-foreground">{problem.description}</p>
              <span
                className={`inline-block px-2 py-1 text-sm rounded mb-4 ${
                  problem.difficulty === "Easy"
                    ? "bg-green-200 text-green-800"
                    : problem.difficulty === "Medium"
                    ? "bg-yellow-200 text-yellow-800"
                    : "bg-red-200 text-red-800"
                }`}
              >
                {problem.difficulty}
              </span>
              <div>
                <Link href={`/submission?id=${problem.id}`}>
                  <Button>Go to Submission</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}
