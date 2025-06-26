"use client"

import Image from "next/image";
import { toast } from "sonner";

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

import avatarVariantsData from '@/public/images/avatars/avatar_id.json'
import { getSettingsResponse } from "./getSettings";
import React from "react";
import { cn } from "@/lib/utils";
import { useFormValidation } from "@/lib/form-validation/form-validation";
import { usernameChangeSchema, passwordChangeSchema } from "@/lib/form-validation/schemas";

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
    const [usernameLoading, setUsernameLoading] = useState(false)
    const [usernameDialogOpen, setUsernameDialogOpen] = useState(false)
    
    const {
        formState,
        handleChange,
        handleBlur,
        mergedErrors,
        validate,
        resetForm
    } = useFormValidation(usernameChangeSchema, {
        newUsername: "",
        password: ""
    })

    // Helper function to check if username form is valid
    function isUsernameFormValid() {
        return formState.newUsername && 
               formState.password && 
               !mergedErrors("newUsername") && 
               !mergedErrors("password");
    }

    async function updateUsername(event: React.FormEvent) {
        event.preventDefault()
        
        const errors = validate(formState)
        if (Object.keys(errors).length > 0) {
            return
        }
        
        setUsernameLoading(true)
        const body = JSON.stringify({
            "key": "username",
            "value": formState.newUsername,
            "password": formState.password
        })
        const response = await fetch("api/settings", {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        setUsernameLoading(false)
        setUsernameDialogOpen(false)
        resetForm()
        
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
                                <Label htmlFor="new-username" className="font-semibold">New Username</Label>
                                <Input
                                    id="new-username"
                                    name="newUsername"
                                    value={formState.newUsername}
                                    onChange={handleChange}
                                    onBlur={() => handleBlur("newUsername")}
                                    className="mt-2"
                                    placeholder={username}
                                    autoFocus
                                />
                                {mergedErrors("newUsername") && (
                                    <p className="text-sm text-red-500">{mergedErrors("newUsername")?.[0]}</p>
                                )}
                            </div>
                            <div className="space-y-4">
                                <Label htmlFor="confirmPasswordForNewUsername" className="font-semibold">Password</Label>
                                <Input
                                    id="confirmPasswordForNewUsername"
                                    name="password"
                                    type="password"
                                    value={formState.password}
                                    onChange={handleChange}
                                    onBlur={() => handleBlur("password")}
                                />
                                {mergedErrors("password") && (
                                    <p className="text-sm text-red-500">{mergedErrors("password")?.[0]}</p>
                                )}
                            </div>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => setUsernameDialogOpen(false)} className="cursor-pointer">
                                Cancel
                            </Button>
                            <Button type="submit" disabled={usernameLoading || !isUsernameFormValid()} className={cn(usernameLoading || !isUsernameFormValid() ? "" : "cursor-pointer", "")}>
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
    const [passwordLoading, setPasswordLoading] = useState(false)
    
    const {
        formState,
        handleChange,
        handleBlur,
        mergedErrors,
        validate,
        resetForm
    } = useFormValidation(passwordChangeSchema, {
        currentPassword: "",
        newPassword: "",
        confirmPassword: ""
    })

    // Helper function to check if password form is valid
    function isPasswordFormValid() {
        return formState.currentPassword && 
               formState.newPassword && 
               formState.confirmPassword && 
               !mergedErrors("currentPassword") && 
               !mergedErrors("newPassword") && 
               !mergedErrors("confirmPassword");
    }

    const handlePasswordDialogClose = () => {
        setPasswordDialogOpen(false);
        resetForm();
    };
    
    async function updatePassword(event: React.FormEvent) {
        event.preventDefault();
        
        const errors = validate(formState)
        if (Object.keys(errors).length > 0) {
            return;
        }
        
        setPasswordLoading(true);
        const body = JSON.stringify({
            "key": "password",
            "value": formState.newPassword,
            "password": formState.currentPassword
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
                                    name="currentPassword"
                                    type="password"
                                    value={formState.currentPassword}
                                    onChange={handleChange}
                                    onBlur={() => handleBlur("currentPassword")}
                                />
                                {mergedErrors("currentPassword") && (
                                    <p className="text-sm text-red-500">{mergedErrors("currentPassword")?.[0]}</p>
                                )}
                            </div>
                            <div className="space-y-4">
                                <Label htmlFor="new-password" className="font-semibold">New Password</Label>
                                <Input
                                    id="new-password"
                                    name="newPassword"
                                    type="password"
                                    value={formState.newPassword}
                                    onChange={handleChange}
                                    onBlur={() => handleBlur("newPassword")}
                                />
                                {mergedErrors("newPassword") && (
                                    <p className="text-sm text-red-500">{mergedErrors("newPassword")?.[0]}</p>
                                )}
                            </div>
                            <div className="space-y-4">
                                <Label htmlFor="confirm-password" className="font-semibold">Confirm New Password</Label>
                                <Input
                                    id="confirm-password"
                                    name="confirmPassword"
                                    type="password"
                                    value={formState.confirmPassword}
                                    onChange={handleChange}
                                    onBlur={() => handleBlur("confirmPassword")}
                                />
                                {mergedErrors("confirmPassword") && (
                                    <p className="text-sm text-red-500">{mergedErrors("confirmPassword")?.[0]}</p>
                                )}
                            </div>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={handlePasswordDialogClose} className="cursor-pointer">
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                disabled={passwordLoading || !isPasswordFormValid()}
                                className={cn(passwordLoading || !isPasswordFormValid() ? "" : "cursor-pointer", "")}
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

