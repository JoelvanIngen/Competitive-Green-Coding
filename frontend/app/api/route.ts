import { NextRequest, NextResponse } from 'next/server';
import { ProblemLeaderboard } from '@/types/api';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
    try {
        const path = request.nextUrl.pathname.replace('/api/', '');
        const searchParams = request.nextUrl.searchParams;

        console.log('API Route - Request:', {
            path,
            searchParams: Object.fromEntries(searchParams.entries())
        });

        // Handle different endpoints
        switch (path) {
            case 'leaderboard': {
                const problemId = searchParams.get('problem_id');
                const firstRow = searchParams.get('first_row');
                const lastRow = searchParams.get('last_row');

                if (!problemId) {
                    console.error('Missing problem_id');
                    return NextResponse.json(
                        { error: 'Problem ID is required' },
                        { status: 400 }
                    );
                }

                const backendUrl = `${BACKEND_URL}/api/leaderboard/${problemId}?first_row=${firstRow}&last_row=${lastRow}`;
                console.log('Making backend request to:', backendUrl);

                const response = await fetch(backendUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    const text = await response.text();
                    console.error('Backend error response:', {
                        status: response.status,
                        statusText: response.statusText,
                        body: text
                    });
                    return NextResponse.json(
                        { error: 'Failed to fetch leaderboard' },
                        { status: response.status }
                    );
                }

                const data = await response.json();
                console.log('Backend response:', data);
                return NextResponse.json(data);
            }

            case 'problems': {
                const page = searchParams.get('page');
                const pageSize = searchParams.get('page_size');
                const problemId = searchParams.get('id');

                // If problemId is provided, get specific problem
                if (problemId) {
                    const backendUrl = `${BACKEND_URL}/api/problems/${problemId}`;
                    console.log('Making backend request to:', backendUrl);

                    const response = await fetch(backendUrl, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    if (!response.ok) {
                        const text = await response.text();
                        console.error('Backend error response:', {
                            status: response.status,
                            statusText: response.statusText,
                            body: text
                        });
                        return NextResponse.json(
                            { error: 'Failed to fetch problem' },
                            { status: response.status }
                        );
                    }

                    const data = await response.json();
                    console.log('Backend response:', data);
                    return NextResponse.json(data);
                }

                // Otherwise get problems list
                const backendUrl = `${BACKEND_URL}/api/problems?page=${page}&page_size=${pageSize}`;
                console.log('Making backend request to:', backendUrl);

                const response = await fetch(backendUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    const text = await response.text();
                    console.error('Backend error response:', {
                        status: response.status,
                        statusText: response.statusText,
                        body: text
                    });
                    return NextResponse.json(
                        { error: 'Failed to fetch problems' },
                        { status: response.status }
                    );
                }

                const data = await response.json();
                console.log('Backend response:', data);
                return NextResponse.json(data);
            }

            default:
                console.error('Invalid endpoint:', path);
                return NextResponse.json(
                    { error: 'Invalid endpoint' },
                    { status: 404 }
                );
        }
    } catch (error) {
        console.error('API request error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
} 