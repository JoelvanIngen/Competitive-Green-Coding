// -----------------------------------------------------------------------------
// Admin API routing
//
// This React component is resposible for the routing of the admin dashboard
// addProblem API. The incoming data will be formatted here to be ready to send
// to the backend endpoint. The response from the backend will be send back to
// the frontend.
// -----------------------------------------------------------------------------

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Extract Authorization header from the incoming request
        const authHeader = request.headers.get('authorization') || '';
        const backendUrl = `${BACKEND_URL}/admin/add-problem`;
        const token = authHeader.replace('Bearer ', ''); // Extract token from Authorization header
        const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'token': token,  // Send token to header 'token'
        },
        body: JSON.stringify(body),
        });

        const text = await response.text();

        if (!response.ok) {
        // Try parsing backend error JSON
        let backendError;
        try {
            backendError = JSON.parse(text);
        } catch {
            backendError = { message: text };
        }

        // Send backend error message back with statuscode
        return NextResponse.json(
            {
            value: {
                type: response.type || 'error',
                description: backendError.message || backendError.description || 'An error occurred',
                details: backendError
            },
            },
            { status: response.status }
        );
        }

        // If successfull, backend returns the created problem ID
        const data = JSON.parse(text);
        return NextResponse.json(data, { status: 200 });
    } catch (error) {
    console.error('POST /admin/add-problem failed:', error);
    return NextResponse.json(
      {
        value: {
          type: 'server_error',
          description: 'An internal server error occurred',
        },
      },
      { status: 500 }
    );
  }
}
