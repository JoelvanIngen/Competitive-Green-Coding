import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { name, language, difficulty, tags, short_description, long_description, template_code } = body;

        const backendUrl = `${BACKEND_URL}/admin/add-problem`;

        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${JWT_SECRET_KEY}`
            },
            body: JSON.stringify({
                name,
                language,
                difficulty,
                tags,
                short_description,
                long_description,
                template_code

            })
        });

        const text = await response.text();

        if (!response.ok) {
            // Try to parse backend error if it's JSON
            let backendError;
            try {
              backendError = JSON.parse(text);
            } catch {
              backendError = { message: text };
            }

            switch (response.status) {
                case 400:
                return NextResponse.json(
                    {
                    value: {
                        type: 'validation',
                        description: "Title is required\nDifficulty must be one of: easy, medium, hard"
                    },
                    },
                    { status: 400 }
                );
                case 401:
                return NextResponse.json(
                    {
                    value: {
                        type: 'unauthorized',
                        description: 'User does not have admin permissions',
                    },
                    },
                    { status: 401 }
                );
                case 404:
                return NextResponse.json(
                    {
                    value: {
                        type: 'not_found',
                        description: 'Endpoint not found',
                    },
                    },
                    { status: 404 }
                );
                default:
                return NextResponse.json(
                    {
                    value: {
                        type: 'server_error',
                        description: 'An internal server error occurred',
                    },
                    },
                    { status: response.status }
                );
            }
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

export async function GET(request: NextRequest) {
    const backendUrl = `${BACKEND_URL}/admin/my-problems`;

    try {
        const response = await fetch(backendUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${JWT_SECRET_KEY}`,
            },
        });

        if (response.status === 401) {
            return NextResponse.json(
                {
                    value: {
                        type: "unauthorized",
                        description: "User does not have admin permissions",
                    },
                },
                { status: 401 }
            );
        }

        if (response.status === 404) {
            return NextResponse.json(
                {
                    value: {
                        type: "not_found",
                        description: "Endpoint not found",
                    },
                },
                { status: 404 }
            );
        }

        if (!response.ok) {
            const text = await response.text();
            return NextResponse.json(
                { error: `Unexpected error: ${text}` },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('Fetch error:', error);
        return NextResponse.json(
            { error: 'An internal server error occurred' },
            { status: 500 }
        );
    }
}
