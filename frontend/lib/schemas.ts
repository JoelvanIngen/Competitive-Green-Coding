import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(1, { message: "Username is required" }).trim(),
  password: z.string().min(1, { message: "Password is required" }).trim(),
});

export const registerSchema = z.object({
  username: z.string()
    .min(2, { message: "Username must be at least 2 characters long" })
    .max(32, { message: "Username must be at most 32 characters long" })
    .regex(/^[a-zA-Z0-9]+$/, { message: "Special characters are not allowed" })
    .trim(),
  email: z.string()
    .email({ message: "Invalid email format" })
    .regex(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b/, { message: "Invalid email format" })
    .max(64, { message: "Email can not be longer than 64 characters" })
    .trim(),
  password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters long" })
    .max(128, { message: "Password can not be longer than 128 characters" })
    .trim(),
}); 