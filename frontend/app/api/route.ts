import { NextRequest, NextResponse } from 'next/server';
import { ProblemLeaderboard } from '@/types/api';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
    try {
        const path = request.nextUrl.pathname.replace('/api/', '');
        const searchParams = request.nextUrl.searchParams;

        // Handle different endpoints
        switch (path) {
            case 'leaderboard': {
                const problemId = searchParams.get('problem_id');
                const firstRow = searchParams.get('first_row');
                const lastRow = searchParams.get('last_row');

                if (!problemId) {
                    return NextResponse.json(
                        { error: 'Problem ID is required' },
                        { status: 400 }
                    );
                }

                const response = await fetch(
                    `${BACKEND_URL}/api/leaderboard/${problemId}?first_row=${firstRow}&last_row=${lastRow}`,
                    {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    }
                );

                if (!response.ok) {
                    const error = await response.json().catch(() => null);
                    return NextResponse.json(
                        { error: error?.message || 'Failed to fetch leaderboard' },
                        { status: response.status }
                    );
                }

                return NextResponse.json(await response.json());
            }

            case 'problems': {
                const page = searchParams.get('page');
                const pageSize = searchParams.get('page_size');
                const problemId = searchParams.get('id');

                // If problemId is provided, get specific problem
                if (problemId) {
                    const response = await fetch(
                        `${BACKEND_URL}/api/problems/${problemId}`,
                        {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                        }
                    );

                    if (!response.ok) {
                        const error = await response.json().catch(() => null);
                        return NextResponse.json(
                            { error: error?.message || 'Failed to fetch problem' },
                            { status: response.status }
                        );
                    }

                    return NextResponse.json(await response.json());
                }

                // Otherwise get problems list
                const response = await fetch(
                    `${BACKEND_URL}/api/problems?page=${page}&page_size=${pageSize}`,
                    {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    }
                );

                if (!response.ok) {
                    const error = await response.json().catch(() => null);
                    return NextResponse.json(
                        { error: error?.message || 'Failed to fetch problems' },
                        { status: response.status }
                    );
                }

                return NextResponse.json(await response.json());
            }

            default:
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