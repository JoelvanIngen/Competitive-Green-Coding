/* Simplified session handling */

import "server-only";
import { cookies } from "next/headers";

// Simple session type
export type Session = {
  userId?: string;
  username?: string;
  expiresAt?: Date;
};

// Mock session for development
const mockSession: Session = {
  userId: "dev-user",
  username: "developer",
  expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
};

export async function getSession(): Promise<Session | null> {
  try {
    const sessionCookie = (await cookies()).get("session");
    if (!sessionCookie) {
      return mockSession; // Return mock session in development
    }
    return mockSession; // For now, always return mock session
  } catch (error) {
    console.log("Session error:", error);
    return mockSession; // Return mock session on error
  }
}

export async function logout() {
  try {
    (await cookies()).delete("session");
  } catch (error) {
    console.log("Logout error:", error);
  }
}

// Export mock session for testing
export const getMockSession = () => mockSession;
