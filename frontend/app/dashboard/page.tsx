"use client";

import { logout } from "../login/actions";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  return (
    <div>
      <Button onClick={() => logout()}>Logout</Button>
    </div>
  );
}