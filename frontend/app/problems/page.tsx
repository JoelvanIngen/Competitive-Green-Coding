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
    // Fetch problems from the new /api/problems/all endpoint
    const response = await problemsApi.getAllProblems(20);

    // Transform the API response to match the Problem interface
    const problems: Problem[] = response.problems.map(p => ({
      // handle either style just in case
      id:        p['problem_id']        ?? p['problem-id']        ?? p.id,
      title:     p.name,
      description: p['short_description'] ?? p['short-description'] ?? '',
      difficulty: (p.difficulty ?? '').replace(/^\w/, c => c.toUpperCase()),
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
