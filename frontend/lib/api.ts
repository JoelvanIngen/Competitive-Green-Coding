import { ProblemLeaderboard } from '@/types/api';

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
async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<ApiResponse<T>> {
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

    getProblem: async (problemId: string) => {
        try {
            const response = await fetch(`/api/problems/${problemId}`, {
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

    getProblems: async (page: number, pageSize: number) => {
        try {
            const response = await fetch(
                `/api/problems?page=${page}&page_size=${pageSize}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );

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

    submitSolution: async (problemId: string, solution: any) => {
        return fetchApi(`/api/problems/${problemId}/submit`, {
            method: 'POST',
            body: JSON.stringify(solution),
        });
    },
};

// User API
export const userApi = {
    getProfile: async () => {
        return fetchApi('/api/user/profile');
    },

    updateProfile: async (profileData: any) => {
        return fetchApi('/api/user/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData),
        });
    },
};

// Leaderboard API
export const leaderboardApi = {
    getGlobalLeaderboard: async (page: number, pageSize: number) => {
        return fetchApi(`/api/leaderboard?page=${page}&pageSize=${pageSize}`);
    },

    getLeaderboard: async (problemId: string, firstRow: number, lastRow: number): Promise<ProblemLeaderboard> => {
        try {
            console.log('Making request to:', `/api/leaderboard?problem_id=${problemId}&first_row=${firstRow}&last_row=${lastRow}`);

            const response = await fetch(
                `/api/leaderboard?problem_id=${problemId}&first_row=${firstRow}&last_row=${lastRow}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );

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
    title: string;
    shortDescription: string;
    longDescription: string;
    templateCode: string;
    difficulty: string;
    language: string;
  }, token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `${token}`, // JWT-token in Authorization header
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
