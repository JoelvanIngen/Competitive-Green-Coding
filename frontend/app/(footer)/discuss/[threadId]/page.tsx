// app/(footer)/discuss/[threadId]/page.tsx
// Dynamic thread‑detail page for the Discussion board.
// this page requires:
// npm install lucide-react          
// npx shadcn add textarea button avatar card

"use client";

import { useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
// import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  ThumbsUp,
  MessageSquare,
  Eye,
  SendHorizonal,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
// import { babelIncludeRegexes } from "next/dist/build/webpack-config";

// Mock thread + comment data – replace with real API calls later.
const mockThreads = [
  {
    id: "abc123",
    title: "Need help optimizing my Two Sum solution",
    content: `Here is my current \`O(n²)\` algorithm for **Two Sum**:

\`\`\`python
for i in range(len(nums)):
    for j in range(i+1, len(nums)):
        if nums[i] + nums[j] == target:
            return [i, j]
\`\`\`

Clearly quadratic. Any advice on how to improve time complexity?`,
    problemSlug: "two-sum",
    votes: 41,
    comments: 8,
    views: 310,
    createdAt: "2025-06-07T08:30:00Z",
    author: {
      name: "Jane",
      avatarUrl: undefined,
    },
  },
  // add more thread objects as needed
] as const;

type Comment = {
  id: string;
  author: { name: string; avatarUrl?: string };
  body: string;
  createdAt: string;
};

const mockComments: Comment[] = [
  {
    id: "c1",
    author: { name: "Alex" },
    body: "Use a hashmap to store seen numbers in O(n).",
    createdAt: "2025-06-07T09:00:00Z",
  },
  {
    id: "c2",
    author: { name: "Priya" },
    body: "@Alex +1. You can solve in one pass by checking if target-num exists.",
    createdAt: "2025-06-07T09:15:00Z",
  },
];

export default function ThreadDetailPage() {
  const { threadId } = useParams<{ threadId: string }>();
  const router = useRouter();
  const [commentInput, setCommentInput] = useState("");

  // Simulate fetch
  const thread = useMemo(() => mockThreads.find((t) => t.id === threadId), [threadId]);

  const comments = mockComments; // in real life → fetch(`/api/thread/${threadId}/comments`)

  if (!thread) {
    return (
      <div className="container mx-auto max-w-2xl py-12 text-center">
        <p className="text-lg">Thread not found.</p>
        <Button variant="secondary" className="mt-4" onClick={() => router.back()}>
          Go back
        </Button>
      </div>
    );
  }

  const timeAgo = formatDistanceToNow(new Date(thread.createdAt), { addSuffix: true });

  return (
    <div className="container mx-auto max-w-2xl py-8 space-y-6">
      {/* Back link */}
      <Button variant="ghost" size="sm" asChild className="gap-1">
        <Link href="/discuss">
          <ArrowLeft className="h-4 w-4" /> Back
        </Link>
      </Button>

      {/* Thread card */}
      <Card>
        <CardHeader className="flex-row items-start gap-4 pb-4">
          <Avatar className="h-10 w-10">
            {thread.author.avatarUrl ? (
              <AvatarImage src={thread.author.avatarUrl} />
            ) : (
              <AvatarFallback>{thread.author.name[0]}</AvatarFallback>
            )}
          </Avatar>
          <div className="space-y-1 flex-1">
            <h1 className="text-xl font-semibold leading-tight">{thread.title}</h1>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{thread.author.name}</span>•<span>{timeAgo}</span>
              <Badge variant="secondary" className="ml-auto">
                {thread.problemSlug}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="prose prose-invert space-y-4">
          {/* For real markdown rendering install react-markdown; plain text for now */}
          {thread.content.split("\n").map((line, idx) => (
            <p key={idx}>{line}</p>
          ))}
        </CardContent>
        <CardFooter className="flex gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <ThumbsUp className="h-4 w-4" /> {thread.votes}
          </span>
          <span className="flex items-center gap-1">
            <MessageSquare className="h-4 w-4" /> {thread.comments}
          </span>
          <span className="flex items-center gap-1">
            <Eye className="h-4 w-4" /> {thread.views}
          </span>
        </CardFooter>
      </Card>

      {/* Comment box */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold">Comments ({comments.length})</h2>

        {/* New comment */}
        <Card>
          <CardContent className="p-4 space-y-3">
            <Textarea
              placeholder="Type comment here…"
              value={commentInput}
              onChange={(e) => setCommentInput(e.target.value)}
              rows={3}
            />
            <div className="flex justify-end">
              <Button disabled={!commentInput.trim()} className="gap-1">
                <SendHorizonal className="h-4 w-4" /> Comment
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Comment list */}
        {comments.map((c) => (
          <Card key={c.id} className="border-none bg-muted/30">
            <CardHeader className="flex-row items-start gap-4 pb-2">
              <Avatar className="h-8 w-8">
                {c.author.avatarUrl ? (
                  <AvatarImage src={c.author.avatarUrl} />
                ) : (
                  <AvatarFallback>{c.author.name[0]}</AvatarFallback>
                )}
              </Avatar>
              <div className="flex-1">
                <p className="text-sm font-medium">{c.author.name}</p>
                <p className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(c.createdAt), { addSuffix: true })}
                </p>
              </div>
            </CardHeader>
            <CardContent className="pt-0 pb-4 text-sm whitespace-pre-line">
              {c.body}
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
