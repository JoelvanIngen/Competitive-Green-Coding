/**
 * Handles user session management by providing functions to work with JWTs.
 * This module allows you to set, get, decrypt, and verify JWTs stored in cookies,
 * as well as log users out by deleting their session cookie.
 */

import "server-only";
import { jwtVerify, decodeJwt } from "jose";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const secretKey = process.env.JWT_SECRET_KEY;
const encodedKey = new TextEncoder().encode(secretKey);

const JwtCookieName = "session";
interface JWTPayload {
    uuid: string;
    username: string;
    permission_level: string;
    avatar_id: number;
    exp: number;
}

/**
 * Deletes the user's JWT session cookie.
 */
export async function deleteJWT() {
    (await cookies()).delete(JwtCookieName);
}

/**
 * Log a user out by deleting their session cookie.
 * This function should be called when the user clicks "Log out" or when
 * the session needs to be invalidated for any reason.
 */
export async function logout() {
    await deleteJWT();
    redirect("/login");
}

/**
 * Sets a JWT in the user's session cookie.
 * 
 * @param rawJWT - The raw JWT string to be stored in the cookie.
 * 
 * The function performs the following actions:
 * - Decodes the JWT payload to read the expiration timestamp
 * - Sets the cookie expiration to match the JWT's expiration time
 * - Sets an HTTP-only session cookie with the JWT token
 * - Configures cookie security settings (secure flag in production, sameSite policy)
 * 
 * @throws Will throw an error if the JWT decoding fails
 */
export async function setJWT(rawJWT: string) {
    /* Parse JWT payload using jose. */
    const payload = decodeJwt(rawJWT) as JWTPayload;
    const expiresAt = new Date(payload.exp * 1000); // Convert seconds to milliseconds

    /* Set the cookie with the JWT. */
    (await cookies()).set(JwtCookieName, rawJWT, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production", // Only secure in production
        sameSite: "lax",
        expires: expiresAt,
        path: "/", // Available across the whole site
    });
}

/**
 * Retrieves the raw encoded JWT token from the user's session cookie.
 * Use this function when you need the raw JWT string for API calls.
 * 
 * @returns {Promise<string | null>} Promise that resolves to:
 *   - The raw JWT string if a valid session cookie exists
 *   - null if no session cookie is found or if the user is not logged in
 * 
 * The returned JWT string is still encoded and requires decoding/verification
 * before accessing the payload data. If you need the decoded session data,
 * use the `getSession` function instead.
 */
export async function getJWT() {
    const sessionCookie = (await cookies()).get(JwtCookieName);
    
    if (!sessionCookie) {
        return null;
    }

    return sessionCookie.value;
}

/**
 * Returns the current user session as a decoded JWT payload object.
 * This can be used as a regular JSON object containing information
 * about the logged-in user. If the user is not logged in, the function
 * returns null.
 * 
 * For an overview of the fields available in the JWTPayload,
 * see "De Interface" OpenAPI documentation.
 * 
 * This function provides a complete authentication check by retrieving the raw JWT
 * from the session cookie, verifying its integrity and expiration, and returning
 * the decoded payload containing user information. It serves as the primary method
 * for accessing authenticated user data throughout the application.
 * 
 * @returns {Promise<JWTPayload | null>} Promise that resolves to:
 *   - A JWTPayload object containing decoded user data (username, uuid, exp, etc.) if valid
 *   - null if no session cookie exists, the JWT is invalid, expired, or verification fails
 */
export async function getSession() {
    const JWT = await getJWT();
    if (!JWT) {
        return null;
    }

    const session = await decrypt(JWT);
    if (!session) {
        return null;
    }

    return session;
}

/*
 * ██   ██ ███████ ██      ██████  ███████ ██████  ███████ 
 * ██   ██ ██      ██      ██   ██ ██      ██   ██ ██      
 * ███████ █████   ██      ██████  █████   ██████  ███████ 
 * ██   ██ ██      ██      ██      ██      ██   ██      ██ 
 * ██   ██ ███████ ███████ ██      ███████ ██   ██ ███████ 
 */

/**
 * Decrypts and verifies a raw JWT string to extract the payload.
 * 
 * @param session - The raw JWT string to decrypt and verify.
 * @returns {Promise<JWTPayload | null>} Promise that resolves to:
 *   - A JWTPayload object if the JWT is valid and successfully verified
 *   - null if the JWT is invalid, expired, or verification fails
 */
export async function decrypt(session: string | undefined = "") {
    try {
        const { payload } = await jwtVerify(session, encodedKey, {
            algorithms: ["HS256"],
        });
        return payload;
    } catch (error) {
        return null;
    }
}
