// app/(footer)/discus/page.tsx
// Discussion board page – looks & feels close to LeetCode’s but scoped to coding‑challenge problems.
// Built with Next.js (App Router), TailwindCSS, and shadcn/ui.
// for this use npm install framer-motion, npm install date-fns
// NOTE: Replace the mockThreads array with a real data‑fetch (e.g. from /api/discussion) once the backend is ready.

"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { formatDistanceToNow } from "date-fns";
import {
  Card,
  CardHeader,
  CardContent,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Avatar,
  AvatarImage,
  AvatarFallback,
} from "@/components/ui/avatar";
import { ThumbsUp, MessageSquare, Eye } from "lucide-react";

/**
 * Thread model – adjust once you connect to real backend.
 */
type Thread = {
  id: string;
  title: string;
  snippet: string;
  problemSlug: string; // e.g. "two-sum"
  votes: number;
  comments: number;
  views: number;
  createdAt: string; // ISO date
  author: {
    name: string;
    avatarUrl?: string;
  };
};

// 🔧 Temporary demo data
const mockThreads: Thread[] = [
  {
    id: "abc123",
    title: "Need help optimizing my Two Sum solution",
    snippet:
      "I solved Two Sum in O(n²) but it times out on large inputs. Any tips on improving it?…",
    problemSlug: "two-sum",
    votes: 41,
    comments: 8,
    views: 310,
    createdAt: "2025-06-07T08:30:00Z",
    author: { name: "Jane", avatarUrl: undefined },
  },
  {
    id: "def456",
    title: "Binary Tree Level Order Traversal – Java review",
    snippet: "Would love feedback on my BFS vs DFS approach in Java. Which is cleaner?…",
    problemSlug: "binary-tree-level-order-traversal",
    votes: 16,
    comments: 6,
    views: 118,
    createdAt: "2025-06-07T10:10:00Z",
    author: { name: "Chen", avatarUrl: undefined },
  },
  {
    id: "ghi789",
    title: "Is my sliding‑window for Longest Substring efficient enough?",
    snippet:
      "I used a hashmap + two pointers. Passes but memory seems high. Any alternative?…",
    problemSlug: "longest-substring-without-repeating-characters",
    votes: 9,
    comments: 2,
    views: 85,
    createdAt: "2025-06-06T22:45:00Z",
    author: { name: "Diego", avatarUrl: undefined },
  },
];

export default function DiscussionPage() {
  const [query, setQuery] = useState("");

  // Case‑insensitive search over title + problemSlug
  const filteredThreads = useMemo(() => {
    if (!query.trim()) return mockThreads;
    const q = query.toLowerCase();
    return mockThreads.filter(
      (t) =>
        t.title.toLowerCase().includes(q) || t.problemSlug.toLowerCase().includes(q)
    );
  }, [query]);

  return (
    <div className="container mx-auto max-w-3xl py-8">
      <h1 className="text-3xl font-bold mb-6">Discussion Board</h1>

      {/* 🔍 Problem search */}
      <Input
        placeholder="Search by problem name…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full"/>

      {/* Thread list */}
      <div className="space-y-4 mt-6">
        {filteredThreads.length === 0 && (
          <p className="text-center text-muted-foreground mt-12">
            No threads found.
          </p>
        )}

        {filteredThreads.map((thread) => (
          <motion.div
            key={thread.id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="flex-row items-start gap-3 pb-2">
                <Avatar className="h-8 w-8">
                  {thread.author.avatarUrl ? (
                    <AvatarImage src={thread.author.avatarUrl} alt={thread.author.name} />
                  ) : (
                    <AvatarFallback>{thread.author.name[0]}</AvatarFallback>
                  )}
                </Avatar>
                <div className="space-y-1">
                  <Link
                    href={`/discuss/${thread.id}`}
                    className="text-lg font-semibold hover:underline"
                  >
                    {thread.title}
                  </Link>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {thread.snippet}
                  </p>
                </div>
              </CardHeader>

              <CardContent className="flex items-center gap-4 text-xs text-muted-foreground pt-2 pb-4">
                <span className="flex items-center gap-1">
                  <ThumbsUp className="h-4 w-4" /> {thread.votes}
                </span>
                <span className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4" /> {thread.comments}
                </span>
                <span className="flex items-center gap-1">
                  <Eye className="h-4 w-4" /> {thread.views}
                </span>
                <Badge variant="secondary" className="ml-auto">
                  {thread.problemSlug}
                </Badge>
                <span>
                  {formatDistanceToNow(new Date(thread.createdAt), {
                    addSuffix: true,
                  })}
                </span>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
