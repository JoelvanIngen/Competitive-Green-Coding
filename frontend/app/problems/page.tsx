import ClientProblems from "./ClientProblems";
import { problemsApi } from "@/lib/api";
import type { ProblemsListResponse } from '@/types/api';

interface Problem {
  id: number;
  title: string;
  description: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
}

function titleCase(str: string) {
  return str ? str[0].toUpperCase() + str.slice(1) : '';
}

export default async function ProblemsPage() {
  try {
    const response = (await problemsApi.getAllProblems(
      20,
    )) as ProblemsListResponse;

    // Transform the API response to match the Problem interface
    const problems: Problem[] = response.problems.map((p) => ({
      id: p['problem-id'],
      title: p.name,
      description: p['short-description'] ?? '',
      difficulty: titleCase(p.difficulty) as Problem['difficulty'],
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
