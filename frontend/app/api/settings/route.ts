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

    const bodyBackendCall = JSON.stringify({
        "user_uuid": session.uuid,
        "key": bodyClient.key,
        "value": bodyClient.value
    })

    /* Make request to backend API */
    const backendResponse = await fetch(`${BACKEND_URL}/settings`, {
        method: 'POST',
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
            type: backendResponse.type || 'Error',
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
