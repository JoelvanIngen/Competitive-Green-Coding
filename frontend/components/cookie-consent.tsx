"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

const COOKIE_NAME = "cookie_consent"

function setConsentCookie() {
  const expires = new Date()
  expires.setDate(expires.getDate() + 30)
  document.cookie = `${COOKIE_NAME}=accepted; expires=${expires.toUTCString()}; path=/`
}

function hasConsent(): boolean {
  return document.cookie.includes(`${COOKIE_NAME}=accepted`)
}

export default function CookieConsent() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!hasConsent()) {
      setVisible(true)
    }
  }, [])

  const handleAccept = () => {
    setConsentCookie()
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 flex justify-center">
      <Card className="max-w-xl w-full bg-theme-bg text-theme-text border border-muted shadow-md">
        <CardContent className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4 px-6">
          <p className="text-sm text-muted-foreground">
            We use functional cookies to ensure the proper functioning of our website.
          </p>
          <Button onClick={handleAccept}>Accept</Button>
        </CardContent>
      </Card>
    </div>
  )
}
