"use client"

import Image from "next/image";
import { JWTPayload } from "jose";

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
import { toast } from "sonner"
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
import { get } from "http";

export default function SettingsWidget({ session }: { session: JWTPayload }) {
    // User data
    const [username, setUsername] = useState(session.username)
    const [email, setEmail] = useState("user@example.com")
    const [hideAccount, sethideAccount] = useState(false)

    // Form states for dialogs
    const [newUsername, setNewUsername] = useState("")
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

    // Avatar states
    const [currentAvatar, setCurrentAvatar] = useState("monkey")
    const [selectedAvatar, setSelectedAvatar] = useState("")
    const [avatarDialogOpen, setAvatarDialogOpen] = useState(false)
    const [avatarLoading, setAvatarLoading] = useState(false)

    // Avatar options
    const getAvatarPath = (variant: string) => `/images/avatars/${variant}/full.png`

    // Avatar variants
    const avatarVariants = [
        "default",
        "girl",
        "pirate",
        "monkey",
        "lion",
        "giraffe",
        "rhino",
        "elephant",
        "frog",
        "eagle",
        "shark",
        "penguin",
    ]

    // Avatar update handler
    async function updateAvatar(event: React.FormEvent) {
        event.preventDefault()
        setAvatarLoading(true)

        // Simulate API call
        setTimeout(() => {
            setCurrentAvatar(selectedAvatar)
            setAvatarLoading(false)
            setAvatarDialogOpen(false)
            setSelectedAvatar("")
            toast("Avatar updated", {
                description: "Your profile picture has been updated successfully."
            })
        }, 1000)
    }


    // Update handlers
    async function updateUsername(event: React.FormEvent) {
        event.preventDefault()
        setUsernameLoading(true)

        // Simulate API call
        setTimeout(() => {
            setUsername(newUsername)
            setUsernameLoading(false)
            setUsernameDialogOpen(false)
            toast("Username updated", {
                description: "Your username has been updated successfully."
            })
        }, 1000)
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
        event.preventDefault()
        setPasswordLoading(true)

        // Simulate API call
        setTimeout(() => {
            setCurrentPassword("")
            setNewPassword("")
            setConfirmPassword("")
            setPasswordLoading(false)
            setPasswordDialogOpen(false)
            toast("Password updated", {
                description: "Your password has been updated successfully."
            })
        }, 1000)
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
                                {/*  */}
                                <form onSubmit={updateAvatar}>
                                    <DialogHeader>
                                        <DialogTitle>Change avatar</DialogTitle>
                                        <DialogDescription>
                                            Select a new avatar from the options below.
                                        </DialogDescription>
                                    </DialogHeader>
                                    <div className="py-6">
                                        <div className="grid grid-cols-3 sm:grid-cols-4 xl:grid-cols-6">
                                            {/*  */}
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
                                            Enter a new username below.
                                        </DialogDescription>
                                    </DialogHeader>
                                    <div className="py-4">
                                        <Label htmlFor="new-username">New Username</Label>
                                        <Input
                                            id="new-username"
                                            value={newUsername}
                                            onChange={(e) => setNewUsername(e.target.value)}
                                            className="mt-2"
                                            placeholder={username}
                                            autoFocus
                                        />
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
                        <Dialog open={passwordDialogOpen} onOpenChange={setPasswordDialogOpen}>
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
                                                onChange={(e) => setCurrentPassword(e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="new-password">New Password</Label>
                                            <Input
                                                id="new-password"
                                                type="password"
                                                value={newPassword}
                                                onChange={(e) => setNewPassword(e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="confirm-password">Confirm New Password</Label>
                                            <Input
                                                id="confirm-password"
                                                type="password"
                                                value={confirmPassword}
                                                onChange={(e) => setConfirmPassword(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                    <DialogFooter>
                                        <Button type="button" variant="outline" onClick={() => setPasswordDialogOpen(false)}>
                                            Cancel
                                        </Button>
                                        <Button
                                            type="submit"
                                            disabled={passwordLoading || !currentPassword || !newPassword || newPassword !== confirmPassword}
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