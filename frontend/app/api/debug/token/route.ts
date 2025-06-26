import { getJWT } from "@/lib/session";
import { NextResponse } from "next/server";

export async function GET() {
  const token = await getJWT();
  return NextResponse.json({ token });
}
