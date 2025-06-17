export interface ScoreEntry {
    user_id: string;
    user_name: string;
    score: number;
}

export interface ProblemLeaderboard {
    problem_id: number;
    problem_name: string;
    problem_language: string;
    problem_difficulty: number;
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

export interface UserProfile {
    id: string;
    username: string;
    email: string;
    created_at: string;
    updated_at: string;
}

export interface AuthResponse {
    token: string;
    user: UserProfile;
} 