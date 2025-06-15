import ClientProblems from "./ClientProblems";

// This is temporary mock data - in a real app, this would come from an API
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

export default async function ProblemsPage() {
  // In a real app, you would fetch this data from your API
  // const problems = await problemsApi.getProblems();

  return <ClientProblems initialProblems={dummyProblems} />;
}
