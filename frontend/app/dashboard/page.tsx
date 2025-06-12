import { getSession } from "@/lib/session";

export default function DashboardPage() {
  return (
    <div className="pt-16 pb-16 mx-8 flex justify-center">
      <GreetUser />
    </div>
  );
}

async function GreetUser() {
  const session = await getSession();
  
  if (!session) {
    return (
      <div>
        <h1 className="text-4xl font-bold mb-4">You are not logged in</h1>
      </div>
    );
  }

  const user = session.username as string;
  
  return (
    <div>
      <h1 className="text-4xl font-bold mb-4">Welcome, {user}!</h1>
    </div>
  );
}
