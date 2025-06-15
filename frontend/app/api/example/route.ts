import { NextRequest, NextResponse } from 'next/server';
import { ProblemLeaderboard } from '@/types/api';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const problemId = searchParams.get('problem_id');
        const firstRow = searchParams.get('first_row');
        const lastRow = searchParams.get('last_row');

        if (!problemId) {
            return NextResponse.json(
                { error: 'Problem ID is required' },
                { status: 400 }
            );
        }

        const backendUrl = `${BACKEND_URL}/leaderboard/${problemId}?first_row=${firstRow}&last_row=${lastRow}`;

        try {
            const response = await fetch(backendUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${JWT_SECRET_KEY}`
                },
            });

            if (!response.ok) {
                const text = await response.text();
                return NextResponse.json(
                    { error: 'Failed to fetch leaderboard' },
                    { status: response.status }
                );
            }

            const data = await response.json();
            return NextResponse.json(data);
        } catch (fetchError) {
            throw fetchError;
        }
    } catch (error) {
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
} 