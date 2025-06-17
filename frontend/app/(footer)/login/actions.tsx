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

export async function login(prevState: any, formData: FormData) {
  /* Check input */
  const result = loginSchema.safeParse(Object.fromEntries(formData));

  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
    };
  }

  const { username, password } = result.data;

  // try {
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
    
    // return {
    //   errors: {
    //     password: [`Response: ${JSON.stringify({
    //       status: response.status,
    //       statusText: response.statusText,
    //       headers: Object.fromEntries(response.headers.entries()),
    //       url: response.url,
    //       body: await response.text()
    //     }, null, 2)}`]
    //   }
    // };

    // return {
    //   errors: {
    //     password: [(!response.ok).toString()]
    //   }
    // };
    
    // Handle failed login
    if (!response.ok) {
      // try {
        // Parse the error response
        const errorData = await response.json();
        
        /* Handle Pydantic validation errors (fallback for unformatted errors from backend) */
        // if (errorData.detail && Array.isArray(errorData.detail)) {
        //   const errors: Record<string, string[]> = {};
          
        //   // Process each validation error
        //   errorData.detail.forEach((error: any) => {
        //     if (error.loc && error.loc.length >= 2) {
        //       const field = error.loc[1]; // Get the field name from loc array
        //       // Map unknown fields to password field since that's where we show general errors
        //       const targetField = ['username', 'password'].includes(field) ? field : 'password';
        //       if (!errors[targetField]) {
        //         errors[targetField] = [];
        //       }
        //       errors[targetField].push(error.msg);
        //     }
        //   });
          
        //   return { errors };
        // }
        
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
                password: [errorData.description || "Invalid username or password"]
              }
            };
          
          case 'other':
            return {
              errors: {
                password: [typeof errorData.detail === 'string' ? `Server error: ${errorData.detail}` : `Server error: ${JSON.stringify(errorData)}`]
              }
            }; 
            
          default:
            // Return the actual error data for debugging
            return {
              errors: {
                password: [typeof errorData.detail === 'string' ? `Server error: ${errorData.detail}` : `Server error: ${JSON.stringify(errorData)}`]
              }
            };
        }
      } 
      // catch (e) {
      //   // If JSON parsing fails, return the raw error
      //   return {
      //     errors: {
      //       password: [`Failed to parse server response: ${e}`]
      //     }
      //   };
      // }

    // Get JWT as plain text
    const responseData = await response.json();
    const jwt = responseData.access_token;

    
    // Parse JWT payload using jose
    const payload = decodeJwt(jwt) as JWTPayload;
    const expiresAt = new Date(payload.exp * 1000); // Convert seconds to milliseconds
    
    return {
      errors: {
      password: [expiresAt.toLocaleString()]
      }
    };

    // Set the cookie with the JWT
    (await cookies()).set("session", jwt, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production", // Only secure in production
      sameSite: "lax",
      expires: expiresAt,
      path: "/", // Available across the whole site
    });
    
    redirect("/problems");
    
  // catch (error) {
  //     // Handle network errors (no response received)
  //     // return loginDummy(prevState, formData); // Fallback to dummy login
  //     return {
  //     errors: {
  //       "confirm-password": [`${error instanceof Error ? error.message : String(error)}`]
  //     }
  //   };
  // }
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

  try {
    // Create timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const requestBody = { username, email, password };
    
    
    /* Send to backend */
    const response = await fetch(`${BACKEND_API_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody)
    });

    // Clear timeout
    clearTimeout(timeoutId);

    // return {
    //   errors: {
    //     password: [`Response: ${JSON.stringify({
    //       status: response.status,
    //       statusText: response.statusText,
    //       headers: Object.fromEntries(response.headers.entries()),
    //       url: response.url,
    //       body: await response.text()
    //     }, null, 2)}`]
    //   }
    // };

    // Handle failed registration
    if (!response.ok) {
      try {
        // Parse the error response
        const errorData = await response.json();
        
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
        
        /* Handle other error types (errors should be formatted by backend) */
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
                "confirm-password": [typeof errorData.detail === 'string' ? `Server error: ${errorData.detail}` : `Server error: ${JSON.stringify(errorData)}`]
              }
            };
            
          default:
            // Return the actual error data for debugging
            return {
              errors: {
                "confirm-password": [`Server error: ${JSON.stringify(errorData)} | Request: ${JSON.stringify(requestBody)}`]
              }
            };
        }
      } catch (e) {
        // If JSON parsing fails, return the raw error
        return {
          errors: {
            "confirm-password": [`Failed to parse server response: ${e} | Request: ${JSON.stringify(requestBody)}`]
          }
        };
      }
    }

    // Get JWT as plain text
    const responseData = await response.json();
    const jwt = responseData.access_token;
    
    // Parse JWT payload using jose
    const { payload } = decodeJwt(jwt) as { payload: JWTPayload };
    const expiresAt = new Date(payload.exp * 1000); // Convert seconds to milliseconds
    
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
    return {
      errors: {
        "confirm-password": [`Network error: ${error instanceof Error ? error.message : String(error)}`]
      }
    };
  }
}
