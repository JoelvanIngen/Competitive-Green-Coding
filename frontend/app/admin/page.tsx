"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Dummy problems (replace with API later)
const dummySubmittedProblems = [
  {
    id: 1,
    title: "Sum of Two Numbers",
    difficulty: "Easy",
  },
  {
    id: 2,
    title: "Longest Increasing Subsequence",
    difficulty: "Medium",
  },
  {
    id: 3,
    title: "Minimum Spanning Tree",
    difficulty: "Hard",
  },
];

export default function AdminPage() {
  // TODO: Replace this with actual user role check from backend/auth
  const userRole = "admin"; // Example: "admin" or "user" or "guest"

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [difficulty, setDifficulty] = useState("Easy");

  const handleSubmit = () => {
    // For now just log — backend will be added later
    console.log("Submitting problem:", {
      title,
      description,
      difficulty,
    });
    alert("Problem submitted (mock)!");
    // Reset form
    setTitle("");
    setDescription("");
    setDifficulty("Easy");
  };

  // If user is not admin → show access denied
  if (userRole !== "admin") {
    return (
      <main className="p-8">
        <h1 className="text-4xl font-bold mb-6">Admin Dashboard</h1>
        <p className="text-red-500 font-bold">
          Access denied. You do not have permission to view this page.
        </p>
        <p className="text-muted-foreground mt-2">
          {/* TODO: Hook this up to actual backend auth when available */}
        </p>
      </main>
    );
  }

  // If user is admin → show full page
  return (
    <main className="p-8">
      <h1 className="text-4xl font-bold mb-6">Admin Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Problem Submission Form */}
        <Card>
          <CardHeader>
            <CardTitle>Add New Problem</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="title">Problem Title</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter problem title"
                />
              </div>

              <div>
                <Label htmlFor="description">Problem Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter problem description (Markdown supported)"
                  className="min-h-[120px]"
                />
              </div>

              <div>
                <Label>Difficulty</Label>
                <Select
                  value={difficulty}
                  onValueChange={(value) => setDifficulty(value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select difficulty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Easy">Easy</SelectItem>
                    <SelectItem value="Medium">Medium</SelectItem>
                    <SelectItem value="Hard">Hard</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleSubmit} className="w-full mt-4">
                Submit Problem
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Admin Tools */}
        <Card>
          <CardHeader>
            <CardTitle>Admin Tools</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              Placeholder for other admin functionality (e.g. manage users,
              review problems, site stats, etc).
            </p>
            <Button variant="outline" disabled>
              Manage Users (coming soon)
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* View Submitted Problems */}
      <Card>
        <CardHeader>
          <CardTitle>Submitted Problems</CardTitle>
        </CardHeader>
        <CardContent>
          {dummySubmittedProblems.length === 0 ? (
            <p className="text-muted-foreground">No problems submitted yet.</p>
          ) : (
            <ul className="space-y-2">
              {dummySubmittedProblems.map((problem) => (
                <li
                  key={problem.id}
                  className="flex justify-between items-center p-3 border rounded"
                >
                  <div>
                    <p className="font-medium">{problem.title}</p>
                    <p className="text-sm text-muted-foreground">
                      Difficulty: {problem.difficulty}
                    </p>
                  </div>
                  <Button size="sm" variant="outline" disabled>
                    View Details
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
