/**
 * File: actions.ts
 * Route: /submission?id=[id]
 * Description:
 * Contains form action handlers and fetch utilities used by the client submission page (client.tsx).
 * Component type: Server actions
 */

'use server';

import { getJWT } from '@/lib/session';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server_interface:8080/api';

async function submitCode(pid: string, language: string, code: string) {
  const jwt = await getJWT() || '';

  const response = await fetch(`${BACKEND_URL}/submission`, { 
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': jwt
      },
      body: JSON.stringify({
        'problem_id': pid,
        language: language,
        code: code
      })
    });
  
  return response;
}

export async function fetchResult(uuid: string) {
  const jwt = await getJWT() || '';

  const response = await fetch(`${BACKEND_URL}/submission-result`, { 
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': jwt
      },
      body: JSON.stringify({
        submission_uuid: uuid
      })
    });

  return response;
}

export async function submit(prevState: any, formData: FormData) {
  const problem_id = formData.get('problemId');
  const code = formData.get('code');
  const language = formData.get('language');

  if (!problem_id || !code || !language) {
    return {status: 400, message: 'Problem ID, code and language are required', submissionuuid: null};
  }

  const response = await submitCode(problem_id.toString(), language.toString(), code.toString());
  const json = await response.json();

  return {status: response.status, message: '', submissionuuid: json['submission_uuid']};
}

export async function getResults(prevState: any, formData: FormData) {
  let submissionuuid = formData.get('submissionuuid');
  if (!submissionuuid) {
    return {submission: '', hastested: true, error: 'MISC', errormsg: 'Something went wrong', testspassed: false, cputime: 0, energyusage: 0, emissions: 0};
  }
  let response = await fetchResult(submissionuuid.toString());

  let pollingActive = true;
  if (response.status !== 200) {
    while(pollingActive) {
      console.log('polling with uuid:', submissionuuid);
      console.log(response.status);
      try {
        if (response.status === 200) {
          pollingActive = false;
          break;
        }
        if (response.status >= 400) {
          pollingActive = false;
          return {submission: '', hastested: true, error: 'MISC', errormsg: 'Something went wrong', testspassed: false, cputime: 0, energyusage: 0, emissions: 0};
        }

      } catch (error) {
        console.error('Polling error:', error);
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
      response = await fetchResult(submissionuuid.toString());
    }
  }

  const json = await response.json();

  return {submission: json['submission_code'], hastested: true, error: json['error_reason'], errormsg: json['error_msg'], testspassed: json['successful'], cputime: json['runtime_ms'], energyusage: json['energy_usage_kwh'], emissions: json['emissions_kg']};
}