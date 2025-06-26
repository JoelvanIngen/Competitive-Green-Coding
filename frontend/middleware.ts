import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { decrypt } from "@/lib/session";

const adminRoutes = ["/admin"];
const userOnlyRoutes = ["/submission", "/settings", "/dashboard"];
const protectedRoutes = [...userOnlyRoutes, ...adminRoutes];
const publicRoutes = ["/login"];

export default async function middleware(req: NextRequest) {
    const path = req.nextUrl.pathname;
    const isProtectedRoute = protectedRoutes.includes(path);
    const isAdminRoute = adminRoutes.includes(path);
    const isPublicRoute = publicRoutes.includes(path);

    const cookie = (await cookies()).get("session")?.value;
    const session = cookie ? await decrypt(cookie) : null;

    /* Step 1: Redirect non-logged in user. */
    if (isProtectedRoute && !session) {
        return NextResponse.redirect(new URL("/login", req.nextUrl));
    }

    /* Step 2: Redirect non-admin user */
    if (isAdminRoute && session && session.permission_level !== "admin") {
        return NextResponse.redirect(new URL("/problems", req.nextUrl));
    }

    /* Step 3: Redirect logged in user from public routes (login page) */
    if (isPublicRoute && session) {
        return NextResponse.redirect(new URL("/problems", req.nextUrl));
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ],
}
