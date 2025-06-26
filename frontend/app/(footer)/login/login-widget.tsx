"use client"

import { useState, useActionState, useEffect } from "react"
import { useFormStatus } from "react-dom";
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import TypewriterComponent from "typewriter-effect"

import { login, register } from "./actions";
import { loginSchema, registerSchema, maxUsernameLength, maxPasswordLength } from "@/lib/form-validation/schemas"


type FormMode = 'login' | 'register'

/* Optional prop to set initial form mode. */
interface LoginWidgetProps extends React.ComponentProps<"div"> {
  initialMode?: FormMode; 
}

export function LoginWidget({
  className,
  initialMode = 'login',
  ...props
}: LoginWidgetProps) {
  const [formMode, setFormMode] = useState<FormMode>(initialMode)

  const renderHeader = () => {
    if (formMode === 'login') {
      return (
        <h1 className="mb-16 text-6xl font-bold text-center text-theme-primary-light">
          Log in
        </h1>
      )
    }
    
    return (
      <h1 className="mb-16 text-6xl font-bold text-center text-theme-secondary">
          Sign up
      </h1>
    )
  }

  return (
    /* The whole widget is centered. */
    <div className="flex flex-col items-center">
      
      {/* Header with title, changes based on form mode. */}
      {renderHeader()}

      {/* The widget itelf, containing the typewriter and form. */}
      <div className={cn("max-w-4xl flex flex-col gap-6", className)} {...props}>

        <Card className="overflow-hidden p-0">
          <CardContent className="grid p-0 md:grid-cols-2">
            <LoginWidgetLeftHalf />
            
            {/* Remove motion wrappers from form switching */}
            {formMode === 'login' ? (
              <LoginForm onSwitchToRegister={() => setFormMode('register')} />
            ) : (
              <RegisterForm onSwitchToLogin={() => setFormMode('login')} />
            )}
          </CardContent>
        </Card>

        <div className="text-muted-foreground *:[a]:hover:text-primary text-center text-xs text-balance *:[a]:underline *:[a]:underline-offset-4">
            By accessing and using the GreenCode platform, you acknowledge and agree that participation in coding competitions may result in a significant reduction in outdoor recreational activities, commonly referred to as "touching grass." User discretion is advised.
        </div>
      </div>

    </div>
  )
}

function LoginWidgetLeftHalf() {
  const typewriterText = 'Saving the world one line of code at a time...'

  return (
    <div className="bg-muted relative hidden md:block">
      
      {/* Text container with styling. */}
      <div className="m-8 relative font-mono text-left text-4xl font-bold text-theme-primary-dark">
        
        {/* Invisible print of the text to reserve space for the typewrited text. */}
        <div className="invisible">
          {typewriterText}
        </div>

        {/* Typewriter effect */}
        <div className="absolute top-0 left-0 w-full">
          <TypewriterComponent
            onInit={(typewriter) => {
            typewriter.typeString(typewriterText)
              .start();
          }}
          />
        </div>

      </div>

    </div>
  )
}

interface LoginFormProps {
  onSwitchToRegister: () => void
}

function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const [serverErrors, loginAction] = useActionState(login, undefined);

  return (
    <form action={loginAction} className="p-6 md:p-8">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col items-center text-center">
          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="text-muted-foreground text-balance">
            Log in to your GreenCode account
          </p>
        </div>

        <div className="grid gap-3">
          <Label htmlFor="login-username">Username</Label>
          <Input
            id="login-username"
            name="username"
            type="text"
            placeholder="linus"
            required
            autoComplete="username"
            maxLength={maxUsernameLength}
          />
        </div>
        {serverErrors?.errors?.username && (
          <p className="text-red-500 text-sm">{serverErrors.errors.username[0]}</p>
        )}

        <div className="grid gap-3">
          <div className="flex items-center">
            <Label htmlFor="login-password">Password</Label>
            <a
              href="#"
              className="ml-auto text-sm underline-offset-2 hover:underline"
            >
              Forgot your password?
            </a>
          </div>
          <Input
            id="login-password"
            name="password"
            type="password"
            required
            maxLength={maxPasswordLength}
          />
        </div>
        {serverErrors?.errors?.password && (
          <p className="text-red-500 text-sm">{serverErrors.errors.password[0]}</p>
        )}

        <LoginSubmitButton />

        <div className="text-center text-sm">
          Don&apos;t have an account?{" "}
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="underline underline-offset-4 hover:text-theme-secondary"
          >
            Sign up
          </button>
        </div>
      </div>
    </form>
  );
}

function LoginSubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button disabled={pending} type="submit" className="w-full">
      Login
    </Button>
  );
}

interface RegisterFormProps {
  onSwitchToLogin: () => void
}

function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const [formState, setFormState] = useState({
    username: "",
    email: "",
    password: "",
    "confirm-password": "",
  })
  const [clientErrors, setClientErrors] = useState<Record<string, string[]>>({})
  const [serverErrors, registerAction] = useActionState(register, undefined)
  const { pending } = useFormStatus()
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  // Validate on every change
  const validate = (state: typeof formState) => {
    const { "confirm-password": confirmPassword, ...zodFields } = state
    const result = registerSchema.safeParse(zodFields)
    const newErrors: Record<string, string[]> = result.success ? {} : result.error.flatten().fieldErrors as Record<string, string[]>
    // Custom confirm-password check
    if (state.password !== state["confirm-password"]) {
      newErrors["confirm-password"] = ["Passwords do not match"]
    }
    setClientErrors(newErrors)
    return newErrors
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    const newState = { ...formState, [name]: value }
    setFormState(newState)
    validate(newState)
  }

  // On submit, only allow if no client errors
  const handleSubmit = async (formData: FormData): Promise<void> => {
    const stateObj = Object.fromEntries(formData)
    const errors = validate(stateObj as typeof formState)
    if (Object.keys(errors).length > 0) {
      return
    }
    await registerAction(formData)
  }

  // Merge errors: show client errors first, then server errors if no client error for that field
  const mergedErrors = (field: string) => {
    if (!formState[field as keyof typeof formState]) return undefined;
    if (!touched[field]) return undefined;
    return (clientErrors as Record<string, string[]>)[field] || (serverErrors?.errors as Record<string, string[]> | undefined)?.[field];
  }

  useEffect(() => {
    if (serverErrors?.errors) {
      setFormState((prev) => ({ ...prev, password: "", "confirm-password": "" }))
    }
  }, [serverErrors?.errors])

  return (
    <form action={handleSubmit} className="p-6 md:p-8">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col items-center text-center">
          <h1 className="text-2xl font-bold">Create an account</h1>
          <p className="text-muted-foreground text-balance">
            Welcome to the GreenCode community!
          </p>
        </div>

        <div className="grid gap-3">
          <Label htmlFor="register-username">Username</Label>
          <Input
            id="register-username"
            name="username"
            type="text"
            placeholder="linus"
            required
            autoComplete="username"
            value={formState.username}
            onChange={handleChange}
            onBlur={() => setTouched(t => ({ ...t, username: true }))}
          />
          {mergedErrors("username") && (
            <p className="text-red-500 text-sm">{mergedErrors("username")?.[0]}</p>
          )}
        </div>

        <div className="grid gap-3">
          <Label htmlFor="register-email">Email</Label>
          <Input
            id="register-email"
            name="email"
            type="email"
            placeholder="linus.torvalds@linux.com"
            required
            value={formState.email}
            onChange={handleChange}
            onBlur={() => setTouched(t => ({ ...t, email: true }))}
          />
          {mergedErrors("email") && (
            <p className="text-red-500 text-sm">{mergedErrors("email")?.[0]}</p>
          )}
        </div>

        <div className="grid gap-3">
          <Label htmlFor="register-password">Password</Label>
          <Input
            id="register-password"
            name="password"
            type="password"
            required
            value={formState.password}
            onChange={handleChange}
            onBlur={() => setTouched(t => ({ ...t, password: true }))}
          />
          {mergedErrors("password") && (
            <p className="text-red-500 text-sm">{mergedErrors("password")?.[0]}</p>
          )}
        </div>

        <div className="grid gap-3">
          <Label htmlFor="register-password-confirm">Confirm Password</Label>
          <Input
            id="register-password-confirm"
            name="confirm-password"
            type="password"
            required
            value={formState["confirm-password"]}
            onChange={handleChange}
            onBlur={() => setTouched(t => ({ ...t, "confirm-password": true }))}
          />
          {mergedErrors("confirm-password") && (
            <p className="text-red-500 text-sm">{mergedErrors("confirm-password")?.[0]}</p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={Object.keys(clientErrors).length > 0 || pending}
        >
          {pending ? "Registering..." : "Register"}
        </Button>

        <div className="text-center text-sm">
          Already have an account?{" "}
          <button
            type="button"
            onClick={onSwitchToLogin}
            className="underline underline-offset-4 hover:text-theme-primary-light"
          >
            Log in
          </button>
        </div>
      </div>
    </form>
  )
}
