import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  (await cookies()).delete("session");
  
  // Get base URL from request
  const url = new URL('/login', request.url);
  return NextResponse.redirect(url);
}