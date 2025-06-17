/**
 * Server actions for login and register form submission.
 */

"use server";

import { z } from "zod";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { loginDummy } from "./actions-dummy"; // Fallback to dummy login if backend is not available
import { decodeJwt } from "jose";

interface JWTPayload {
  exp: number;
  uuid: string;
  username: string;
  permission: string;
}

const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000/api";

const loginSchema = z.object({
  username: z.string().min(1, { message: "Username is required" }).trim(),
  password: z
    .string()
    .min(1, { message: "Password is required" })
    .trim(),
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
 * Helper function to process JWT response and set session cookie
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

export async function login(prevState: any, formData: FormData) {
  // return loginDummy(prevState, formData); // Fallback to dummy login

  /* Check input */
  const result = loginSchema.safeParse(Object.fromEntries(formData));
  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
    };
  }

  const { username, password } = result.data;
  
  /* Send to backend */
  const response = await fetch(`${BACKEND_API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password })
  });

    // Handle failed login
    if (!response.ok) {
        // Read response text
        const responseText = await response.text();
        
        // Try to parse as JSON
        let errorData: { type?: string; description?: string, detail?: any };
        try {
          errorData = JSON.parse(responseText);
        } catch {
          // If JSON parsing fails, return the raw body
          return {
            errors: {
              "password": [responseText]
            }
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
                const targetField = ['username', 'email', 'password'].includes(field) ? field : 'password';
                if (!errors[targetField]) {
                    errors[targetField] = [];
                }
                errors[targetField].push(error.msg);
            }
          });
          
          return { errors };
        }

        /* If the format is not as expected and not handled by Pydantic, return the raw body */
        if (!errorData.type || !errorData.description) {
          return {
            errors: {
              "password": [responseText]
            }
          };
        }
        
        /* Handle other error types (errors should be formatted by backend) */
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
                password: [errorData.description]
              }
            };
          
          case 'other':
            return {
              errors: {
                password: [errorData.description]
              }
            }; 
            
          default:
            // Return the actual error data for debugging
            return {
              errors: {
                password: [errorData.description]
              }
            };
        }
      }

    await processJWTResponse(response);
    redirect("/");
}

export async function logout() {
  (await cookies()).delete("session")
  redirect("/login");
}

export async function register(prevState: any, formData: FormData) {
  /* Check input */
  const result = registerSchema.safeParse(Object.fromEntries(formData));

  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
    };
  }

  const { username, email, password } = result.data;
  
  /* Send to backend */
  const response = await fetch(`${BACKEND_API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, email, password })
  });

  // const responseText = await response.text();
  // return {
  //   errors: {
  //     "confirm-password": [responseText]
  //   }
  // };

  // Handle failed registration
  if (!response.ok) {
    // Read response text
    const responseText = await response.text();
    
    // Try to parse as JSON
    let errorData: { type?: string; description?: string, detail?: any };
    try {
      errorData = JSON.parse(responseText);
    } catch {
      // If JSON parsing fails, return the raw body
      return {
        errors: {
          "confirm-password": [responseText]
        }
      };
    }

    /* Handle Pydantic validation errors (fallback for unformatted errors from backend) */
    if (errorData.detail && Array.isArray(errorData.detail)) {
      const errors: Record<string, string[]> = {};
      
      // Process each validation error
      errorData.detail.forEach((error: any) => {
        if (error.loc && error.loc.length >= 2) {
          const field = error.loc[1]; // Get the field name from loc array
          // Map unknown fields to confirm-password
          const targetField = ['username', 'email', 'password'].includes(field) ? field : 'confirm-password';
          if (!errors[targetField]) {
            errors[targetField] = [];
          }
          errors[targetField].push(error.msg);
        }
      });
      
      return { errors };
    }

     /* If the format is not as expected and not handled by Pydantic, return the raw body */
    if (!errorData.type || !errorData.description) {
      return {
        errors: {
          "confirm-password": [responseText]
        }
      };
    }
    
    /* Handle expected error types (errors should be formatted by backend) */
    switch (errorData.type) {
      case 'username':
        return {
          errors: {
            username: [errorData.description]
          }
        };
        
      case 'email':
        return {
          errors: {
            email: [errorData.description]
          }
        };
        
      case 'password':
        return {
          errors: {
            password: [errorData.description]
          }
        };
      
      case 'other':
        return {
          errors: {
            "confirm-password": [errorData.description]
          }
        };
        
      default:
        // Return the actual error data for debugging
        return {
          errors: {
            "confirm-password": [errorData.description]
          }
        };
    }
  }

  await processJWTResponse(response);
  redirect("/");
}
