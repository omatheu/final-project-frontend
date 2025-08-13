"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { FileText, MessageSquare, Plus, Search, Sparkles } from "lucide-react"

interface Chat {
  id: string
  title: string
  lastMessage?: string
  timestamp: Date
}

interface SidebarProps {
  currentChat: string | null
  chats: Chat[]
  onChatSelect: (chatId: string) => void
  onNewChat: () => void
}

const navigationItems = [
  { icon: MessageSquare, label: "Chats", id: "chats" },
]

export function Sidebar({ currentChat, chats, onChatSelect, onNewChat }: SidebarProps) {
  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center gap-2 mb-4">
          <div className="text-xl font-bold text-sidebar-foreground">DEMO</div>
          <div className="flex items-center gap-1 ml-auto">
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-white/80 hover:text-white">
              <FileText className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-white/80 hover:text-white">
              <Search className="h-3 w-3" />
            </Button>
          </div>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search"
            className="pl-9 bg-sidebar-accent border-sidebar-border text-sidebar-foreground placeholder:text-muted-foreground"
          />
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          {navigationItems.map((item) => (
            <Button
              key={item.id}
              variant="ghost"
              className="w-full justify-start gap-3 text-sidebar-foreground hover:bg-sidebar-accent mb-1"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Button>
          ))}
        </div>

        {/* Chats Section */}
        <div className="px-2 py-4">
          <div className="flex items-center justify-between mb-2 px-2">
            <div className="text-xs font-medium text-muted-foreground">Chats</div>
            <Button variant="ghost" size="sm" onClick={onNewChat} className="h-6 w-6 p-0 hover:bg-sidebar-accent text-white/80 hover:text-white">
              <Plus className="h-3 w-3" />
            </Button>
          </div>

          {chats.length === 0 ? (
            <div className="px-2 py-8 text-center">
              <MessageSquare className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
              <p className="text-xs text-muted-foreground">No chats yet</p>
              <p className="text-xs text-muted-foreground/70 mt-1">Start a conversation to create your first chat</p>
            </div>
          ) : (
            chats.map((chat) => (
              <Button
                key={chat.id}
                variant="ghost"
                onClick={() => onChatSelect(chat.id)}
                className={cn(
                  "w-full justify-start gap-3 text-sidebar-foreground hover:bg-sidebar-accent mb-1 text-left",
                  currentChat === chat.id && "bg-sidebar-accent",
                )}
              >
                <MessageSquare className="h-4 w-4 flex-shrink-0" />
                <span className="truncate">{chat.title}</span>
              </Button>
            ))
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <Button className="w-full justify-start gap-2 bg-sidebar-primary hover:bg-sidebar-primary/90 text-sidebar-primary-foreground">
          <Sparkles className="h-4 w-4" />
          DEMO app
        </Button>
      </div>
    </div>
  )
}
