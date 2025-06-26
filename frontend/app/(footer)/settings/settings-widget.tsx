"use client"

import Image from "next/image";
import { toast } from "sonner";
import { z } from "zod"

import { useState } from "react"
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
import { getSettingsResponse } from "./getSettings";
import React from "react";
import { cn } from "@/lib/utils";


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

export default function SettingsWidget({ currentSettings }: { currentSettings: getSettingsResponse }) {
    return (
        <div className="container max-w-2xl mx-auto pt-16 pb-16 px-8 ">
            <h1 className="text-4xl font-bold mb-8 text-center text-theme-primary">Account Settings</h1>
            <Card className="border-stone-200 dark:bg-stone-900 dark:border-stone-700">
                <CardHeader>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>
                        Update your account details and how others see you on the site.
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">

                    <AvatarSetting currentAvatarId={currentSettings.avatar_id} />
                    <Separator />

                    <UsernameSetting currentUsername={currentSettings.username} />
                    <Separator />

                    <EmailSetting currentEmail={currentSettings.email} />
                    <Separator />

                    <PasswordSetting />
                    <Separator />

                    <PrivacyToggleSetting currentPrivate={currentSettings.private} />

                </CardContent>
            </Card>
        </div>
    )
}

// --- Change Button Component ---
const ChangeButton = React.forwardRef<HTMLButtonElement, React.ComponentProps<typeof Button>>(
    (props, ref) => (
        <Button
            ref={ref}
            className="
                hidden sm:block
                rounded-md cursor-pointer 
                hover:bg-stone-200
                dark:bg-stone-800 dark:border-stone-600 dark:hover:bg-stone-600 
            "
            variant="outline"
            {...props}
        >
            Change
        </Button>
    )
);
ChangeButton.displayName = "ChangeButton";

// --- Email Setting Component ---
function EmailSetting({ currentEmail }: { currentEmail: string }) {
    return (
        <div className="flex items-center justify-between">
            <div className="space-y-3">
                <Label htmlFor="current-email">Email Address</Label>
                <div>
                    <Input 
                        id="current-email" 
                        value={currentEmail} 
                        readOnly 
                        className="bg-stone-100 dark:bg-stone-900 text-stone-500 dark:text-neutral-400" 
                    />
                </div>
            </div>
        </div>
    )
}

// --- Avatar Setting Component ---
function AvatarSetting({ currentAvatarId }: { currentAvatarId: number }) {
    const currentAvatarName: string = avatarVariantsData[currentAvatarId];
    const [currentAvatar, setCurrentAvatar] = useState(currentAvatarName)
    const [selectedAvatar, setSelectedAvatar] = useState("")
    const [avatarDialogOpen, setAvatarDialogOpen] = useState(false)
    const [avatarLoading, setAvatarLoading] = useState(false)

    const getAvatarPath = (variant: string) => `/images/avatars/${variant}/full.png`

    async function updateAvatar(event: React.FormEvent) {
        event.preventDefault()
        setAvatarLoading(true)
        const newAvatarID: number = avatarVariantsData.indexOf(selectedAvatar);
        const body = JSON.stringify({
            "key": "avatar_id",
            "value": newAvatarID.toString(),
        })
        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        setAvatarLoading(false)
        setAvatarDialogOpen(false)
        setSelectedAvatar("")
        
        if (!(response.status === 303 || response.ok)) {
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = (
                    <span>
                        <span className="font-semibold italic">{errorData.type}: </span> {errorData.description}
                    </span>
                )
            } catch (error) {
                errorMessage = "An unexpected error occurred while updating your avatar. Please try again later.";
            }
            const errorHeader = (<span className="font-bold">Failed to update avatar</span>)
            toast.error(errorHeader, {
                description: errorMessage,
                duration: 5000
            })
            return
        }
        window.location.reload()
    }

    return (
        <div>
            <Label htmlFor="current-avatar" className="block mb-3">Avatar</Label>
            <Dialog
                open={avatarDialogOpen}
                onOpenChange={setAvatarDialogOpen}
            >
                <div className="flex items-center justify-between">
                    <DialogTrigger asChild>
                        <div className="h-40 w-40 flex items-center justify-center p-1 overflow-hidden bg-stone-100 border-stone-200 dark:bg-stone-800 dark:border-stone-600 border rounded-md cursor-pointer hover:bg-stone-200 dark:hover:bg-stone-700 transition-colors">
                            <div className="relative h-full w-full">
                                <Image
                                    src={getAvatarPath(currentAvatar)}
                                    alt="Avatar"
                                    fill
                                    className="object-cover"
                                />
                            </div>
                        </div>
                    </DialogTrigger>
                    <DialogTrigger asChild>
                        <ChangeButton />
                    </DialogTrigger>
                </div>
                
                <DialogContent className="w-[calc(100vw-2rem)] max-w-md sm:max-w-2xl xl:max-w-6xl">
                    <form onSubmit={updateAvatar}>
                        <DialogHeader>
                            <DialogTitle>Change avatar</DialogTitle>
                            <DialogDescription>
                                Select a new avatar from the options below.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="py-6">
                            <div className="grid grid-cols-3 sm:grid-cols-4 xl:grid-cols-6">
                                {avatarVariantsData.map((avatar, index) => (
                                    <div
                                        key={avatar}
                                        className={`
                                            cursor-pointer rounded-md 
                                            border-2 
                                            aspect-square flex items-center justify-center p-1 
                                            ${selectedAvatar === avatar ? 'border-primary dark:border-stone-600 bg-primary/10 dark:bg-stone-800' : 'border-transparent hover:border-muted-foreground/20 dark:hover:border-stone-700 hover:bg-muted dark:hover:bg-stone-900'}`}
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
                                className="cursor-pointer"
                            >
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                disabled={avatarLoading || !selectedAvatar}
                                className={cn(avatarLoading || !selectedAvatar ? "" : "cursor-pointer", "")}
                            >
                                {avatarLoading ? "Saving..." : "Confirm Selection"}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>
        </div>
    )
}

// --- Username Setting Component ---
function UsernameSetting({ currentUsername }: { currentUsername: string }) {
    const [username, setUsername] = useState(currentUsername)
    const [newUsername, setNewUsername] = useState("")
    const [confirmPasswordForNewUsername, setConfirmPasswordForNewUsername] = useState("")
    const [usernameLoading, setUsernameLoading] = useState(false)
    const [usernameDialogOpen, setUsernameDialogOpen] = useState(false)
    const [usernameErrors, setUsernameErrors] = useState<{
        newUsername?: string[];
        password?: string[];
    }>({});
    
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
    const handleNewUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setNewUsername(e.target.value);
        validateUsername();
    };
    const handleConfirmPasswordForUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setConfirmPasswordForNewUsername(e.target.value);
        validateUsername();
    };
    async function updateUsername(event: React.FormEvent) {
        event.preventDefault()
        setUsernameLoading(true)
        const body = JSON.stringify({
            "key": "username",
            "value": newUsername,
            "password": confirmPasswordForNewUsername
        })
        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        setUsernameLoading(false)
        setUsernameDialogOpen(false)
        setNewUsername("")
        setConfirmPasswordForNewUsername("")
        if (!(response.status === 303 || response.ok)) {
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = (
                    <span>
                        <span className="font-semibold italic">{errorData.type}: </span> {errorData.description}
                    </span>
                )
            } catch (error) {
                errorMessage = "An unexpected error occurred while updating your username. Please try again later.";
            }
            const errorHeader = (<span className="font-bold">Failed to change username</span>)
            toast.error(errorHeader, {
                description: errorMessage,
                duration: 10000
            })
            return
        }
        window.location.reload()
    }
    return (
        <div>
            <Label htmlFor="current-username" className="block mb-3">Username</Label>
            <Dialog open={usernameDialogOpen} onOpenChange={setUsernameDialogOpen}>
                <div className="flex items-center justify-between">
                    <DialogTrigger asChild>
                        <div className="cursor-pointer">
                            <Input id="current-username" value={username} readOnly className="bg-stone-100 border-stone-200 dark:bg-stone-800 dark:border-stone-600 border rounded-md cursor-pointer hover:bg-stone-200 dark:hover:bg-stone-700 transition-colors" />
                        </div>
                    </DialogTrigger>
                    <DialogTrigger asChild>
                        <ChangeButton />
                    </DialogTrigger>
                </div>
                <DialogContent>
                    <form onSubmit={updateUsername}>
                        <DialogHeader>
                            <DialogTitle>Change username</DialogTitle>
                            <DialogDescription>
                                Enter a new username below. You'll need to confirm your password to make this change.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="py-6 space-y-6">
                            <div className="space-y-4">
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
                            <div className="space-y-4">
                                <Label htmlFor="confirmPasswordForNewUsername">Password</Label>
                                <Input
                                    id="confirmPasswordForNewUsername"
                                    type="password"
                                    value={confirmPasswordForNewUsername}
                                    onChange={handleConfirmPasswordForUsernameChange}
                                />
                            </div>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => setUsernameDialogOpen(false)} className="cursor-pointer">
                                Cancel
                            </Button>
                            <Button type="submit" disabled={usernameLoading || !newUsername} className={usernameLoading || !newUsername ? "" : "cursor-pointer"}>
                                {usernameLoading ? "Saving..." : "Save Changes"}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>
        </div>
    )
}

// --- Password Setting Component ---
function PasswordSetting() {
    const [passwordDialogOpen, setPasswordDialogOpen] = useState(false)
    const [currentPassword, setCurrentPassword] = useState("")
    const [newPassword, setNewPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [passwordLoading, setPasswordLoading] = useState(false)
    const [passwordErrors, setPasswordErrors] = useState<{
        currentPassword?: string[];
        newPassword?: string[];
        confirmPassword?: string[];
    }>({});
    
    // Password form data interface
    interface PasswordFormData {
        currentPassword: string;
        newPassword: string;
        confirmPassword: string;
    }

    // Zod schema for password update form
    const passwordSchema = z.object({
        currentPassword: z.string().min(1, { message: "Current password is required" }),
        newPassword: z.string().min(8, { message: "Password must be at least 8 characters long" }),
        confirmPassword: z.string().min(1, { message: "Please confirm your password" })
    }).refine((data: PasswordFormData) => data.newPassword === data.confirmPassword, {
        message: "Passwords don't match",
        path: ["confirmPassword"]
    });
    const validatePassword = (currentPwd?: string, newPwd?: string, confirmPwd?: string) => {
        const currentPassword_val = currentPwd ?? currentPassword;
        const newPassword_val = newPwd ?? newPassword;
        const confirmPassword_val = confirmPwd ?? confirmPassword;
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
    const handleNewPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setNewPassword(newValue);
        validatePassword(currentPassword, newValue, confirmPassword);
    };
    const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setConfirmPassword(newValue);
        validatePassword(currentPassword, newPassword, newValue);
    };
    const handleCurrentPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setCurrentPassword(newValue);
        validatePassword(newValue, newPassword, confirmPassword);
    };
    const handlePasswordDialogClose = () => {
        setPasswordDialogOpen(false);
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");
        setPasswordErrors({});
    };
    
    async function updatePassword(event: React.FormEvent) {
        event.preventDefault();
        if (!validatePassword()) {
            return;
        }
        setPasswordLoading(true);
        const body = JSON.stringify({
            "key": "password",
            "value": newPassword,
            "password": currentPassword
        })
        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        setPasswordLoading(false);
        
        if (!(response.status === 303 || response.ok)) {
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = (
                    <span>
                        <span className="font-semibold italic">{errorData.type}: </span> {errorData.description}
                    </span>
                )
            } catch (error) {
                errorMessage = "An unexpected error occurred while updating your password. Please try again later.";
            }
            const errorHeader = (<span className="font-bold">Failed to change password</span>)
            toast.error(errorHeader, {
                description: errorMessage,
                duration: 10000
            })
            return
        }
        
        handlePasswordDialogClose();
        toast("Password updated", {
            description: "Your password has been updated successfully."
        });
    }

    return (
        <div>
            <Label className="block mb-3">Password</Label>
            <Dialog
                open={passwordDialogOpen}
                onOpenChange={(open: boolean) => {
                    if (!open) {
                        handlePasswordDialogClose();
                    } else {
                        setPasswordDialogOpen(true);
                    }
                }}
            >
                <div className="flex items-center justify-between">
                    <DialogTrigger asChild>
                        <div className="cursor-pointer">
                            <Input value="••••••••" readOnly className="bg-stone-100 border-stone-200 dark:bg-stone-800 dark:border-stone-600 border rounded-md cursor-pointer hover:bg-stone-200 dark:hover:bg-stone-700 transition-colors" />
                        </div>
                    </DialogTrigger>
                    <DialogTrigger asChild>
                        <ChangeButton />
                    </DialogTrigger>
                </div>
                <DialogContent className="sm:max-w-[425px]">
                    <form onSubmit={updatePassword}>
                        <DialogHeader>
                            <DialogTitle>Change password</DialogTitle>
                            <DialogDescription>
                                Enter your current password and a new password.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="py-6 space-y-6">
                            <div className="space-y-4">
                                <Label htmlFor="current-password" className="font-semibold">Current Password</Label>
                                <Input
                                    id="current-password"
                                    type="password"
                                    value={currentPassword}
                                    onChange={handleCurrentPasswordChange}
                                />
                            </div>
                            <div className="space-y-4">
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
                            <div className="space-y-4">
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
                            <Button type="button" variant="outline" onClick={handlePasswordDialogClose} className="cursor-pointer">
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                disabled={
                                    passwordLoading ||
                                    !currentPassword ||
                                    !newPassword ||
                                    Object.keys(passwordErrors).length > 0
                                }
                                className={
                                    passwordLoading ||
                                    !currentPassword ||
                                    !newPassword ||
                                    Object.keys(passwordErrors).length > 0
                                        ? ""
                                        : "cursor-pointer"
                                }
                            >
                                {passwordLoading ? "Saving..." : "Save Changes"}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>
        </div>
    )
}

// --- Privacy Toggle Setting Component ---
function PrivacyToggleSetting({ currentPrivate }: { currentPrivate: boolean }) {
    const [isPrivate, setisPrivate] = useState(currentPrivate)
    const [privacyDialogOpen, setPrivacyDialogOpen] = useState(false)
    const [pendingPrivacyValue, setPendingPrivacyValue] = useState<boolean | null>(null)
    const [privacyLoading, setPrivacyLoading] = useState(false)
    
    function handlePrivacyToggle() {
        setPendingPrivacyValue(!isPrivate)
        setPrivacyDialogOpen(true)
    }

    async function confirmPrivacyChange() {
        /* Early return if toggle is not pending (i.e. if the dialog is not open) */
        if (pendingPrivacyValue === null) {
            return;
        }

        setPrivacyLoading(true);

        const body = JSON.stringify({
            "key": "private",
            "value": pendingPrivacyValue ? "1" : "0"
        })

        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        
        setPrivacyLoading(false);
        
        if (!(response.status === 303 || response.ok)) {
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = (
                    <span>
                        <span className="font-semibold italic">{errorData.type}: </span> {errorData.description}
                    </span>
                )
            } catch (error) {
                errorMessage = "An unexpected error occurred while updating your privacy setting. Please try again later.";
            }
            const errorHeader = (<span className="font-bold">Failed to update privacy setting</span>)

            toast.error(errorHeader, {
                description: errorMessage,
                duration: 10000
            })

            return
        }
        
        setPrivacyDialogOpen(false);
        setisPrivate(pendingPrivacyValue);
        toast(pendingPrivacyValue ? "Account Hidden" : "Account Visibility Restored", {
            description: pendingPrivacyValue
                ? "Your account is now hidden from public leaderboards."
                : "Your account is now visible on public leaderboards."
        });

    }

    return (
        <div className="flex items-center justify-between">
            <div>
                <Label htmlFor="privacy-switch" className="text-base">Hide my account</Label>
                <p className="text-sm text-muted-foreground">
                    Makes your account private and hides it from the public leaderboards.
                </p>
            </div>

            <Switch
                id="privacy-switch"
                checked={isPrivate}
                onCheckedChange={handlePrivacyToggle}
                className="
                    cursor-pointer
                    data-[state=checked]:bg-red-600 
                    hover:data-[state=checked]:bg-red-700 dark:hover:data-[state=checked]:bg-red-500 
                    hover:data-[state=unchecked]:bg-orange-300 dark:hover:data-[state=unchecked]:bg-orange-400
                "
            />

            <AlertDialog
                open={privacyDialogOpen}
                onOpenChange={(open: boolean) => {
                    if (!open && !privacyLoading) {
                        setPrivacyDialogOpen(open);
                        setTimeout(() => {
                            setPendingPrivacyValue(null);
                        }, 300);
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
                        <AlertDialogCancel disabled={privacyLoading} className={privacyLoading ? "" : "cursor-pointer"}>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={confirmPrivacyChange}
                            disabled={privacyLoading}
                            className={`${pendingPrivacyValue ? "bg-red-600 hover:bg-red-700" : "bg-green-500 hover:bg-green-600"} ${privacyLoading ? "" : "cursor-pointer"}`}
                        >
                            {privacyLoading ? "Saving..." : (pendingPrivacyValue ? "Hide my account" : "Make my account public")}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}

