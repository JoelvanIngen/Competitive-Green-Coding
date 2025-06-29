/**
 * Settings page for user preferences.
 * The page GETs the current user settings and passes them to the SettingsWidget component.
 * It ensures the user is logged in before rendering the settings.
 */

"use server";

import { getSession } from "@/lib/session";
import { redirect } from "next/navigation";

import SettingsWidget from "./settings-widget";
import { getSettings, getSettingsResponse } from "./getSettings";

export default async function SettingsPage() {
  /* Ensure user is logged in (should be handled by middleware but just in case) */
  const session = await getSession();
  if (!session) {
    redirect("/login");
  }

  const currentSettings: getSettingsResponse = await getSettings();

  return <SettingsWidget currentSettings={currentSettings} />;
}
