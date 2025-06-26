import { NextResponse } from "next/server";

import { getJWT, getSession, deleteJWT, setJWT } from "@/lib/session";

const BACKEND_URL = process.env.BACKEND_API_URL;


export async function PUT(request: Request) {
    /* Check backend url. */
    if (!BACKEND_URL) {
        return NextResponse.json({
            type: 'Internal Server Error',
            description: 'Backend API URL not configured.'
        },

            { status: 500 });
    }

    /* Get and check the JWT. */
    const JWT = await getJWT();
    const session = await getSession();

    // If no session or JWT, return unauthorized
    if (!session || !JWT) {
        return NextResponse.json({
            type: 'Unauthorized',
            description: 'Authentication failed. Please log out and log back in to continue.'
        },

            { status: 401 });
    }

    /* Prepare backend request */
    const bodyClient = await request.json();

    // For username or password change: validate password first
    if (bodyClient.key === "username" || bodyClient.key === "password") {
        const validationError = await validateUserPassword(
            session.username, 
            bodyClient.password, 
            bodyClient.key
        );
        
        if (validationError) {
            return validationError;
        }
    }

    const bodyBackendCall = JSON.stringify({
        "user_uuid": session.uuid,
        "key": bodyClient.key,
        "value": bodyClient.value
    })

    /* Make request to backend API */
    const backendResponse = await fetch(`${BACKEND_URL}/settings`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${JWT}`
        },
        body: bodyBackendCall
    });

    const backendResponseBody = await backendResponse.json();

    /* Backend FAIL: forward to client. */
    if (!backendResponse.ok) {
        return NextResponse.json({
            type: backendResponseBody.type || 'Error',
            description: backendResponseBody.description || 'An internal server error occurred while updating settings. Please try again later.'
        },

            { status: backendResponse.status });
    }

    /* Backend SUCCESS: update session cookie and redirect. */
    const newJWT = backendResponseBody.access_token;
    if (!newJWT) {
        return NextResponse.json({
            type: 'Internal Server Error',
            description: 'Backend did not return a new JWT.'
        },

            { status: 500 });
    }

    // Replace the old JWT with the new one
    await deleteJWT();
    await setJWT(newJWT);

    // Redirect to refresh the page with new JWT cookie
    const url = new URL('/settings', request.url);
    return NextResponse.redirect(url, 303); // 303 status code tells the browser to GET the new URL
}


/*
 * ██   ██ ███████ ██      ██████  ███████ ██████  ███████ 
 * ██   ██ ██      ██      ██   ██ ██      ██   ██ ██      
 * ███████ █████   ██      ██████  █████   ██████  ███████ 
 * ██   ██ ██      ██      ██      ██      ██   ██      ██ 
 * ██   ██ ███████ ███████ ██      ███████ ██   ██ ███████ 
 */

/**
 * Validates user password by attempting login with current credentials
 * 
 * @param username - Current username from session
 * @param password - Password to validate
 * @param operationType - Type of operation requiring validation ("username" | "password")
 * 
 * @returns NextResponse with error details if validation fails, null if successful
 */
async function validateUserPassword(
    username: string, 
    password: string, 
    operationType: "username" | "password"
): Promise<NextResponse | null> {
    const passwordValidationResponse = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username: username,
            password: password
        }),
    });

    if (!passwordValidationResponse.ok) {
        /* Parse error response. */
        let passwordValidationResponseBody = await passwordValidationResponse.json();
        
        /* Handle nested detail object */
        if (passwordValidationResponseBody.detail && 
            typeof passwordValidationResponseBody.detail === 'object' && 
            !Array.isArray(passwordValidationResponseBody.detail)) {
            passwordValidationResponseBody = passwordValidationResponseBody.detail;
        }
        
        /* Choose appropriate client error. */
        let type: string;
        let description: string;
        
        if (passwordValidationResponseBody.type === "invalid") {
            type = operationType === "password" ? 
                'Invalid Current Password' : 
                'Invalid Password';
                
            description = operationType === "password" ? 
                'The provided current password was incorrect. Please try again.' : 
                'The provided password was incorrect. Please try again.';
        } else {
            type = passwordValidationResponseBody.type || (operationType === "password" ? 
                'Current Password Validation Error' : 
                'Password Validation Error');
            
            description = passwordValidationResponseBody.description || (operationType === "password" ? 
                'An internal server error occurred while validating the current password. Please try again later.' : 
                'An internal server error occurred while validating the password. Please try again later.');
        }

        /* Return error response */
        return NextResponse.json({
            type: type,
            description: description
        }, { status: passwordValidationResponse.status });
    }

    return null; // Validation successful
}