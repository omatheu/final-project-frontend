"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Paperclip, Mic, Send, Loader2 } from "lucide-react"

interface MessageInputProps {
  onSendMessage: (message: string) => void
  isLoading?: boolean
}

export function MessageInput({ onSendMessage, isLoading }: MessageInputProps) {
  const [message, setMessage] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  return (
    <div className="border-t border-border p-4">
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <Button variant="ghost" size="sm" type="button" className="h-9 w-9 p-0 flex-shrink-0 text-white/80 hover:text-white">
          <Paperclip className="h-4 w-4" />
        </Button>

        <div className="flex-1 relative">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me something"
            className="pr-20 bg-background border-input text-white placeholder:text-white/70"
            disabled={isLoading}
          />
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
            <Button variant="ghost" size="sm" type="button" className="h-6 w-6 p-0 text-white/80 hover:text-white">
              <Mic className="h-3 w-3" />
            </Button>
            <Button type="submit" size="sm" className="h-6 w-6 p-0 text-white/80 hover:text-white" disabled={!message.trim() || isLoading}>
              {isLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Send className="h-3 w-3" />}
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
}
