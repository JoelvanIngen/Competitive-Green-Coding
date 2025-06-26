"use client";

import { useState, useEffect } from "react";
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
import { addProblemAPI, problemsApi,RemoveProblemAPI } from "@/lib/api";
import { unknown } from "zod";

interface AdminClientProps {
  user: string | undefined;
  tokenJWT: string | null;
}

export default function AdminClient({ user, tokenJWT }: AdminClientProps) {
  const [name, setTitle] = useState("");
  const [short_description, setShortDescription] = useState("");
  const [long_description, setLongDescription] = useState("");
  const [template_code, setTemplateCode] = useState("");
  const [wrapperInput, setWrapperInput] = useState("");
  const [wrappers, setWrappers] = useState<string[][]>([]);
  const [wrapperType, setWrapperType] = useState("wrapper.c");
  const [tagsInput, setTagsInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [difficulty, setDifficulty] = useState("easy");
  const [language, setLanguage] = useState("c");
  const [problems, setProblems] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProblems();
  }, [tokenJWT]);

  const fetchProblems = async () => {
    if (!tokenJWT) return;
    setLoading(true);
    setError(null);
    try {
      const data = await problemsApi.getAllProblems();
      setProblems(data.problems);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unknown error");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddTags = () => {
    const tagsArray = tagsInput
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0 && !tags.includes(tag));
    setTags([...tags, ...tagsArray]);
    setTagsInput("");
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleAddWrapper = () => {
    const trimmed = wrapperInput.trim();
    if (trimmed && !wrappers.includes([wrapperType, trimmed])) {
      setWrappers([...wrappers, [wrapperType, trimmed]]);
    }
    setWrapperInput("");
  };

  const handleRemoveWrapper = (wrapperToRemove: string[]) => {
  setWrappers(
    wrappers.filter(
      ([type, content]) =>
        !(type === wrapperToRemove[0] && content === wrapperToRemove[1])
    )
    );
  };

  const handleSubmit = async () => {
    try {
      const problemData = {
        name,
        language,
        difficulty,
        tags,
        short_description,
        long_description,
        template_code,
        wrappers,
      };

      // console.log(problemData);   // DEBUG
      await addProblemAPI.addProblem(problemData, tokenJWT);

      alert('Problem submitted successfully!');
      // Reset form
      setTitle('');
      setShortDescription('');
      setLongDescription('');
      setTemplateCode('');
      setWrapperInput('');
      setWrapperType('wrapper.c');
      setTagsInput('');
      setDifficulty('easy');
      setLanguage('c');
      setTags([]);
      setWrappers([]);

      await fetchProblems();
    } catch (error: unknown) {
      if (error instanceof Error) {
        alert(`Error: ${error.message}`);
      } else {
        alert('An unexpected error occurred');
      }
    }
  };

  const handleRemove = (problem_id: number) => async () => {
    try {
      const problemData = {
        problem_id
      }
      
      await RemoveProblemAPI.removeProblem(problemData, tokenJWT);
      alert('Problem removed!');
      await fetchProblems();
    } catch (error: unknown) {
      if (error instanceof Error) {
        alert(`Error: ${error.message}`);
      } else {
        alert(`An unexpected error occurred`);
      }
    }
  };

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

              <div className="grid gap-2">
                <Label htmlFor="tags">Tags</Label>
                <div className="flex flex-col gap-2">
                  <Textarea
                    id="tags"
                    value={tagsInput}
                    onChange={(e) => setTagsInput(e.target.value)}
                    placeholder="Enter tags, separated by commas"
                    className="min-h-[40px]"
                  />
                  <Button type="button" onClick={handleAddTags}>OK</Button>
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="wrapper">Wrapper</Label>
                <div className="flex flex-col gap-2">
                  <Textarea
                    id="wrapper"
                    value={wrapperInput}
                    onChange={(e) => setWrapperInput(e.target.value)}
                    placeholder="Enter a wrapper"
                    className="min-h-[40px]"
                  />
                  <Select
                    value={wrapperType}
                    onValueChange={(value) => setWrapperType(value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select wrapper" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="wrapper.c">wrapper.c</SelectItem>
                      <SelectItem value="wrapper.h">wrapper.h</SelectItem>
                      <SelectItem value="submission.h">submission.h</SelectItem>
                      <SelectItem value="input.txt">input.txt</SelectItem>
                      <SelectItem value="expected_output.txt">expected_output.txt</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button type="button" onClick={handleAddWrapper}>OK</Button>
                </div>
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
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
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
                      <SelectItem value="c">C</SelectItem>
                      <SelectItem value="python">Python</SelectItem>
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

        {/* Tags & Wrappers for this Problem */}
        <Card>
          <CardHeader>
            <CardTitle>Tags & Wrappers for this Problem</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <div className="font-semibold">Tags:</div>
              {tags.length === 0 ? (
                <p className="text-muted-foreground">No tags added yet.</p>
              ) : (
                <ul className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <li key={tag} className="flex items-center bg-theme-bg rounded px-2 py-1">
                      {tag}
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        className="ml-2 bg-rose-600"
                        onClick={() => handleRemoveTag(tag)}
                      >
                        ×
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <div className="font-semibold">Wrappers:</div>
              {wrappers.length === 0 ? (
                <p className="text-muted-foreground">No wrappers added yet.</p>
              ) : (
                <ul className="flex flex-col gap-2">
                  {wrappers.map(([filename, content], idx) => (
                    <li key={filename + idx} className="flex items-center bg-theme-bg rounded px-2 py-1">
                      <span className="truncate max-w-xs">{filename}:<br/>{content}</span>
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        className="ml-auto bg-rose-600"
                        onClick={() => handleRemoveWrapper([filename, content])}
                      >
                        ×
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* View Submitted Problems */}
      <Card>
        <CardHeader>
          <CardTitle>Submitted Problems</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Loading problems...</p>
          ) : error ? (
            <p className="text-red-500">Error: {error}</p>
          ) : problems.length === 0 ? (
            <p className="text-muted-foreground">No problems submitted yet.</p>
          ) : (
            <ul className="space-y-2">
              {problems.map((problem: any) => (
                <li
                  key={problem.problem_id}
                  className="flex justify-between items-center p-3 border rounded"
                >
                  <div>
                    <p className="font-medium">{problem.name}</p>
                    <p className="text-sm text-muted-foreground">
                      Difficulty: {problem.difficulty}
                    </p>
                  </div>
                  <div>
                    <Button
                      type="button"
                      size="sm"
                      onClick={handleRemove(problem.problem_id)}
                      className="ml-2 bg-rose-600 hover:bg-rose-900">
                      x
                    </Button>
                    <Button size="sm" className="bg-theme-primary hover:bg-theme-primary-dark">
                      View Details
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
