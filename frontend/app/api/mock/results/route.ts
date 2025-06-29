import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const mockResult = {
        success: () => NextResponse.json(
            {
                submission_uuid: 'fkasjdfkljdsakljf',
                runtime_ms: 1.617823,
                emissions_kg: 89834,
                energy_usage_kwh: .0044832904832,
                successful: true,
                error_reason: '',
                error_msg: ''
            }, {status: 200}),
        fail: () => NextResponse.json(
            {
                submission_uuid: 'fkasjdfkljdsakljf',
                runtime_ms: 2.617823,
                emissions_kg: 89334,
                energy_usage_kwh: 102034,
                successful: false,
                error_reason: 'compiler',
                error_msg: 'Syntax error on line 1'
            }, {status: 200}),
        testsfail: () => NextResponse.json(
            {
                submission_uuid: 'fkasjdfkljdsakljf',
                runtime_ms: 2.617823,
                emissions_kg: 89334,
                energy_usage_kwh: 102034,
                successful: false,
                error_reason: 'tests_failed',
                error_msg: 'Failed test 4'
            }, {status: 200})


        //     {'error': null,
        //      'description': 'All tests passed.',
        //      'tests-passed': 10,
        //      'tests-failed': 0,
        //      'cpu-time': 1.112},
        //     {status: 200}),
        // compiler: () => NextResponse.json(
        //     {'error': 'compiler',
        //      'description': 'Syntax error on line 4.',
        //      'tests-passed': 0,
        //      'tests-failed': 0,
        //      'cpu-time': 0},
        //     {status: 200}),
        // tests: () => NextResponse.json(
        //     {'error': 'test',
        //      'description': 'Failed test 4, 5 and 9',
        //      'tests-passed': 7,
        //      'tests-failed': 3,
        //      'cpu-time': 1.538},
        //     {status: 200}),
        // fault1: () => NextResponse.json(
        //     {'message': 'Not ready yet'},
        //     {status: 202}),
        // fault2: () => NextResponse.json(
        //     {'message': 'Not ready yet'},
        //     {status: 202}),
        // fault3: () => NextResponse.json(
        //     {'message': 'Not ready yet'},
        //     {status: 202}),
        // fault4: () => NextResponse.json(
        //     {'message': 'Not ready yet'},
        //     {status: 202})
    }

    // random response
    // const keys = Object.keys(mockResult);
    // const randomKey = keys[Math.floor(Math.random() * keys.length)];
    // const response = mockResult[randomKey]();
    // return response;

      // Cast `keys` so TypeScript knows each element IS one of the real keys
    // const keys = Object.keys(mockResult) as Array<keyof typeof mockResult>;
    // const randomKey = keys[Math.floor(Math.random() * keys.length)];
    // return mockResult[randomKey]();

    return mockResult.success();
}
