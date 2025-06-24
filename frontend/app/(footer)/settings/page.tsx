"use server"

import { getJWT, getSession, decrypt } from "@/lib/session";
import { redirect } from 'next/navigation';

import SettingsWidget from "./settings-widget"
import { decodeJwt } from 'jose';

export default async function SettingsPage() {
    const session = await getSession();

    if (!session) {
        // This should never happen because of middleware,
        // but satisfies TypeScript
        redirect('/login');
    }

    const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${await getJWT()}`
        }

    const body = JSON.stringify({
        "user_uuid": session.uuid,
        "key": "private",
        "value": "0",
    })

    const BACKEND_URL = process.env.BACKEND_API_URL
    const response = await fetch(`${BACKEND_URL}/settings`, {
        method: 'POST',
        headers: headers,
        body: body
    });

    const responseText = await response.text();

    let response_decrypted;
    try {
        response_decrypted = decodeJwt(responseText);
    } catch (error) {
        response_decrypted = null;
    }

    return (
        <div className="my-8 flex flex-col gap-4">
            <div>
                <h1 className="text-2xl font-bold text-center mb-4">JWT</h1>
                <p className="text-center">{JSON.stringify(session)}</p>
            </div>
            <div>
                <h1 className="text-2xl font-bold text-center mb-4">Request</h1>

                <h2 className="text-xl font-bold text-center mb-4">Header</h2>
                <p className="text-center">{JSON.stringify(headers)}</p>

                <h2 className="text-xl font-bold text-center mb-4">Body</h2>
                <p className="text-center">{body}</p>

            </div>
            <div>
                <h1 className="text-2xl font-bold text-center mb-4">Response</h1>
                <p className="text-center">{responseText}</p>
                
                {response_decrypted && (
                    <>
                        <h2 className="text-xl font-bold text-center mb-4">Response decrypted</h2>
                        <p className="text-center">{JSON.stringify(response_decrypted)}</p>
                    </>
                )}
            </div>
            {/* <SettingsWidget session={session} /> */}
        </div>
    )
}
