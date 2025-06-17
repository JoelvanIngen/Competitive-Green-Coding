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
import { addProblemAPI } from "@/lib/api";

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

interface AdminClientProps {
  user: string | undefined;
}

export default function AdminClient({ user }: AdminClientProps) {
  const [name, setTitle] = useState("");
  const [short_description, setShortDescription] = useState("");
  const [long_description, setLongDescription] = useState("");
  const [template_code, setTemplateCode] = useState("");
  const [difficulty, setDifficulty] = useState("Easy");
  const [language, setLanguage] = useState("C");

  const handleSubmit = async () => {
    try {
      const token = "123";  // change to real jwt token
      const tags = [""];

      const problemData = {
        name,
        language,
        difficulty,
        tags,
        short_description,
        long_description,
        template_code,
      };

      const result = await addProblemAPI.addProblem(problemData, token);

      alert('Problem submitted successfully!');
      // Reset form
      setTitle('');
      setShortDescription('');
      setLongDescription('');
      setTemplateCode('');
      setDifficulty('Easy');
      setLanguage('C');
    } catch (error: unknown) {
      if (error instanceof Error) {
        alert(`Error: ${error.message}`);
      } else {
        alert('An unexpected error occurred');
      }
    }
  };


  if (!user) {
    return (
      <main className="p-8">
        <h1 className="text-4xl font-bold mb-6">Admin Dashboard</h1>
        <p className="text-red-500 font-bold">
          Access denied. You do not have permission to view this page.
        </p>
        <p className="text-muted-foreground mt-2">
          Please log in to access the admin dashboard.
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
              <div className="grid gap-2">
                <Label htmlFor="title">Problem Title</Label>
                <Input
                  id="title"
                  value={name}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter problem title"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="shortDescription">Short description</Label>
                <Input
                  id="shortDescription"
                  value={short_description}
                  onChange={(e) => setShortDescription(e.target.value)}
                  placeholder="Enter short description"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="longDescription">Problem Description</Label>
                <Textarea
                  id="longDescription"
                  value={long_description}
                  onChange={(e) => setLongDescription(e.target.value)}
                  placeholder="Enter problem description"
                  className="min-h-[120px]"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="templateCode">Code template</Label>
                <Textarea
                  id="templateCode"
                  value={template_code}
                  onChange={(e) => setTemplateCode(e.target.value)}
                  placeholder="Enter the template for the code"
                  className="min-h-[120px]"
                />
              </div>

              <div className="flex gap-10">
                <div className="grid gap-2">
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

                <div className="grid gap-2">
                  <Label>Language</Label>
                  <Select
                    value={language}
                    onValueChange={(value) => setLanguage(value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="C">C</SelectItem>
                      <SelectItem value="Python">Python</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
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
