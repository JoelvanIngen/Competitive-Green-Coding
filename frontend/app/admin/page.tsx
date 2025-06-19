import { getSession } from "@/lib/session";
import AdminClient from "./adminClient";

export default async function AdminPage() {
  // Get user session data
  const session = await getSession();
  const user = session?.username as string;

  return (
    <main className="p-8">
      <AdminClient
        user={user}
        session={session}
      // Pass the API data to client component when implemented
      />
    </main>
  );
}