/**
 * Reusable validation hook for forms.
 * 
 * Used by the login and settings page.
 */

"use client"

import { useState } from "react";

/* Reusable validation hook for forms */
export function useFormValidation<T extends Record<string, any>>(
  schema: any,
  initialState: T
) {
  const [formState, setFormState] = useState<T>(initialState)
  const [clientErrors, setClientErrors] = useState<Record<string, string[]>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  // Validate on every change
  const validate = (state: T) => {
    const result = schema.safeParse(state)
    const newErrors: Record<string, string[]> = result.success ? {} : result.error.flatten().fieldErrors as Record<string, string[]>
    setClientErrors(newErrors)
    return newErrors
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    const newState = { ...formState, [name]: value }
    setFormState(newState)
    validate(newState)
  }

  const handleBlur = (fieldName: string) => {
    setTouched(t => ({ ...t, [fieldName]: true }))
  }

  // Merge errors: show client errors first, then server errors if no client error for that field
  const mergedErrors = (field: string, serverErrors?: Record<string, string[]>) => {
    if (!formState[field as keyof T]) return undefined;
    if (!touched[field]) return undefined;
    return clientErrors[field] || serverErrors?.[field];
  }

  const resetForm = () => {
    setFormState(initialState)
    setClientErrors({})
    setTouched({})
  }

  return {
    formState,
    setFormState,
    clientErrors,
    touched,
    handleChange,
    handleBlur,
    mergedErrors,
    validate,
    resetForm
  }
} 