import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id') ?? '0';
    
    const mockData = {
        pid: id, 
        name: 'Sum of Two Numbers',
        language: 'python',
        difficulty: 'Easy',
        tags: ['arithmetic'],
        shortDesc: 'Write a function that returns the sum of two integers.',
        longDesc: `# Problem:\nWrite a Python program that takes two numbers as input and returns their sum.\n\n# Input\n- Two numbers (integers or floats).\n# Output:\n- A single number representing the sum of the two inputs.\n\n# Example:\n~~~python\ndef sumTwoNumbers(3, 5) -> 8\n~~~`,
        templateCode: 'def sumTwoNumbers(x, y):\n\t# Here comes your code.'
    };

    return NextResponse.json(mockData);
}