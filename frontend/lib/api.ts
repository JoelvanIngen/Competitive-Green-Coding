import { ProblemLeaderboard, ProblemDetailsResponse, ProblemsListResponse, ProblemsFilterRequest, ProfileResponse, ProfileUpdateRequest, ProfileUpdateResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

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
    getLeaderboard: async (problemId: string, firstRow: number, lastRow: number) => {
        return fetchApi<ProblemLeaderboard>(
            `/api/problems/${problemId}/leaderboard?first_row=${firstRow}&last_row=${lastRow}`
        );
    },

    getProblem: async (problemId: string): Promise<ProblemDetailsResponse> => {
        try {
            const response = await fetch(`/api/problem?problem-id=${problemId}`, {
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
                throw new Error(`Failed to fetch problem: ${response.statusText}`);
            }

            return response.json();
        } catch (error) {
            console.error('Problem API error:', error);
            throw error;
        }
    },

    getProblems: async (params?: {
        difficulty?: 'easy' | 'medium' | 'hard';
        search?: string;
        offset?: number;
        limit?: number;
    }): Promise<ProblemsListResponse> => {
        try {
            const searchParams = new URLSearchParams();
            if (params?.difficulty) searchParams.append('difficulty', params.difficulty);
            if (params?.search) searchParams.append('search', params.search);
            if (params?.offset) searchParams.append('offset', params.offset.toString());
            if (params?.limit) searchParams.append('limit', params.limit.toString());

            const response = await fetch(`/api/problems?${searchParams.toString()}`, {
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
                throw new Error(`Failed to fetch problems: ${response.statusText}`);
            }

            return response.json();
        } catch (error) {
            console.error('Problems API error:', error);
            throw error;
        }
    },

    filterProblems: async (filter: ProblemsFilterRequest): Promise<ProblemsListResponse> => {
        try {
            const response = await fetch('/api/problems', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(filter),
            });

            if (!response.ok) {
                const text = await response.text();
                console.error('Error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: text
                });
                throw new Error(`Failed to filter problems: ${response.statusText}`);
            }

            return response.json();
        } catch (error) {
            console.error('Problems API error:', error);
            throw error;
        }
    },

    submitSolution: async (problemId: string, solution: any) => {
        return fetchApi(`/api/problems/${problemId}/submit`, {
            method: 'POST',
            body: JSON.stringify(solution),
        });
    },

    getAllProblems: async (limit?: number): Promise<ProblemsListResponse> => {
        const response = await fetch('/api/problems', {
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
    getGlobalLeaderboard: async (page: number, pageSize: number) => {
        return fetchApi(`/api/leaderboard?page=${page}&pageSize=${pageSize}`);
    },

    getLeaderboard: async (problemId: string, firstRow: number, lastRow: number): Promise<ProblemLeaderboard> => {
        try {
            // Use absolute URL for server-side requests
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';
            const url = new URL('/api/leaderboard', baseUrl);
            url.searchParams.append('problem_id', problemId);
            url.searchParams.append('first_row', firstRow.toString());
            url.searchParams.append('last_row', lastRow.toString());

            console.log('Making request to:', url.toString());
            const response = await fetch(url.toString(), {
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
                throw new Error(`Failed to fetch leaderboard: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Received data:', data);
            return data;
        } catch (error) {
            console.error('Leaderboard API error:', error);
            throw error;
        }
    },

    // New POST method for leaderboard
    postLeaderboard: async (problemId: string, firstRow: number, lastRow: number): Promise<ProblemLeaderboard> => {
        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';
            const url = new URL('/api/leaderboard', baseUrl);

            const response = await fetch(url.toString(), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ID: Number(problemId),
                    "first-row": Number(firstRow),
                    "last-row": Number(lastRow)
                })
            });

            if (!response.ok) {
                const text = await response.text();
                console.error('Error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: text
                });
                throw new Error(`Failed to fetch leaderboard: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Leaderboard API error:', error);
            throw error;
        }
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