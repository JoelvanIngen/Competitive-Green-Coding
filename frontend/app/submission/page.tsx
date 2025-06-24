import Submission from './client';

type PageProps = {
  searchParams: { id: string };
};

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://server:8080/api';

async function fetchProblem(pid: string) {
// `${BACKEND_URL}/problem/${pid}`
 const response = await fetch(`http://localhost:3000/api/mock/submission?id=${pid}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }});

  console.log("fetchProblem:", response.status);

  if (!response.ok) {
    throw new Error('Failed to fetch problem');
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