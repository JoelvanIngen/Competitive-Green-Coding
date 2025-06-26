import { z } from "zod";

/* Constraints for login and register forms */
const minUsernameLength = 2;
export const maxUsernameLength = 32;

const maxEmailLength = 64;

const minPasswordLength = 8;
export const maxPasswordLength = 128;

/* Zod schemas for login and register forms */
export const loginSchema = z.object({
  username: z.string().min(1, { message: "Username is required" }).trim(),
  password: z.string().min(1, { message: "Password is required" }).trim(),
});

export const registerSchema = z.object({
  username: z.string()
    .min(minUsernameLength, { message: `Username must be at least ${minUsernameLength} characters long` })
    .max(maxUsernameLength, { message: `Username must be at most ${maxUsernameLength} characters long` })
    .regex(/^[a-zA-Z0-9]+$/, { message: "Special characters are not allowed" })
    .trim(),
  email: z.string()
    .email({ message: "Invalid email format" })
    .regex(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b/, { message: "Invalid email format" })
    .max(maxEmailLength, { message: `Email can not be longer than ${maxEmailLength} characters` })
    .trim(),
  password: z
    .string()
    .min(minPasswordLength, { message: `Password must be at least ${minPasswordLength} characters long` })
    .max(maxPasswordLength, { message: `Password can not be longer than ${maxPasswordLength} characters` })
    .trim(),
}); 