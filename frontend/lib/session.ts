/* Creates and assigns JWT cookies to log a user in. */

import "server-only";
import { jwtVerify } from "jose";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const secretKey = process.env.JWT_SECRET_KEY || "super-secret-demo-key-for-competitive-coding";
const encodedKey = new TextEncoder().encode(secretKey);

export async function logout() {
  (await cookies()).delete("session")
  redirect("/login");
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
