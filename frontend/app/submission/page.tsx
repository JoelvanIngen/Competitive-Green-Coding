import Submission from './client';
import { Button } from "@/components/ui/button";

import { fetchResult } from './actions';

import { getJWT } from '@/lib/session'

type PageProps = {
  searchParams: Promise<{ id: string }>;
};

async function fetchProblem(pid: string) {
  const jwt = await getJWT() || '';
  const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server_interface:8080/api';

  // const testurl = `http://localhost:3000/api/mock/submission?id=${pid}`;
  // const response = await fetch(testurl, {
  console.log('api/problem:', pid);

 const response = await fetch(`${BACKEND_URL}/problem?problem_id=${pid}`, { 
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'token': jwt
      }});

  return response
}

export default async function Page({ searchParams }: PageProps) {
  const param = await searchParams;
  const id = param.id ?? '0';

  const fetched = await fetchProblem(id);

  if (fetched.status != 200) {
    return(
      <div className='bg-theme-bg justify-center items-center flex h-[calc(100vh-82px)]'>
        <div>
          <img className='h-[10rem]' src='images\submission\pass\incognito\full.png'></img>
        </div>
        <div>  
          <h2 className='font-bold text-4xl'>404</h2>
          <p className='font-bold text-2xl'>Detective Groot has lost the page.</p>
          <Button className='mt-2'><a href='/problems'>Get me back to safety</a></Button>
        </div>
      </div>
    );
  }

  const problemData = await fetched.json();

  const problemDataClient = {templateCode: problemData['template_code'],
    difficulty: problemData.difficulty,
    pid: problemData['problem_id'],
    name: problemData.name,
    language: problemData.language,
    tags: problemData.tags,
    longDesc: problemData['long_description']}

  if (problemData.submissionuuid !== '') {
    const response = await fetchResult(problemData.submissionuuid);
    const json = await response.json();
    const submissionData = {prevsubmission: true, hastested: true, error: json['error_msg'], errormsg: json['error_reason'], testspassed: json['successful'], cputime: json['runtime_ms'], energyusage: json['energy_usage_kwh']}

    return(
      <Submission data={problemDataClient} subData={submissionData}></Submission>
    );
  }

  return(
    <Submission data={problemDataClient} subData={{prevsubmission: false, hastested: false, error: '', errormsg: '', testspassed: false, cputime: 0, energyusage: 0}}></Submission>
  );
}