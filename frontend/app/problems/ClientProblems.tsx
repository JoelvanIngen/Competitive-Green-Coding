"use client";
import Link from "next/link";
import { useState } from "react";

// old shadcn imports
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";

/* ---------- shadcn/ui ---------- */
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface Problem {
  id: number;
  title: string;
  description: string;
  difficulty: string;
}

interface Props {
  initialProblems: Problem[];
}

// export default function ClientProblems({ initialProblems }: Props) {
//     const [difficultyFilter, setDifficultyFilter] = useState("All");
//     const [searchTerm, setSearchTerm] = useState("");

//     const filteredProblems = initialProblems.filter((problem) => {
//         const matchesDifficulty =
//             difficultyFilter === "All" || problem.difficulty === difficultyFilter;
//         const matchesSearch =
//             problem.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
//             problem.description.toLowerCase().includes(searchTerm.toLowerCase());

//         return matchesDifficulty && matchesSearch;
//     });

//     return (
//         <main className="p-8">
//             <h1 className="text-4xl font-bold mb-6">Available Problems</h1>

//             <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-2 sm:space-y-0">
//                 <div>
//                     <label className="block text-sm font-medium mb-1">Filter by Difficulty</label>
//                     <select
//                         value={difficultyFilter}
//                         onChange={(e) => setDifficultyFilter(e.target.value)}
//                         className="border rounded px-3 py-2 bg-white text-black"
//                     >
//                         <option value="All">All</option>
//                         <option value="Easy">Easy</option>
//                         <option value="Medium">Medium</option>
//                         <option value="Hard">Hard</option>
//                     </select>
//                 </div>

//                 <div className="flex-1">
//                     <label className="block text-sm font-medium mb-1">Search</label>
//                     <input
//                         type="text"
//                         placeholder="Search problems..."
//                         value={searchTerm}
//                         onChange={(e) => setSearchTerm(e.target.value)}
//                         className="w-full border rounded px-3 py-2"
//                     />
//                 </div>
//             </div>

//             <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
//                 {filteredProblems.map((problem) => (
//                     <Card key={problem.id}>
//                         <CardHeader>
//                             <CardTitle>{problem.title}</CardTitle>
//                         </CardHeader>
//                         <CardContent>
//                             <p className="mb-2 text-muted-foreground">{problem.description}</p>
//                             <span
//                                 className={`inline-block px-2 py-1 text-sm rounded mb-4 ${problem.difficulty === "Easy"
//                                     ? "bg-green-200 text-green-800"
//                                     : problem.difficulty === "Medium"
//                                         ? "bg-yellow-200 text-yellow-800"
//                                         : "bg-red-200 text-red-800"
//                                     }`}
//                             >
//                                 {problem.difficulty}
//                             </span>
//                             <div className="flex space-x-2">
//                                 <Link href={`/submission?id=${problem.id}`}>
//                                     <Button>Go to Submission</Button>
//                                 </Link>
//                                 <Link href={`/leaderboards?id=${problem.id}`}>
//                                     <Button variant="outline">Leaderboard</Button>
//                                 </Link>
//                             </div>
//                         </CardContent>
//                     </Card>
//                 ))}
//             </div>
//         </main>
//     );
// }

/* ---------- COMPONENT ---------- */
export default function ClientProblems({ initialProblems }: Props) {
  const [difficultyFilter, setDifficultyFilter] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");

  /* ---- FILTERED, ALPHANUMERICALLY SORTED LIST ---- */
  const filteredProblems = initialProblems
    .filter((p) => {
      const matchesDifficulty =
        difficultyFilter === "All" || p.difficulty === difficultyFilter;
      const matchesSearch =
        p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.description.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesDifficulty && matchesSearch;
    })
    .sort((a, b) => a.id - b.id);

  /* ---------------- RENDER ---------------- */
  return (
    <main className="max-w-screen-lg mx-auto px-4 lg:px-8 py-8">
      <h1 className="text-4xl font-bold mb-6">Available Problems</h1>

      {/* --------- CONTROLS --------- */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end">
        {/* Difficulty selector */}
        <div className="w-fit">
          <label className="block text-sm font-medium mb-1">
            Filter by Difficulty
          </label>
          <Select
            defaultValue={difficultyFilter}
            onValueChange={setDifficultyFilter}
          >
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Difficulty" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All</SelectItem>
              <SelectItem value="Easy">Easy</SelectItem>
              <SelectItem value="Medium">Medium</SelectItem>
              <SelectItem value="Hard">Hard</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Search field */}
        <div className="flex-grow">
          <label className="block text-sm font-medium mb-1">Search</label>
          <Input
            placeholder="Search problems…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* --------- PROBLEMS TABLE --------- */}
      <div className="overflow-x-auto rounded-lg border-2">        {/* thicker outer border */}
        {/* `border-separate` lets us add vertical spacing WITHOUT the default cell-collapse */}
        <Table className="border-separate border-spacing-y-1">
          <TableHeader>
            <TableRow>
              <TableHead className="w-[60px]">#</TableHead>
              <TableHead className="min-w-[260px]">Title</TableHead>
              <TableHead className="w-[120px]">Difficulty</TableHead>
              <TableHead className="w-[180px]">Actions</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {filteredProblems.map((problem, idx) => (
              <TableRow key={problem.id}
                className="
                    odd:bg-background
                    even:bg-muted/30
                    odd:hover:bg-muted/30
                    even:hover:bg-muted/
                    transition-colors
                "
              >
                {/* Index (with trailing dot) */}
                <TableCell className="font-medium">{`${idx + 1}.`}</TableCell>

                {/* Title + short description */}
                <TableCell>
                  <p className="font-semibold">{problem.title}</p>
                  {problem.description && (
                    <p className="text-sm text-muted-foreground line-clamp-1">
                      {problem.description}
                    </p>
                  )}
                </TableCell>

                {/* Difficulty */}
                <TableCell>
                  <Badge
                    className={
                      problem.difficulty === "Easy"
                        ? "bg-green-200 text-green-800"
                        : problem.difficulty === "Medium"
                          ? "bg-yellow-200 text-yellow-800"
                          : "bg-red-200 text-red-800"
                    }
                  >
                    {problem.difficulty}
                  </Badge>
                </TableCell>

                {/* Action buttons */}
                <TableCell>
                  <div className="flex gap-2">
                    <Link href={`/submission?id=${problem.id}`}>
                      <Button size="sm">Solve</Button>
                    </Link>
                    <Link href={`/leaderboards?id=${problem.id}`}>
                      <Button size="sm" variant="outline">
                        Leaderboard
                      </Button>
                    </Link>
                  </div>
                </TableCell>
              </TableRow>
            ))}

            {filteredProblems.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8">
                  No problems match your filters.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </main>
  );
}