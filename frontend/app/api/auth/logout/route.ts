/**
 * Logout route. Used by logout option in the toolbar.
 * Deletes the session cookie and redirects to the login page.
 */

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  (await cookies()).delete("session");
  
  // Get base URL from request
  const url = new URL('/login', request.url);
  return NextResponse.redirect(url);
}