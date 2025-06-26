/**
 * This file contains the getSettings function, which is used to fetch the user's settings from the backend API.
 * It is used in the settings page to display the user's settings.
 * 
 * The getSettings function returns a Promise<getSettingsResponse>, which is a type that contains the user's settings.
 * 
 * The getSettingsResponse type is defined in this file, and it is used to type the return value of the getSettings function.
 * 
 * The getSettings function is exported, so it can be used in other files.
 */

"use server"

import { getJWT } from "@/lib/session";

const BACKEND_URL = process.env.BACKEND_API_URL;

export interface getSettingsResponse {
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
