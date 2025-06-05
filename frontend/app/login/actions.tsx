/* Demo backend that validates a login attempt. */

"use server";

import { z } from "zod";
import { createSession, deleteSession } from "@/lib/session";
import { redirect } from "next/navigation";

const testUser = {
  id: "1",
  username: "jona",
  password: "1234",
};

const loginSchema = z.object({
  username: z.string().min(1, { message: "Username is required" }).trim(),
  password: z
    .string()
    .min(4, { message: "Password must be at least 4 characters" })
    .trim(),
});

export async function login(prevState: any, formData: FormData) {
  const result = loginSchema.safeParse(Object.fromEntries(formData));

  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
    };
  }

  const { username, password } = result.data;

  if (username !== testUser.username || password !== testUser.password) {
    return {
      errors: {
        password: ["Invalid username or password"],
      },
    };
  }

  await createSession(testUser.id);

  redirect("/dashboard");
}

export async function logout() {
  await deleteSession();
  redirect("/login");
}