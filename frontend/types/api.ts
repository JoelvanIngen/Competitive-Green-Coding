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
    'wrappers': string[][];
}

export interface AddProblem {
    name: string;
    language: string;
    difficulty: string;
    tags: string[];
    short_description: string;
    long_description: string;
    template_code: string;
    wrapper: string[][];
}

export interface ProblemErrorResponse {
    error: string;
}

export interface ProblemMetadata {
    'problem-id': number;
    name: string;
    difficulty: 'easy' | 'medium' | 'hard';
    'short-description': string;
}

export interface ProblemsListResponse {
    total: number;
    problems: ProblemMetadata[];
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

// Profile API Types
export interface ProfileSolvedStats {
    total: number;
    easy: number;
    medium: number;
    hard: number;
}

export interface ProfileLanguageStat {
    language: string;
    solved: number;
}

export interface ProfileRecentItem {
    id: string;
    title: string;
    createdAt: string; // ISO date-time format
}

export interface ProfileRecentSubmissionItem {
    submission_id: string;
    problem_id: number;
    title: string;
    createdAt: string; // ISO date-time format
}

export interface ProfileResponse {
    username: string;
    avatarUrl: string | null; // URI format, nullable
    rank: number;
    solved: ProfileSolvedStats;
    greenScore: number;
    languageStats: ProfileLanguageStat[];
    recentSubmissions: ProfileRecentSubmissionItem[];
    recentDiscussions: ProfileRecentItem[];
}

export interface ProfileUpdateRequest {
    avatarUrl?: string; // URI format
    bio?: string;
}

export interface ProfileUpdateResponse {
    updated: boolean;
}
