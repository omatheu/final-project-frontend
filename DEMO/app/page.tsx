"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatArea } from "@/components/chat-area"
import { MessageInput } from "@/components/message-input"

export interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
}

interface Chat {
  id: string
  title: string
  messages: Message[]
  lastMessage?: string
  timestamp: Date
}

export default function Home() {
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChat, setCurrentChat] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const currentChatData = chats.find((chat) => chat.id === currentChat)

  const handleNewChat = () => {
    const newChatId = `chat-${Date.now()}`
    const newChat: Chat = {
      id: newChatId,
      title: "New Chat",
      messages: [],
      timestamp: new Date(),
    }

    setChats((prev) => [newChat, ...prev])
    setCurrentChat(newChatId)
  }

  const handleSendMessage = async (content: string) => {
    let chatId = currentChat

    if (!chatId) {
      chatId = `chat-${Date.now()}`
      const newChat: Chat = {
        id: chatId,
        title: content.slice(0, 50) + (content.length > 50 ? "..." : ""),
        messages: [],
        timestamp: new Date(),
      }
      setChats((prev) => [newChat, ...prev])
      setCurrentChat(chatId)
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: "user",
      timestamp: new Date(),
    }

    setChats((prev) =>
      prev.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              messages: [...chat.messages, userMessage],
              lastMessage: content,
              timestamp: new Date(),
            }
          : chat,
      ),
    )

    setIsLoading(true)

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content }),
      })

      if (!response.ok) {
        throw new Error("Failed to send message")
      }

      const data = await response.json()

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        sender: "ai",
        timestamp: new Date(),
      }

      setChats((prev) =>
        prev.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                messages: [...chat.messages, aiMessage],
                title:
                  chat.title === "New Chat" ? content.slice(0, 50) + (content.length > 50 ? "..." : "") : chat.title,
                lastMessage: data.response,
                timestamp: new Date(),
              }
            : chat,
        ),
      )
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error. Please try again.",
        sender: "ai",
        timestamp: new Date(),
      }

      setChats((prev) =>
        prev.map((chat) => (chat.id === chatId ? { ...chat, messages: [...chat.messages, errorMessage] } : chat)),
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-background dark">
      <Sidebar currentChat={currentChat} chats={chats} onChatSelect={setCurrentChat} onNewChat={handleNewChat} />
      <div className="flex-1 flex flex-col">
        {!currentChat ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="text-6xl mb-4">💬</div>
              <h1 className="text-2xl font-semibold mb-2 text-foreground">Welcome to DEMO</h1>
              <p className="text-muted-foreground mb-6">Start a conversation with AI to create your first chat</p>
              <button
                onClick={handleNewChat}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                Start New Chat
              </button>
            </div>
          </div>
        ) : (
          <>
            <ChatArea messages={currentChatData?.messages || []} isLoading={isLoading} />
            <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          </>
        )}
      </div>
    </div>
  )
}
