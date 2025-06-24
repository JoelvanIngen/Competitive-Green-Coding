"use server"

import { getJWT, getSession } from "@/lib/session";
import { redirect } from 'next/navigation';

import SettingsWidget from "./settings-widget"

export default async function SettingsPage() {
  const session = await getSession();

  if (!session) {
    // This should never happen because of middleware,
    // but satisfies TypeScript
    redirect('/login');
  }

  const BACKEND_URL = process.env.BACKEND_API_URL
  const response = await fetch(`${BACKEND_URL}/settings`, { 
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getJWT()}`
      },
      body: JSON.stringify({
        "user_uuid": session.uuid,
        "key": "avatar_id",
        "value": "4",
      })
  });

  const responseText = await response.text();

  return (
    <>
      <p className="text-center">{responseText}</p>
      <p className="text-center">{JSON.stringify(session)}</p>
      <SettingsWidget session={session} />
    </>
  )
}
