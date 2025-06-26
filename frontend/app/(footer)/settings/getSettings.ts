"use server"

import { getJWT } from "@/lib/session";

const BACKEND_URL = process.env.BACKEND_API_URL;

interface getSettingsResponse {
    uuid: string;
    username: string;
    email: string;
    permission_level: string;
    avatar_id: number;
    private: boolean;
}

/**
 * Fetches user settings from the backend API.
 * 
 * This function retrieves the current user's settings including profile information
 * such as username, email, avatar, and privacy preferences. It requires a valid
 * JWT token to authenticate the request.
 * 
 * @returns Promise<getSettingsResponse> - The user's settings data
 * @throws Error - If no JWT token is available (assumes caller is logged in)
 */
export async function getSettings(): Promise<getSettingsResponse> {
    const JWT = await getJWT();

    if (!JWT) {
        throw new Error("No JWT found");
    }

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${JWT}`
    }

    const backendResponse: Response = await fetch(`${BACKEND_URL}/settings`, {
        method: 'GET',
        headers: headers,
    });

    const backendResponseBody: getSettingsResponse = await backendResponse.json();
    return backendResponseBody;
} 
