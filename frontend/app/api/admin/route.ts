import { NextRequest, NextResponse } from 'next/server';
import { ProblemLeaderboard } from '@/types/api';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { name, language, difficulty, tags, short_description, long_description, template_code } = body;

        const backendUrl = `${BACKEND_URL}/admin/add-problem`;

        try {
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

            if (!response.ok) {
                const text = await response.text();
                console.error('Backend error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: text
                });
                return NextResponse.json(
                    { error: 'Failed to filter problems' },
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

export async function GET(request: NextRequest) {
    try {

        const backendUrl = `${BACKEND_URL}/admin/my-problems`;

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
                    { error: 'Failed to fetch problems' },
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