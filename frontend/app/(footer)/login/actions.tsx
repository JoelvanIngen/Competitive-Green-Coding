/**
 * Server actions for login and register form submission.
 */

"use server";

import { z } from "zod";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { loginDummy } from "./actions-dummy"; // Fallback to dummy login if backend is not available

const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000/api";

const loginSchema = z.object({
  username: z.string().min(1, { message: "Username is required" }).trim(),
  password: z
    .string()
    .min(1, { message: "Password is required" })
    .trim(),
});

export async function login(prevState: any, formData: FormData) {
  /* Check input */
  const result = loginSchema.safeParse(Object.fromEntries(formData));

  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
    };
  }

  const { username, password } = result.data;

  try {
    // Create timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
  /* Send to backend */
  const response = await fetch(`${BACKEND_API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password })
  });

  // Clear timeout
    clearTimeout(timeoutId);

  // Handle failed login
  if (!response.ok) {
    try {
      // Parse the error response
      const errorData = await response.json();
      
      // Handle different error types
      switch (errorData.type) {
        case 'username':
          return {
            errors: {
              username: [errorData.description]
            }
          };
          
        case 'password':
          return {
            errors: {
              password: [errorData.description]
            }
          };
          
        case 'invalid':
          return {
            errors: {
              password: [errorData.description || "Invalid username or password"]
            }
          };
        
        // TODO: handle other error with toast 
        case 'other':
          return {
            errors: {
              password: [errorData.description || "A server error occurred"]
            }
          }; 

        // case 'other':
        //   // Return a toast message for client-side handling
        //   return {
        //     toast: {
        //       type: "error",
        //       message: errorData.description || "A server error occurred"
        //     }
        //   };
          
        default:
          // Fallback for unknown error types
          return {
            errors: {
              password: [errorData.description || "An error occurred"]
            }
          };
      }
    } catch (e) {
      // If JSON parsing fails, return a generic error
      return {
        errors: {
          password: ["Login failed. Please try again."]
        }
      };
    }
  }

  // Get JWT as plain text
  const jwt = await response.text();
  
  // Calculate JWT expiry by parsing it
  const jwtPayload = JSON.parse(atob(jwt.split('.')[1]));
  const expiresAt = new Date(jwtPayload.exp * 1000); // Convert seconds to milliseconds
  
  // Set the cookie with the JWT
  (await cookies()).set("session", jwt, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production", // Only secure in production
    sameSite: "lax",
    expires: expiresAt,
    path: "/", // Available across the whole site
  });
  
  redirect("/problems");
  
 } catch (error) {
    // Handle network errors (no response received)
    console.error("Login network error:", error);
    
    return loginDummy(prevState, formData); // Fallback to dummy login
  }
}

export async function logout() {
  (await cookies()).delete("session")
  redirect("/login");
}
