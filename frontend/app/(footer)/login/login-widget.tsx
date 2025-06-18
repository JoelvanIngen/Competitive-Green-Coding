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
  const [state, loginAction] = useActionState(login, undefined);
  
  return (
    <form action={loginAction}  className="p-6 md:p-8">
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
          />
        </div>

        {state?.errors?.username && (
          <p className="text-red-500 text-sm">{state.errors.username}</p>
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
          />
        </div>

        {state?.errors?.password && (
          <p className="text-red-500 text-sm">{state.errors.password}</p>
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
  )
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
  const [usernameValid, setUsernameValid] = useState(true)
  const [emailValid, setEmailValid] = useState(true)
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordsMatch, setPasswordsMatch] = useState(true)
  const [passwordLengthValid, setPasswordLengthValid] = useState(true)
  const { pending } = useFormStatus()
  const [state, registerAction] = useActionState(register, undefined)

  // Reset form state when there are errors
  useEffect(() => {
    if (state?.errors) {
      setPassword('')
      setConfirmPassword('')
    }
  }, [state?.errors])

  // Calculate if the form is valid
  const showPasswordError = !passwordsMatch && password !== '' && confirmPassword !== ''
  const isFormValid = usernameValid && emailValid && password !== '' && confirmPassword !== '' && passwordsMatch && passwordLengthValid

  const handleSubmit = async (formData: FormData) => {
    return registerAction(formData)
  }

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
            onChange={(e) => setUsernameValid(e.target.value !== '' && e.target.validity.valid)}
          />
          {state?.errors?.username && (
            <p className="text-red-500 text-sm">{state.errors.username}</p>
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
            onChange={(e) => setEmailValid(e.target.validity.valid || e.target.value === '')}
          />
          {state?.errors?.email && (
            <p className="text-red-500 text-sm">{state.errors.email}</p>
          )}
        </div>

        <div className="grid gap-3">
          <Label htmlFor="register-password">Password</Label>
          <Input 
            id="register-password" 
            name="password"
            type="password" 
            required 
            value={password}
            onChange={(e) => {
              const value = e.target.value
              setPassword(value)
              setPasswordLengthValid(value.length >= 8)
              setPasswordsMatch(value === confirmPassword)
            }}
          />
          {!passwordLengthValid && password !== '' && (
            <p className="mt-2 text-sm text-red-600">Password must be at least 8 characters long</p>
          )}
          {state?.errors?.password && (
            <p className="text-red-500 text-sm">{state.errors.password}</p>
          )}
        </div>

        <div className="grid gap-3">
          <Label htmlFor="register-password-confirm">Confirm Password</Label>
          <Input 
            id="register-password-confirm" 
            name="confirm-password"
            type="password" 
            required
            value={confirmPassword}
            onChange={(e) => {
              const newConfirmPassword = e.target.value
              setConfirmPassword(newConfirmPassword)
              // Update match status when confirm password changes
              setPasswordsMatch(newConfirmPassword === '' || password === newConfirmPassword)
            }}
          />
          {(state?.errors as any)?.["confirm-password"] && (
            <p className="text-red-500 text-sm">{(state?.errors as any)["confirm-password"]}</p>
          )}
        </div>

        {showPasswordError && (
          <p className="text-red-500 text-sm">Passwords don't match</p>
        )}

        <Button 
          type="submit" 
          className="w-full"
          disabled={!isFormValid || pending}
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
