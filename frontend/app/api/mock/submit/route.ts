import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const body = await request.json();
    console.log('submit data:', body);

    const mockSubmit = {
        success: () => NextResponse.json(
            {message: 'Successfully submitted',
             'submission-uuid': 10},
            {status: 201}),

        failed: () => NextResponse.json(
            {message: 'Submit failed'},
            {status: 400}),

        notfound: () => NextResponse.json(
            {message: 'Problem not found'},
            {status: 404}),
    }

    // const keys = Object.keys(mockSubmit) as Array<keyof typeof mockSubmit>;
    // const randomKey = keys[Math.floor(Math.random() * keys.length)];

    // const response = mockSubmit[randomKey]();

    // return response;

    return mockSubmit.success();

}