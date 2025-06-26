import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Haal de Authorization header uit de inkomende request
        const authHeader = request.headers.get('authorization') || '';
        const backendUrl = `${BACKEND_URL}/admin/remove-problem`;
        const token = authHeader.replace('Bearer ', ''); // haal token uit Authorization header
        const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(body),
        });

        const text = await response.text();

        if (!response.ok) {
        // Probeer backend error JSON te parsen
        let backendError;
        try {
            backendError = JSON.parse(text);
        } catch {
            backendError = { message: text };
        }

        // Stuur de backend error message door, met statuscode
        return NextResponse.json(
            {
            value: {
                type: response.type || 'error',
                description: backendError.message || backendError.description || 'An error occurred',
                // eventueel hele backendError object toevoegen als je meer info wilt:
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
    console.error('POST /admin/remove-problem failed:', error);
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
