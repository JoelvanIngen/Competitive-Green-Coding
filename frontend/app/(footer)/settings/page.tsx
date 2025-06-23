"use client"

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
import { Switch } from "@/components/ui/switch"

export default function SettingsPage() {
  // User data
  const [username, setUsername] = useState("greencoder123")
  const [email, setEmail] = useState("user@example.com")
  const [emailNotifications, setEmailNotifications] = useState(true)
  
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

  async function toggleNotifications() {
    const newValue = !emailNotifications
    setEmailNotifications(newValue)
    
    // Simulate API call
    toast("Notification preferences updated", {
      description: `Email notifications ${newValue ? "enabled" : "disabled"}.`
    })
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
          {/* Username setting */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
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
            <div className="space-y-1">
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
            <div className="space-y-1">
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
          
          {/* Notification preferences */}
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="notifications" className="text-base">Email Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Receive email updates about your account activity.
              </p>
            </div>
            <Switch 
              id="notifications" 
              checked={emailNotifications} 
              onCheckedChange={toggleNotifications}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}