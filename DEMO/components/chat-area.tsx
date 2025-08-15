"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ThumbsUp, ThumbsDown, Copy, RotateCcw, Share, Loader2 } from "lucide-react"

interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
}

interface ChatAreaProps {
  messages: Message[]
  isLoading?: boolean
}

export function ChatArea({ messages, isLoading }: ChatAreaProps) {
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.map((message) => (
        <div key={message.id} className="flex gap-4">
          {message.sender === "ai" && (
            <Avatar className="h-8 w-8 flex-shrink-0">
              <AvatarFallback className="bg-primary text-primary-foreground text-xs">AI</AvatarFallback>
            </Avatar>
          )}

          <div className="flex-1 space-y-2">
            <div className="prose prose-invert max-w-none">
              {message.content.split("\n").map((line, index) => (
                <p key={index} className="text-white leading-relaxed mb-2">
                  {line}
                </p>
              ))}
            </div>

            {message.sender === "ai" && (
              <>
                {message.id === "2" && (
                  <div className="my-4">
                    <div className="bg-muted p-4 rounded-lg border border-border">
                      <img
                        src="/chaotic-freelancer-desk.png"
                        alt="Chaotic freelancer workspace"
                        className="rounded-lg w-full max-w-md"
                      />
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-2 mt-3">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-white/80 hover:text-white">
                    <ThumbsUp className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-white/80 hover:text-white">
                    <ThumbsDown className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-white/80 hover:text-white">
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-white/80 hover:text-white">
                    <RotateCcw className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-white/80 hover:text-white">
                    <Share className="h-3 w-3" />
                  </Button>
                </div>
              </>
            )}
          </div>

          {message.sender === "user" && (
            <div className="flex items-center gap-2">
              <div className="text-xs text-white">6/75</div>
              <Avatar className="h-8 w-8 flex-shrink-0">
                <AvatarImage src="/placeholder.svg?height=32&width=32" />
                <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">U</AvatarFallback>
              </Avatar>
            </div>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="flex gap-4">
          <Avatar className="h-8 w-8 flex-shrink-0">
            <AvatarFallback className="bg-primary text-primary-foreground text-xs">AI</AvatarFallback>
          </Avatar>
          <div className="flex items-center gap-2 text-white">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Thinking...</span>
          </div>
        </div>
      )}
    </div>
  )
}
