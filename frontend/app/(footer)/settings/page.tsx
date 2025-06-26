"use server"

import { getSession } from "@/lib/session";
import { redirect } from 'next/navigation';

import SettingsWidget from "./settings-widget"
import CallAndShow from "./debug-backend-calls";
import { getSettings, getSettingsResponse } from "./getSettings";

export default async function SettingsPage() {
    /* Ensure user is logged in (should be handled by middleware but just in case) */
    const session = await getSession();
    if (!session) {
        redirect('/login');
    }

    const currentSettings: getSettingsResponse = await getSettings();

    return (
        <SettingsWidget currentSettings={currentSettings} />
        // <CallAndShow/>
        
    )
}
