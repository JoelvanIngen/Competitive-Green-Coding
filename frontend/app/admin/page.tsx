// -----------------------------------------------------------------------------
// Admin page
//
// This page displays the admin dashboard, allowing administrators to
// add, remove, and view problems. It fetches user session data and passes it
// to the AdminClient component.
// -----------------------------------------------------------------------------

import { getSession, getJWT } from "@/lib/session";
import AdminClient from "./adminClient";

export default async function AdminPage() {
  // Get user session data
  const session = await getSession();
  const user = session?.username as string;
  const tokenJWT = await getJWT();

  return (
    <main className="p-8">
      <AdminClient
        user={user}
        tokenJWT={tokenJWT}
      // Pass the API data to client component when implemented
      />
    </main>
  );
}