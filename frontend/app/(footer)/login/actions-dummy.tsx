/* Demo backend that validates a login attempt. */

"use server";

import { z } from "zod";
import { createSession, deleteSession } from "@/lib/session-dummy";
import { redirect } from "next/navigation";

const testUsers = [
  {
    id: "1",
    username: "jona",
    password: "123456",
  },
  {
    id: "2",
    username: "olivier",
    password: "123456",
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

  await createSession(user.id, user.username);

  redirect("/problems");
}

export async function logout() {
  await deleteSession();
  redirect("/login");
}