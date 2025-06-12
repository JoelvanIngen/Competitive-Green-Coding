import { NextRequest, NextResponse } from 'next/server';
import { ProblemLeaderboard } from '@/types/api';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

export async function GET(request: NextRequest) {
    try {
        console.log('=== Leaderboard API Request Debug ===');
        console.log('Full URL:', request.url);
        console.log('Method:', request.method);
        console.log('Headers:', Object.fromEntries(request.headers.entries()));

        const searchParams = request.nextUrl.searchParams;
        console.log('Search Params:', Object.fromEntries(searchParams.entries()));
        console.log('BACKEND_URL:', BACKEND_URL);

        const problemId = searchParams.get('problem_id');
        const firstRow = searchParams.get('first_row');
        const lastRow = searchParams.get('last_row');

        console.log('Leaderboard Request Details:', {
            problemId,
            firstRow,
            lastRow
        });

        if (!problemId) {
            console.error('Missing problem_id');
            return NextResponse.json(
                { error: 'Problem ID is required' },
                { status: 400 }
            );
        }

        const backendUrl = `${BACKEND_URL}/leaderboard/${problemId}?first_row=${firstRow}&last_row=${lastRow}`;
        console.log('Making backend request to:', backendUrl);
        console.log('Request headers:', {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${JWT_SECRET_KEY ? 'JWT present' : 'JWT missing'}`
        });

        try {
            const response = await fetch(backendUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${JWT_SECRET_KEY}`
                },
            });

            console.log('Backend Response Status:', response.status);
            console.log('Backend Response Headers:', Object.fromEntries(response.headers.entries()));

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
            console.log('Backend response data:', data);
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