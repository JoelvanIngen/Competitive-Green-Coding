"use server"

import { redirect } from 'next/navigation';
import { decodeJwt } from 'jose';

import { getJWT, getSession } from "@/lib/session";

export default async function CallAndShow() {
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

    const request_method: 'GET' | 'PUT' | 'POST' = 'GET'; // 'POST' for sending data
    
    const BACKEND_URL = process.env.BACKEND_API_URL
    const request_url = `${BACKEND_URL}/settings`;

    let body = null;
    if (request_method === 'POST' || request_method === 'PUT') {
    body = JSON.stringify({
        "user_uuid": session.uuid,
        "key": "private",
        "value": "0",
    })
    }
    const response = await fetch(request_url, {
        method: request_method, // 'POST'
        headers: headers,
        ...(request_method !== 'GET' && { body: body })
        // body: ""
    });

    const responseText = await response.text();

    let response_decrypted;
    try {
        response_decrypted = decodeJwt(responseText);
    } catch (error) {
        response_decrypted = null;
    }

    return (
        <div className="my-8 flex flex-col gap-4 container mx-auto break-all">
            <div>
                <h1 className="text-2xl font-bold text-center mb-4">JWT</h1>
                <p className="text-center">{JSON.stringify(session)}</p>
            </div>
            <div>
                <h1 className="text-2xl font-bold text-center mb-4">Request</h1>

                <h2 className="text-xl font-bold text-center mb-4">URL</h2>
                <p className="text-center">{request_url}</p>

                <h2 className="text-xl font-bold text-center mb-4">Header</h2>
                <p className="text-center ">{JSON.stringify(headers, null, 2)}</p>

                {body && (
                    <>
                        <h2 className="text-xl font-bold text-center mb-4">Body</h2>
                        <p className="text-center">{body}</p>
                    </>
                )}

            </div>
            <div>
                <h1 className="text-2xl font-bold text-center mb-4">Response</h1>
                
                <h2 className="text-xl font-bold text-center mb-4">Status</h2>
                <p className="text-center">Status: {response.status} {response.statusText}</p>
                
                <h2 className="text-xl font-bold text-center mb-4">Headers</h2>
                <p className="text-center">{JSON.stringify(Object.fromEntries(response.headers.entries()), null, 2)}</p>
                
                <h2 className="text-xl font-bold text-center mb-4">Body</h2>
                <p className="text-center">{responseText}</p>
                
                {response_decrypted && (
                    <>
                        <h2 className="text-xl font-bold text-center mb-4">Response decrypted</h2>
                        <p className="text-center">{JSON.stringify(response_decrypted, null, 2)}</p>
                    </>
                )}
            </div>
        </div>
    )
}
