"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatArea } from "@/components/chat-area"
import { MessageInput } from "@/components/message-input"
import { ExampleQueries } from "@/components/example-queries"

export interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
  ragData?: any // Dados da API RAG
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
      title: "Nova Consulta RAG",
      messages: [],
      timestamp: new Date(),
    }

    setChats((prev) => [newChat, ...prev])
    setCurrentChat(newChatId)
  }

  const handleQuerySelect = (query: string) => {
    handleSendMessage(query)
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
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `Erro HTTP: ${response.status}`)
      }

      const data = await response.json()

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        sender: "ai",
        timestamp: new Date(),
        ragData: data.ragData, // Incluir dados da API RAG
      }

      setChats((prev) =>
        prev.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                messages: [...chat.messages, aiMessage],
                title:
                  chat.title === "Nova Consulta RAG" ? content.slice(0, 50) + (content.length > 50 ? "..." : "") : chat.title,
                lastMessage: data.response,
                timestamp: new Date(),
              }
            : chat,
        ),
      )
    } catch (error) {
      console.error("Error sending message:", error)
      
      let errorMessage = "Desculpe, encontrei um erro. Tente novamente."
      
      if (error instanceof Error) {
        if (error.message.includes('API RAG')) {
          errorMessage = "Erro de conexão com a API RAG. Verifique se o serviço está rodando na porta 8000."
        } else if (error.message.includes('fetch')) {
          errorMessage = "Erro de conexão. Verifique se a API RAG está rodando."
        } else {
          errorMessage = `Erro: ${error.message}`
        }
      }
      
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        content: errorMessage,
        sender: "ai",
        timestamp: new Date(),
      }

      setChats((prev) =>
        prev.map((chat) => (chat.id === chatId ? { ...chat, messages: [...chat.messages, errorMsg] } : chat)),
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
          <div className="flex-1 flex flex-col">
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="text-6xl mb-4">🔍</div>
                <h1 className="text-2xl font-semibold mb-2 text-foreground">Visagio RAG Chat</h1>
                <p className="text-muted-foreground mb-6">
                  Faça perguntas sobre dados de telemetria em linguagem natural. 
                  O sistema irá gerar consultas SQL e retornar insights dos seus dados.
                </p>
                <button
                  onClick={handleNewChat}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                >
                  Iniciar Nova Consulta
                </button>
              </div>
            </div>
            <ExampleQueries onQuerySelect={handleQuerySelect} />
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
