import { ProblemLeaderboard, ProblemDetailsResponse, ProblemsListResponse, ProblemsFilterRequest, ProfileResponse, ProfileUpdateRequest, ProfileUpdateResponse } from '@/types/api';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

//----------------------------------------------------------------------//
// This file handles all the API calls to the backend.                  //
// It handles most calls and is done here via proxy to be able to call  //
// client side by using the relative path instead of a full url.        //
//----------------------------------------------------------------------//

// Problems API makes a POST request to the /api/problems endpoint with the limit parameter
// The limit parameter is the number of problems to fetch from the backend
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

// Leaderboard API makes a POST request to the /api/leaderboard endpoint with the problemId, firstRow, and lastRow parameters
// The problemId is the id of the problem to fetch the leaderboard for
// The firstRow and lastRow are the rows to fetch from the leaderboard
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

// Add problem API makes a POST request to the /api/admin/addProblem endpoint with the problemData and token parameters
// The problemData is the data of the problem to add
// The token is the token of the user to add the problem
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
            const response = await fetch('/api/admin/addProblem', {
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

// Remove problem API makes a POST request to the /api/admin/removeProblem endpoint with the problemData and token parameters
// The problemData is the data of the problem to remove
// The token is the token of the user to remove the problem (only admins can remove problems)
export const removeProblemAPI = {
    removeProblem: async (problemData: {
        problem_id: number;
    }, token: string | null) => {
        try {
            const response = await fetch('/api/admin/removeProblem', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(problemData),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to remove problem: ${errorText || response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Remove problem API error:', error);
            throw error;
        }
    },
};

// Profile API makes a GET request to the /api/profile/{username} endpoint with the username parameter
// The username is the username of the user to fetch the profile for
export const profileApi = {
    getUserProfile: async (username: string): Promise<ProfileResponse> => {
        const isServer = typeof window === 'undefined';
        const url = isServer
            ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000') + `/api/profile/${username}`
            : `/api/profile/${username}`;
        try {
            const response = await fetch(url, {
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

    // Update profile API makes a PUT request to the /api/profile/{username} endpoint with the username and updates parameters
    // The username is the username of the user to update the profile for
    // The updates is the updates to the profile
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