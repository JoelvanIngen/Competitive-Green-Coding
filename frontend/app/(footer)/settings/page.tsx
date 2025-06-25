"use server"

import { getSession } from "@/lib/session";
import { redirect } from 'next/navigation';

import SettingsWidget from "./settings-widget"
import CallAndShow from "./debug-backend-calls";

export default async function SettingsPage() {
  const session = await getSession();

  if (!session) {
    // This should never happen because of middleware,
    // but satisfies TypeScript
    redirect('/login');
  }

  return (
    <SettingsWidget session={session} />
    // <CallAndShow/>
  )
}
