/* Creates and assigns JWT cookies to log a user in. */

import "server-only";
import { jwtVerify } from "jose";
import { cookies } from "next/headers";

const secretKey = process.env.JWT_SECRET;
const encodedKey = new TextEncoder().encode(secretKey);

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
