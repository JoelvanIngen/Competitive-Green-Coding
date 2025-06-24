import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const mockResult = {
        success: () => NextResponse.json(
            {'error': null,
             'description': 'All tests passed.',
             'tests-passed': 10,
             'tests-failed': 0,
             'cpu-time': 1.112},
            {status: 200})
    }

    return mockResult.success();
}