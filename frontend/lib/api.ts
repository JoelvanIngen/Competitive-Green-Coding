import { ProblemLeaderboard, ProblemDetailsResponse, ProblemsListResponse, ProblemsFilterRequest, ProfileResponse, ProfileUpdateRequest, ProfileUpdateResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

interface ApiResponse<T> {
    data?: T;
    error?: string;
}

interface ApiRequest {
    endpoint: string;
    method: string;
    body: any;
    headers?: Record<string, string>;
}

// Helper function for making API calls
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { data };
    } catch (error) {
        console.error('API call failed:', error);
        return { error: error instanceof Error ? error.message : 'An error occurred' };
    }
}

// Problems API
export const problemsApi = {
    getAllProblems: async (limit?: number): Promise<ProblemsListResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/problems`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(limit !== undefined ? { limit } : {}),
        });
        if (!response.ok) {
            const text = await response.text();
            console.error('Error response:', {
                status: response.status,
                statusText: response.statusText,
                body: text
            });
            throw new Error(`Failed to fetch all problems: ${response.statusText}`);
        }
        return response.json();
    },
};

// Leaderboard API
export const leaderboardApi = {
    postLeaderboard: async (problemId: string | number, firstRow: number, lastRow: number): Promise<ProblemLeaderboard> => {
        // If running in the browser, use relative path
        // If running on the server, use absolute URL
        const isServer = typeof window === 'undefined';
        const url = isServer
            ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000') + '/api/leaderboard'
            : '/api/leaderboard';

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                problem_id: Number(problemId),
                first_row: Number(firstRow),
                last_row: Number(lastRow)
            })
        });

        if (!response.ok) {
            const text = await response.text();
            throw new Error(`Failed to fetch leaderboard: ${response.statusText}`);
        }

        return response.json();
    }
};

// Profile API
export const profileApi = {
    getUserProfile: async (username: string): Promise<ProfileResponse> => {
        try {
            const response = await fetch(`/api/profile/${username}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const text = await response.text();
                console.error('Error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: text
                });
                throw new Error(`Failed to fetch profile: ${response.statusText}`);
            }

            return response.json();
        } catch (error) {
            console.error('Profile API error:', error);
            throw error;
        }
    },

    updateProfile: async (username: string, updates: ProfileUpdateRequest): Promise<ProfileUpdateResponse> => {
        try {
            const response = await fetch(`/api/profile/${username}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    // Note: This would need authentication headers in a real implementation
                    // 'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(updates),
            });

            if (!response.ok) {
                const text = await response.text();
                console.error('Error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: text
                });
                throw new Error(`Failed to update profile: ${response.statusText}`);
            }

            return response.json();
        } catch (error) {
            console.error('Profile update API error:', error);
            throw error;
        }
    }
};

// Auth API
export const authApi = {
    login: async (credentials: { email: string; password: string }) => {
        return fetchApi('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
    },

    register: async (userData: any) => {
        return fetchApi('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },

    logout: async () => {
        return fetchApi('/api/auth/logout', {
            method: 'POST',
        });
    },
};

// Add problem API
export const addProblemAPI = {
    addProblem: async (problemData: {
        name: string;
        language: string;
        difficulty: string;
        tags: string[];
        short_description: string;
        long_description: string;
        template_code: string;
        wrappers: string[][];
    }, token: string | null) => {
        try {
            const response = await fetch('/api/admin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(problemData),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to submit problem: ${errorText || response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Add problem API error:', error);
            throw error;
        }
    },
};
