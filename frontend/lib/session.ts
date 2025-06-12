/* Creates and assigns JWT cookies to log a user in. */

import "server-only";
import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";

const secretKey = "super-secret-demo-key-for-competitive-coding";
const encodedKey = new TextEncoder().encode(secretKey);

export async function createSession(userId: string, username: string) {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // expires 7 days from now
  const session = await encrypt({ userId, username, expiresAt });

  (await cookies()).set("session", session, {
    httpOnly: true,
    secure: true,
    expires: expiresAt,
  });
}

export async function deleteSession() {
  (await cookies()).delete("session");
}

export async function getSession() {
  const sessionCookie = (await cookies()).get("session");
  if (!sessionCookie) {
    return null;
  }
  
  const session = await decrypt(sessionCookie.value);
  if (!session) {
    return null;
  }
  
  return session;
}

/* Helpers */
type SessionPayload = {
  userId: string;
  username: string;
  expiresAt: Date;
};

export async function encrypt(payload: SessionPayload) {
  return new SignJWT(payload)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(encodedKey);
}

export async function decrypt(session: string | undefined = "") {
  try {
    const { payload } = await jwtVerify(session, encodedKey, {
      algorithms: ["HS256"],
    });
    return payload;
  } catch (error) {
    console.log("Failed to verify session");
  }
}
