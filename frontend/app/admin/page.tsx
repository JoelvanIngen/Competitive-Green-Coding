// Admin page
//
// This page displays the admin dashboard, allowing administrators to
// add, remove, and view problems. It fetches user session data and passes it
// to the AdminClient component.
// -----------------------------------------------------------------------------

import { getJWT } from "@/lib/session";
import AdminClient from "./adminClient";

export default async function AdminPage() {
  // Get user JWT token
  const tokenJWT = await getJWT();

  return (
    <main className="p-8">
      <AdminClient
        tokenJWT={tokenJWT}
      />
    </main>
  );
}