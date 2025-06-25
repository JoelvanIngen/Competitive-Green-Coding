import { NextRequest, NextResponse } from 'next/server';
import { ProblemLeaderboard } from '@/types/api';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const problem_id = body.problem_id;
        const first_row = body.first_row;
        const last_row = body.last_row;
        console.log("body: ", body);
        console.log("problem_id: ", problem_id);
        console.log("first_row: ", first_row);
        console.log("last_row: ", last_row);

        /*if (!problem_id) {
            console.error('Missing ID');
            return NextResponse.json(
                { error: 'Problem ID is required' },
                { status: 400 }
            );
        }*/

        const backendUrl = `${BACKEND_URL}/leaderboard`;
        console.log("backendUrl: ", backendUrl);
        console.log("ID ROUTE: ", problem_id);
        try {
            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    problem_id: Number(problem_id),
                    first_row: Number(first_row),
                    last_row: Number(last_row)
                })
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
            return NextResponse.json(data);
        } catch (fetchError) {
            console.error('Fetch error:', fetchError);
            throw fetchError;
        }
    } catch (error) {
        console.error('API request error:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
} 