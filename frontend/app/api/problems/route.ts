import { NextRequest, NextResponse } from 'next/server';
import { ProblemsListResponse } from '@/types/api';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

// Handle POST /api/problems for basic info with only limit
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { limit } = body;

        const backendUrl = `${BACKEND_URL}/problems/all`;

        try {
            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${JWT_SECRET_KEY}`
                },
                body: JSON.stringify(limit !== undefined ? { limit } : {}),
            });

            if (!response.ok) {
                const text = await response.text();
                console.error('Backend error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: text
                });
                return NextResponse.json(
                    { error: 'Failed to fetch all problems' },
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