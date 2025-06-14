import { Button } from "@/components/ui/button";

import { logout } from "@/app/(footer)/login/actions";
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
        <a href="/login" className="inline-block">
          <Button type="button">Log in</Button>
        </a>
      </div>
    );
  }

  const user = session.username as string;
  
  return (
    <div>
      <h1 className="text-4xl font-bold mb-4">Welcome, {user}!</h1>
      <form action={logout}>
        <Button type="submit">Log out</Button>
      </form>
    </div>
  );
}
