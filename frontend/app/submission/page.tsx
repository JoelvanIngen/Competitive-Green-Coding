import Submission from './client';

type PageProps = {
  searchParams: Promise<{ id: string }>;
};


async function fetchProblem(pid: string) {
const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server_interface:8080/api';

//  const response = await fetch(`http://localhost:3000/api/mock/submission?id=${pid}`, {
  // console.log(pid, 'pid');

  // const testurl = 'http://server_interface:8080/api/problem?problem_id=10000';
  // console.log("testurl:", testurl);

//  const response = await fetch(testurl, {
 const response = await fetch(`${BACKEND_URL}/problem?problem_id=${pid}`, { 
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }});

  if (response.status !== 200) {
    throw new Error(`Failed to fetch problem with id ${pid}, status: ${response.status}`);
  }

  return response.json();
}

export default async function Page({ searchParams }: PageProps) {
  const param = await searchParams;
  const id = param.id ?? '0';

// export default async function Page({ params }: { params: { pid: string } }) {
    // const param = await params;
    // const id = param.pid ?? '0';
    const problemData = await fetchProblem(id);

    return(
        <Submission data={problemData}></Submission>
    );
}