/**
 * Server actions for login and register form submission.
 */

"use server";

import { z } from "zod";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { decodeJwt } from "jose";
// import { loginDummy } from "./actions-dummy"; // Fallback to dummy login if backend is not available

interface JWTPayload {
    exp: number;
    uuid: string;
    username: string;
    permission: string;
}

const BACKEND_API_URL =
    process.env.BACKEND_API_URL;

/* Contraints for login an register forms can be added here. These are checked before sending the data to the backend. */
const loginSchema = z.object({
    username: z.string().min(1, { message: "Username is required" }).trim(),
    password: z.string().min(1, { message: "Password is required" }).trim(),
});

const registerSchema = z.object({
    username: z.string().min(1, { message: "Username is required" }).trim(),
    email: z.string().email({ message: "Invalid email format" }).trim(),
    password: z
        .string()
        .min(8, { message: "Password must be at least 8 characters long" })
        .trim(),
});

/**
 * Processes a successful authentication response containing a JWT token and establishes a user session.
 * 
 * This helper function extracts the JWT access token from the backend response, decodes its payload
 * to retrieve expiration information, and sets a secure HTTP-only session cookie. The cookie is
 * configured with appropriate security settings based on the current environment.
 * 
 * @param response - The successful HTTP Response object from the backend authentication endpoint
 *                   Expected to contain a JSON body with an `access_token` field
 * 
 * @returns Promise<void> - Resolves when the session cookie has been successfully set
 * 
 * The function automatically:
 * - Extracts the JWT from the response JSON under the `access_token` key
 * - Decodes the JWT payload to read the expiration timestamp
 * - Sets an HTTP-only session cookie with the JWT token
 * - Configures cookie security settings (secure flag in production, sameSite policy)
 * - Sets the cookie expiration to match the JWT's expiration time
 * 
 * @throws Will throw an error if the response doesn't contain valid JSON or if JWT decoding fails
 */
async function processJWTResponse(response: Response) {
    // Get JWT as plain text
    const responseData = await response.json();
    const jwt = responseData.access_token;

    // Parse JWT payload using jose
    const payload = decodeJwt(jwt) as JWTPayload;
    const expiresAt = new Date(payload.exp * 1000); // Convert seconds to milliseconds

    // Set the cookie with the JWT
    (await cookies()).set("session", jwt, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production", // Only secure in production
        sameSite: "lax",
        expires: expiresAt,
        path: "/", // Available across the whole site
    });
}

/**
 * Handles user login form submission.
 * 
 * This function validates the login form data, sends a login request to the backend API,
 * processes the JWT response to establish a user session, and handles various error scenarios
 * that may occur during authentication.
 * 
 * @param prevState - The previous state from the form action (unused in current implementation)
 * @param formData - FormData object containing the login form fields (username, password)
 * 
 * @returns Promise that resolves to either:
 *   - An object with `errors` property containing field-specific validation errors if login fails
 *   - Redirects to "/" if login is successful and session is established
 * 
 * On successful authentication, this function automatically sets a secure HTTP-only session cookie
 * containing the JWT token. All backend errors are mapped to appropriate form fields, with unknown 
 * errors defaulting to the "password" field for display purposes.
 */
export async function login(prevState: any, formData: FormData) {
    // return loginDummy(prevState, formData); // Fallback to dummy login

    /* Check input */
    const result = loginSchema.safeParse(Object.fromEntries(formData));
    if (!result.success) {
        return {
            errors: result.error.flatten().fieldErrors,
        };
    }

    /* Send to backend */
    const { username, password } = result.data;
    const response = await fetch(`${BACKEND_API_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
    });

    /* Handle error response */
    if (!response.ok) {
        /* Read response text */
        const responseText = await response.text();

        /* Try to parse as JSON */
        /* If JSON parsing fails, return the raw body */
        let errorData: { type?: string; description?: string; detail?: any };
        try {
            errorData = JSON.parse(responseText);
        } catch {
            return {
                errors: {
                    password: [responseText],
                },
            };
        }

        /* Handle Pydantic validation errors (fallback for unformatted errors from backend) */
        if (errorData.detail && Array.isArray(errorData.detail)) {
            const errors: Record<string, string[]> = {};

            // Process each validation error
            errorData.detail.forEach((error: any) => {
                if (error.loc && error.loc.length >= 2) {
                    const field = error.loc[1]; // Get the field name from loc array
                    // Map unknown fields to password
                    const targetField = ["username", "email", "password"].includes(field)
                        ? field
                        : "password";
                    if (!errors[targetField]) {
                        errors[targetField] = [];
                    }
                    errors[targetField].push(error.msg);
                }
            });

            return { errors };
        }

        /* Handle nested detail object (if backend decides to wrap the actual response in a "detail" key (why!?)) */
        if (errorData.detail && typeof errorData.detail === 'object' && !Array.isArray(errorData.detail)) {
            errorData = errorData.detail;
        }

        /* If the format is not as expected and fallbacks didn't work, just return the raw body. */
        if (!errorData.type || !errorData.description) {
            return {
                errors: {
                    password: [responseText],
                },
            };
        }

        /* Handle expected error reponse. */
        switch (errorData.type) {
            case "username":
                return {
                    errors: {
                        username: [errorData.description],
                    },
                };

            case "password":
                return {
                    errors: {
                        password: [errorData.description],
                    },
                };

            case "invalid":
                return {
                    errors: {
                        password: [errorData.description],
                    },
                };

            case "other":
                return {
                    errors: {
                        password: [errorData.description],
                    },
                };

            default:
                return {
                    errors: {
                        password: [errorData.description],
                    },
                };
        }
    }

    /* Handle ok response and redirect */
    await processJWTResponse(response);
    redirect("/");
}

export async function logout() {
    (await cookies()).delete("session");
    redirect("/login");
}

/**
 * Handles user registration form submission.
 * 
 * This function validates the registration form data, sends a registration request to the backend API,
 * processes the response, and handles various error scenarios that may occur during registration.
 * 
 * @param prevState - The previous state from the form action (unused in current implementation)
 * @param formData - FormData object containing the registration form fields (username, email, password, confirm-password)
 * 
 * @returns Promise that resolves to either:
 *   - An object with `errors` property containing field-specific validation errors if registration fails
 *   - Redirects to "/" if registration is successful
 * 
 * All backend errors are mapped to appropriate form fields, with unknown errors
 * defaulting to the "confirm-password" field for display purposes.
 */
export async function register(prevState: any, formData: FormData) {
    /* Check input */
    const result = registerSchema.safeParse(Object.fromEntries(formData));
    if (!result.success) {
        return {
            errors: result.error.flatten().fieldErrors,
        };
    }

    /* Send to backend */
    const { username, email, password } = result.data;
    const response = await fetch(`${BACKEND_API_URL}/auth/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password }),
    });

    /* Handle error response */
    if (!response.ok) {
        /* Read response text */
        const responseText = await response.text();

        /* Try to parse as JSON */
        /* If JSON parsing fails, return the raw body */
        let errorData: { type?: string; description?: string; detail?: any };
        try {
            errorData = JSON.parse(responseText);
        } catch {
            return {
                errors: {
                    "confirm-password": [responseText],
                },
            };
        }

        /* Handle Pydantic validation errors (fallback for unformatted errors from backend). */
        if (errorData.detail && Array.isArray(errorData.detail)) {
            const errors: Record<string, string[]> = {};

            // Process each validation error
            errorData.detail.forEach((error: any) => {
                if (error.loc && error.loc.length >= 2) {
                    const field = error.loc[1]; // Get the field name from loc array
                    // Map unknown fields to confirm-password
                    const targetField = ["username", "email", "password"].includes(field)
                        ? field
                        : "confirm-password";
                    if (!errors[targetField]) {
                        errors[targetField] = [];
                    }
                    errors[targetField].push(error.msg);
                }
            });

            return { errors };
        }

        /* Handle nested detail object (if backend decides to wrap the actual response in a "detail" key (why!?)) */
        if (errorData.detail && typeof errorData.detail === 'object' && !Array.isArray(errorData.detail)) {
            errorData = errorData.detail;
        }

        /* If the format is not as expected and fallbacks didn't work, just return the raw body. */
        if (!errorData.type || !errorData.description) {
            return {
                errors: {
                    "confirm-password": [responseText],
                },
            };
        }

        /* Handle expected error response. */
        switch (errorData.type) {
            case "username":
                return {
                    errors: {
                        username: [errorData.description],
                    },
                };

            case "email":
                return {
                    errors: {
                        email: [errorData.description],
                    },
                };

            case "password":
                return {
                    errors: {
                        password: [errorData.description],
                    },
                };

            case "other":
                return {
                    errors: {
                        "confirm-password": [errorData.description],
                    },
                };

            default:
                return {
                    errors: {
                        "confirm-password": [errorData.description],
                    },
                };
        }
    }

    /* Handle ok response and redirect */
    await processJWTResponse(response);
    redirect("/");
}
