'use server';

import { getJWT } from '@/lib/session';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';

async function submitCode(pid: string, code: string) {
  const jwt = await getJWT();
  console.log('JWT:', jwt);

  const response = await fetch(`http://localhost:3000/api/mock/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwt}`
      },
      body: JSON.stringify({
        'problem-id': pid,
        'code': code
      })
    });
  
  console.log('submitCode:', response.status);

  return response;
}

async function fetchResult(pid: string) {
  const jwt = await getJWT();

  const response = await fetch(`http://localhost:3000/api/mock/results`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwt}`
      },
      body: JSON.stringify({
        'problem-id': pid
      })
    });

  console.log('codeResult:', response.status);

  if (!response.ok) {
    // throw new Error('Failed to fetch problem');
    return '';
  }

  return response.json();
}

export async function submit(prevState: any, formData: FormData) {
  const problem_id = formData.get('problemId');
  const code = formData.get('code');

  const response = await submitCode(problem_id, code);
  const json = await response.json();

  console.log(json);

  return {status: response.status, message: json.message, submissionuuid: json['submissionuuid']};
}

export async function getResults(prevState: any, formData: FormData) {
  const problem_id = formData.get('problemId');

  const response = await fetchResult(problem_id);

  console.log(response);

  return {hastested: true, error: response.error, desc: response.description, testspassed: response['tests-passed'], testsfailed: response['tests-failed'], cputime: response['cpu-time']};
}