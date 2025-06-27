/**
 * Demo backend that validates a login attempt.
 * 
 * It simulates a user database with hardcoded users.
 * This can be used for testing the frontend login logic without a real backend.
 * The real backend already works and this is just a fallback for development.
 */

"use server";

import { z } from "zod";
import { createSession, deleteSession } from "@/lib/session-dummy";
import { redirect } from "next/navigation";

const testUsers: Array<{
  id: string;
  username: string;
  password: string;
  permission: "user" | "admin";
}> = [
  {
    id: "1",
    username: "jona",
    password: "123456",
    permission: "user"
  },
  {
    id: "2",
    username: "olivier",
    password: "123456",
    permission: "user"
  },
  {
    id: "3",
    username: "admin",
    password: "123456",
    permission: "admin"
  },
];

export async function getUser(id: string) {
  const user = testUsers.find(user => user.id === id);
  return user ? user.username : null;
}

const loginSchema = z.object({
  username: z.string().min(1, { message: "Username is required" }).trim(),
  password: z
    .string()
    .min(4, { message: "Password must be at least 4 characters" })
    .trim(),
});

export async function loginDummy(prevState: any, formData: FormData) {
  const result = loginSchema.safeParse(Object.fromEntries(formData));

  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
    };
  }

  const { username, password } = result.data;

  const user = testUsers.find(u => u.username === username && u.password === password);

  if (!user) {
    return {
      errors: {
        password: ["Invalid username or password"],
      },
    };
  }

  await createSession(user.id, user.username, user.permission);

  redirect("/problems");
}

export async function logout() {
  await deleteSession();
  redirect("/login");
}