export interface ScoreEntry {
    user_id: string;
    user_name: string;
    score: number;
}

export interface ProblemLeaderboard {
    'problem-id': number;
    'problem-name': string;
    'problem-language': string;
    'problem-difficulty': string;
    scores: ScoreEntry[];
}

export interface Problem {
    id: number;
    name: string;
    description: string;
    difficulty: number;
    language: string;
    created_at: string;
    updated_at: string;
}

export interface ProblemDetailsResponse {
    'problem-id': number;
    name: string;
    language: string;
    difficulty: string;
    tags: string[];
    'short-description': string;
    'long-description': string;
    'template-code': string;
}

export interface ProblemErrorResponse {
    error: string;
}

export interface ProblemSummary {
    'problem-id': number;
    name: string;
    difficulty: 'easy' | 'medium' | 'hard';
    'short-description': string;
}

export interface ProblemsListResponse {
    total: number;
    problems: ProblemSummary[];
}

export interface ProblemsFilterRequest {
    difficulty?: ('easy' | 'medium' | 'hard')[];
    search?: string;
    offset?: number;
    limit?: number;
}

export interface ProblemsAllRequest {
    limit?: number;
}