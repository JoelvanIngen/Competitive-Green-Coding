import ClientProblems from "./ClientProblems";
import { problemsApi } from "@/lib/api";

interface Problem {
  id: number;
  title: string;
  description: string;
  difficulty: string;
}

export default async function ProblemsPage() {
  try {
    // Fetch problems from the API with default pagination
    const response = await problemsApi.getProblems({
      limit: 20,
      offset: 0
    });

    // Transform the API response to match the Problem interface
    const problems: Problem[] = response.problems.map(problem => ({
      id: problem['problem-id'],
      title: problem.name,
      description: problem['short-description'],
      difficulty: problem.difficulty.charAt(0).toUpperCase() + problem.difficulty.slice(1) // Capitalize first letter
    }));

    return <ClientProblems initialProblems={problems} />;
  } catch (error) {
    console.error('Failed to fetch problems:', error);
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Error Loading Problems</h1>
          <p className="mt-2 text-gray-600">Please try again later</p>
        </div>
      </div>
    );
  }
}
