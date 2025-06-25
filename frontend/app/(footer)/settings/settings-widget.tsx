"use client"

import Image from "next/image";
import { toast } from "sonner";
import { z } from "zod"

import { useState, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"

import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Switch } from "@/components/ui/switch"

import type { JWTPayload } from "@/lib/session";
import avatarVariantsData from '@/public/images/avatars/avatar_id.json'
import { set } from "date-fns";

// Zod schema for password update form
const passwordSchema = z.object({
    currentPassword: z.string().min(1, { message: "Current password is required" }),
    newPassword: z.string().min(8, { message: "Password must be at least 8 characters long" }),
    confirmPassword: z.string().min(1, { message: "Please confirm your password" })
}).refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"]
});

const usernameSchema = z.object({
    newUsername: z.string().min(1, { message: "Username is required" }).trim(),
    password: z.string().min(1, { message: "Password is required" })
});

export default function SettingsWidget({ session }: { session: JWTPayload }) {
    // User data
    const [username, setUsername] = useState(session.username)
    const [email, setEmail] = useState("user@example.com")
    const [hideAccount, sethideAccount] = useState(false)

    // Form states for dialogs
    const [newUsername, setNewUsername] = useState("")
    const [confirmPasswordForNewUsername, setConfirmPasswordForNewUsername] = useState("")

    const [newEmail, setNewEmail] = useState("")

    const [currentPassword, setCurrentPassword] = useState("")
    const [newPassword, setNewPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")

    // Loading states
    const [usernameLoading, setUsernameLoading] = useState(false)
    const [emailLoading, setEmailLoading] = useState(false)
    const [passwordLoading, setPasswordLoading] = useState(false)

    // Dialog open states
    const [usernameDialogOpen, setUsernameDialogOpen] = useState(false)
    const [emailDialogOpen, setEmailDialogOpen] = useState(false)
    const [passwordDialogOpen, setPasswordDialogOpen] = useState(false)

    // Hide my account dialog
    const [privacyDialogOpen, setPrivacyDialogOpen] = useState(false)
    const [pendingPrivacyValue, setPendingPrivacyValue] = useState<boolean | null>(null)

    // Zod validation errors state
    const [passwordErrors, setPasswordErrors] = useState<{
        currentPassword?: string[];
        newPassword?: string[];
        confirmPassword?: string[];
    }>({});

    const [usernameErrors, setUsernameErrors] = useState<{
        newUsername?: string[];
        password?: string[];
    }>({});

    // Live validation for password fields
    // Modify validation to match register form behavior
    // Update the validatePassword function to accept optional values
const validatePassword = (currentPwd?: string, newPwd?: string, confirmPwd?: string) => {
    // Use passed values or fall back to state
    const currentPassword_val = currentPwd ?? currentPassword;
    const newPassword_val = newPwd ?? newPassword;
    const confirmPassword_val = confirmPwd ?? confirmPassword;

    // Only validate if fields have values (like register form)
    if (!newPassword_val && !confirmPassword_val && !currentPassword_val) {
        setPasswordErrors({});
        return true;
    }

    const result = passwordSchema.safeParse({
        currentPassword: currentPassword_val,
        newPassword: newPassword_val,
        confirmPassword: confirmPassword_val
    });

    if (!result.success) {
        const errors = result.error.flatten().fieldErrors;

        // Filter out errors for empty fields (register form behavior)
        const filteredErrors: typeof passwordErrors = {};

        if (newPassword_val && errors.newPassword) {
            filteredErrors.newPassword = errors.newPassword;
        }

        if (confirmPassword_val && errors.confirmPassword) {
            filteredErrors.confirmPassword = errors.confirmPassword;
        }

        if (currentPassword_val && errors.currentPassword) {
            filteredErrors.currentPassword = errors.currentPassword;
        }

        setPasswordErrors(filteredErrors);
        return Object.keys(filteredErrors).length === 0;
    } else {
        setPasswordErrors({});
        return true;
    }
};

    // Live validation for username fields
    const validateUsername = () => {
        const result = usernameSchema.safeParse({
            newUsername,
            password: confirmPasswordForNewUsername
        });

        if (!result.success) {
            setUsernameErrors(result.error.flatten().fieldErrors);
            return false;
        } else {
            setUsernameErrors({});
            return true;
        }
    };

const handleNewPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setNewPassword(newValue);
    // Pass the new value directly to validation
    validatePassword(currentPassword, newValue, confirmPassword);
};

const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setConfirmPassword(newValue);
    // Pass the new value directly to validation
    validatePassword(currentPassword, newPassword, newValue);
};

const handleCurrentPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setCurrentPassword(newValue);
    // Pass the new value directly to validation
    validatePassword(newValue, newPassword, confirmPassword);
};

    const handlePasswordDialogClose = () => {
        setPasswordDialogOpen(false);

        // Reset form fields
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");

        // Reset errors
        setPasswordErrors({});
    };

    const handleNewUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setNewUsername(e.target.value);
        validateUsername();
    };

    const handleConfirmPasswordForUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setConfirmPasswordForNewUsername(e.target.value);
        validateUsername();
    };

    /* Avatar setup */

    // Avatar variants
    const avatarVariants: string[] = avatarVariantsData; // Imported from JSON file
    const avatarIndex = session.avatar_id as number; // Get the avatar index from the session
    const currentAvatarName: string = avatarVariants[avatarIndex]

    // Avatar states
    const [currentAvatar, setCurrentAvatar] = useState(currentAvatarName)
    const [selectedAvatar, setSelectedAvatar] = useState("")
    const [avatarDialogOpen, setAvatarDialogOpen] = useState(false)
    const [avatarLoading, setAvatarLoading] = useState(false)


    // Avatar options
    const getAvatarPath = (variant: string) => `/images/avatars/${variant}/full.png`

    // Avatar update handler
    async function updateAvatar(event: React.FormEvent) {
        event.preventDefault()
        setAvatarLoading(true)

        const newAvatarID: number = avatarVariants.indexOf(selectedAvatar);

        /* Send request */
        const body = JSON.stringify({
            "key": "avatar_id",
            "value": newAvatarID.toString(),
        })

        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include', // Include cookies for session management
            headers: { 'Content-Type': 'application/json' },
            body: body
        });

        /* 
        Close dialog and reset loading state.
        Regardless of success or failure, we want to close and reset the dialog.
        */
        setAvatarLoading(false)
        setAvatarDialogOpen(false)
        setSelectedAvatar("")

        /* On fail: show error message as toast */
        if (!(response.status === 303 || response.ok)) {
            // Try to get error message from response
            // If the response is not JSON, we will catch the error and use a generic message
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = (
                    <span>
                        <span className="font-semibold italic">{errorData.type}: </span> {errorData.description}
                    </span>
                )
            } catch (error) {
                // If JSON parsing fails, use a generic error message
                errorMessage = "An unexpected error occurred while updating your avatar. Please try again later.";
            }

            const errorHeader = (<span className="font-bold">Failed to update avatar</span>)

            // Show error toast and return early
            toast.error(errorHeader, {
                description: errorMessage,
                duration: 5000
            })
            return
        }

        /* 
        Success: reload page to reread JWT.
        */
        window.location.reload()
    }


    // Update handlers
    async function updateUsername(event: React.FormEvent) {
        event.preventDefault()
        setUsernameLoading(true)

        /* Send request */
        const body = JSON.stringify({
            "key": "username",
            "value": newUsername,
            "password": confirmPasswordForNewUsername
        })

        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include', // Include cookies for session management
            headers: { 'Content-Type': 'application/json' },
            body: body
        });

        /* 
        Close dialog and reset loading state.
        Regardless of success or failure, we want to close and reset the dialog.
        */
        setUsernameLoading(false)
        setUsernameDialogOpen(false)
        setNewUsername("")
        setConfirmPasswordForNewUsername("")

        /* On fail: show error message as toast */
        if (!(response.status === 303 || response.ok)) {
            // Try to get error message from response
            // If the response is not JSON, we will catch the error and use a generic message
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = (
                    <span>
                        <span className="font-semibold italic">{errorData.type}: </span> {errorData.description}
                    </span>
                )
            } catch (error) {
                // If JSON parsing fails, use a generic error message
                errorMessage = "An unexpected error occurred while updating your username. Please try again later.";
            }

            const errorHeader = (<span className="font-bold">Failed to change username</span>)

            // Show error toast and return early
            toast.error(errorHeader, {
                description: errorMessage,
                duration: 10000
            })
            return
        }

        /* 
        Success: reload page to reread JWT.
        */
        window.location.reload()
    }

    async function updateEmail(event: React.FormEvent) {
        event.preventDefault()
        setEmailLoading(true)

        // Simulate API call
        setTimeout(() => {
            setEmail(newEmail)
            setEmailLoading(false)
            setEmailDialogOpen(false)
            toast("Email updated", {
                description: "Your email has been updated successfully."
            })
        }, 1000)
    }

    async function updatePassword(event: React.FormEvent) {
        event.preventDefault();
        // Final validation before submit
        if (!validatePassword()) {
            return;
        }
        setPasswordLoading(true);

        /* Send request */
        const body = JSON.stringify({
            "key": "password",
            "value": newPassword,
            "password": currentPassword
        })

        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include', // Include cookies for session management
            headers: { 'Content-Type': 'application/json' },
            body: body
        });

        /* 
        Close dialog and reset loading state.
        Regardless of success or failure, we want to close and reset the dialog.
        */
        setPasswordLoading(false);
        handlePasswordDialogClose();

        /* On fail: show error message as toast */
        if (!(response.status === 303 || response.ok)) {
            // Try to get error message from response
            // If the response is not JSON, we will catch the error and use a generic message
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = (
                    <span>
                        <span className="font-semibold italic">{errorData.type}: </span> {errorData.description}
                    </span>
                )
            } catch (error) {
                // If JSON parsing fails, use a generic error message
                errorMessage = "An unexpected error occurred while updating your password. Please try again later.";
            }

            const errorHeader = (<span className="font-bold">Failed to change password</span>)

            // Show error toast and return early
            toast.error(errorHeader, {
                description: errorMessage,
                duration: 10000
            })
            return
        }

        /* 
        Success: reload page to reread JWT.
        */
        window.location.reload()

        // Simulate API call
        // setTimeout(() => {

        //     toast("Password updated", {
        //         description: "Your password has been updated successfully."
        //     })
        // }, 1000)
    }

    // Modify the toggle function to show the alert dialog first
    function handlePrivacyToggle() {
        // Store the pending value but don't apply it yet
        setPendingPrivacyValue(!hideAccount)
        setPrivacyDialogOpen(true)
    }

    // Function to confirm the hide account change
    function confirmPrivacyChange() {
        if (pendingPrivacyValue !== null) {
            // Apply the value
            sethideAccount(pendingPrivacyValue);

            // Close the dialog
            setPrivacyDialogOpen(false);

            // Show toast message
            toast(pendingPrivacyValue ? "Account Hidden" : "Account Visibility Restored", {
                description: pendingPrivacyValue
                    ? "Your account is now hidden from public leaderboards."
                    : "Your account is now visible on public leaderboards."
            });
        }
    }

    return (
        <div className="container max-w-3xl mx-auto pt-16 pb-16 px-8">
            <h1 className="text-4xl font-bold mb-8 text-center text-theme-secondary">Account Settings</h1>

            <Card>
                <CardHeader>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>
                        Update your account details and how others see you on the site.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">

                    {/* Avatar setting */}
                    <div className="flex items-center justify-between ">
                        <div className="space-y-3">
                            <Label htmlFor="current-avatar">Avatar</Label>
                            <div className="
                                h-40 w-40
                                flex items-center justify-center
                                p-1 overflow-hidden
                                bg-stone-100 border-stone-200
                                dark:bg-stone-800 dark:border-stone-600
                                border rounded-md
                            ">
                                <div className="relative h-full w-full">
                                    <Image
                                        src={getAvatarPath(currentAvatar)}
                                        alt="Avatar"
                                        fill
                                        className="object-cover"
                                    />
                                </div>

                            </div>
                        </div>
                        <Dialog
                            open={avatarDialogOpen}
                            onOpenChange={setAvatarDialogOpen}
                        >
                            <DialogTrigger asChild>
                                <Button variant="outline">Change</Button>
                            </DialogTrigger>
                            <DialogContent className="
                                w-[calc(100vw-2rem)] max-w-md
                                sm:max-w-2xl
                                xl:max-w-6xl"
                            >
                                <form onSubmit={updateAvatar}>
                                    <DialogHeader>
                                        <DialogTitle>Change avatar</DialogTitle>
                                        <DialogDescription>
                                            Select a new avatar from the options below.
                                        </DialogDescription>
                                    </DialogHeader>
                                    <div className="py-6">
                                        <div className="grid grid-cols-3 sm:grid-cols-4 xl:grid-cols-6">
                                            {avatarVariants.map((avatar, index) => (
                                                <div
                                                    key={avatar}
                                                    className={`
                                                        cursor-pointer rounded-md border-2
                                                        aspect-square flex items-center justify-center p-1
                                                        ${selectedAvatar === avatar
                                                            ? 'border-primary bg-primary/10'
                                                            : 'border-transparent hover:border-muted-foreground/20 hover:bg-muted'
                                                        }
                                                    `}
                                                    onClick={() => setSelectedAvatar(avatar)}
                                                >
                                                    <div className="relative h-full w-full">
                                                        <Image
                                                            src={getAvatarPath(avatar)}
                                                            alt={avatar}
                                                            fill
                                                            className="mx-auto"
                                                        />
                                                    </div>

                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <DialogFooter>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() => {
                                                setAvatarDialogOpen(false)
                                                setSelectedAvatar("")
                                            }}
                                        >
                                            Cancel
                                        </Button>
                                        <Button
                                            type="submit"
                                            disabled={avatarLoading || !selectedAvatar}
                                        >
                                            {avatarLoading ? "Saving..." : "Confirm Selection"}
                                        </Button>
                                    </DialogFooter>
                                </form>
                            </DialogContent>
                        </Dialog>
                    </div>

                    <Separator />

                    {/* Username setting */}
                    <div className="flex items-center justify-between">
                        <div className="space-y-3">
                            <Label htmlFor="current-username">Username</Label>
                            <div>
                                <Input id="current-username" value={username} readOnly className="bg-muted" />
                            </div>
                        </div>
                        <Dialog open={usernameDialogOpen} onOpenChange={setUsernameDialogOpen}>
                            <DialogTrigger asChild>
                                <Button variant="outline">Change</Button>
                            </DialogTrigger>
                            <DialogContent>
                                <form onSubmit={updateUsername}>
                                    <DialogHeader>
                                        <DialogTitle>Change username</DialogTitle>
                                        <DialogDescription>
                                            Enter a new username below. You'll need to confirm your password to make this change.
                                        </DialogDescription>
                                    </DialogHeader>

                                    <div className="py-4 space-y-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="new-username">New Username</Label>
                                            <Input
                                                id="new-username"
                                                value={newUsername}
                                                onChange={handleNewUsernameChange}
                                                className="mt-2"
                                                placeholder={username}
                                                autoFocus
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="confirmPasswordForNewUsername">Password</Label>
                                            <Input
                                                id="confirmPasswordForNewUsername"
                                                type="password"
                                                value={confirmPasswordForNewUsername}
                                                onChange={handleConfirmPasswordForUsernameChange}  // Use the new handler
                                            />
                                        </div>
                                    </div>

                                    <DialogFooter>
                                        <Button type="button" variant="outline" onClick={() => setUsernameDialogOpen(false)}>
                                            Cancel
                                        </Button>
                                        <Button type="submit" disabled={usernameLoading || !newUsername}>
                                            {usernameLoading ? "Saving..." : "Save Changes"}
                                        </Button>
                                    </DialogFooter>
                                </form>
                            </DialogContent>
                        </Dialog>
                    </div>

                    <Separator />

                    {/* Email setting */}
                    <div className="flex items-center justify-between">
                        <div className="space-y-3">
                            <Label htmlFor="current-email">Email Address</Label>
                            <div>
                                <Input id="current-email" value={email} readOnly className="bg-muted" />
                            </div>
                        </div>
                        <Dialog open={emailDialogOpen} onOpenChange={setEmailDialogOpen}>
                            <DialogTrigger asChild>
                                <Button variant="outline">Change</Button>
                            </DialogTrigger>
                            <DialogContent>
                                <form onSubmit={updateEmail}>
                                    <DialogHeader>
                                        <DialogTitle>Change email address</DialogTitle>
                                        <DialogDescription>
                                            Enter a new email address below.
                                        </DialogDescription>
                                    </DialogHeader>
                                    <div className="py-4">
                                        <Label htmlFor="new-email">New Email Address</Label>
                                        <Input
                                            id="new-email"
                                            type="email"
                                            value={newEmail}
                                            onChange={(e) => setNewEmail(e.target.value)}
                                            className="mt-2"
                                            placeholder={email}
                                            autoFocus
                                        />
                                    </div>
                                    <DialogFooter>
                                        <Button type="button" variant="outline" onClick={() => setEmailDialogOpen(false)}>
                                            Cancel
                                        </Button>
                                        <Button type="submit" disabled={emailLoading || !newEmail}>
                                            {emailLoading ? "Saving..." : "Save Changes"}
                                        </Button>
                                    </DialogFooter>
                                </form>
                            </DialogContent>
                        </Dialog>
                    </div>

                    <Separator />

                    {/* Password setting */}
                    <div className="flex items-center justify-between">
                        <div className="space-y-3">
                            <Label>Password</Label>
                            <div>
                                <Input value="••••••••" readOnly className="bg-muted" />
                            </div>
                        </div>
                        <Dialog
                            open={passwordDialogOpen}
                            onOpenChange={(open) => {
                                if (!open) {
                                    handlePasswordDialogClose();
                                } else {
                                    setPasswordDialogOpen(true);
                                }
                            }}
                        >
                            <DialogTrigger asChild>
                                <Button variant="outline">Change</Button>
                            </DialogTrigger>
                            <DialogContent className="sm:max-w-[425px]">
                                <form onSubmit={updatePassword}>
                                    <DialogHeader>
                                        <DialogTitle>Change password</DialogTitle>
                                        <DialogDescription>
                                            Enter your current password and a new password.
                                        </DialogDescription>
                                    </DialogHeader>
                                    <div className="py-4 space-y-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="current-password">Current Password</Label>
                                            <Input
                                                id="current-password"
                                                type="password"
                                                value={currentPassword}
                                                onChange={handleCurrentPasswordChange}  // Use the new handler
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="new-password">New Password</Label>
                                            <Input
                                                id="new-password"
                                                type="password"
                                                value={newPassword}
                                                onChange={handleNewPasswordChange}
                                                className={passwordErrors.newPassword && newPassword ? "border-red-500" : ""}
                                            />
                                            {passwordErrors.newPassword && newPassword && (
                                                <p className="text-sm text-red-500">{passwordErrors.newPassword[0]}</p>
                                            )}
                                        </div>

                                        <div className="space-y-2">
                                            <Label htmlFor="confirm-password">Confirm New Password</Label>
                                            <Input
                                                id="confirm-password"
                                                type="password"
                                                value={confirmPassword}
                                                onChange={handleConfirmPasswordChange}
                                                className={passwordErrors.confirmPassword && confirmPassword ? "border-red-500" : ""}
                                            />
                                            {passwordErrors.confirmPassword && confirmPassword && (
                                                <p className="text-sm text-red-500">{passwordErrors.confirmPassword[0]}</p>
                                            )}
                                        </div>
                                    </div>
                                    <DialogFooter>

                                        <Button type="button" variant="outline" onClick={handlePasswordDialogClose}>
                                            Cancel
                                        </Button>

                                        <Button
                                            type="submit"
                                            disabled={
                                                passwordLoading ||
                                                !currentPassword ||
                                                !newPassword ||
                                                Object.keys(passwordErrors).length > 0 // Disable if validation errors exist
                                            }
                                        >
                                            {passwordLoading ? "Saving..." : "Save Changes"}
                                        </Button>

                                    </DialogFooter>
                                </form>
                            </DialogContent>
                        </Dialog>
                    </div>

                    <Separator />

                    {/* Opt out for leaderboard */}
                    <div className="flex items-center justify-between">
                        <div>
                            <Label htmlFor="privacy-switch" className="text-base">Hide my account</Label>
                            <p className="text-sm text-muted-foreground">
                                Makes your account private and hides it from the public leaderboards.
                            </p>
                        </div>
                        <Switch
                            id="privacy-switch"
                            checked={hideAccount}
                            onCheckedChange={handlePrivacyToggle}
                            className="data-[state=checked]:bg-red-600 hover:data-[state=checked]:bg-red-700 hover:data-[state=unchecked]:bg-orange-300"
                        />

                        {/* Alert Dialog */}
                        <AlertDialog
                            open={privacyDialogOpen}
                            onOpenChange={(open) => {
                                setPrivacyDialogOpen(open);
                                // Only reset pendingPrivacyValue when dialog is fully closed
                                if (!open) {
                                    // Use setTimeout to wait for animation to finish
                                    setTimeout(() => {
                                        setPendingPrivacyValue(null);
                                    }, 300); // Animation duration in ms
                                }
                            }}
                        >
                            <AlertDialogContent>
                                <AlertDialogHeader>
                                    <AlertDialogTitle>
                                        {pendingPrivacyValue
                                            ? "Hide your account from leaderboards?"
                                            : "Make your account public again?"}
                                    </AlertDialogTitle>
                                    <AlertDialogDescription>
                                        {pendingPrivacyValue
                                            ? "Your submissions will still be processed, but your name and results won't appear in any public leaderboards."
                                            : "Your name and results will be visible on our public leaderboards."}
                                    </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction
                                        onClick={confirmPrivacyChange}
                                        className={pendingPrivacyValue ? "bg-red-600 hover:bg-red-700" : "bg-green-500 hover:bg-green-600"}
                                    >
                                        {pendingPrivacyValue ? "Hide my account" : "Make my account public"}
                                    </AlertDialogAction>
                                </AlertDialogFooter>
                            </AlertDialogContent>
                        </AlertDialog>
                    </div>

                </CardContent>
            </Card>
        </div>
    )
}