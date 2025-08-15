"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ThumbsUp, ThumbsDown, Copy, RotateCcw, Share, Loader2, Database, Code, Lightbulb, Clock, Calendar } from "lucide-react"

interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
  ragData?: any // Dados adicionais da API RAG
}

interface ChatAreaProps {
  messages: Message[]
  isLoading?: boolean
}

export function ChatArea({ messages, isLoading }: ChatAreaProps) {
  const formatRAGResponse = (content: string) => {
    // Dividir o conteúdo em seções baseadas em ##
    const sections = content.split('## ')
    
    return (
      <div className="space-y-6">
        {sections.map((section, index) => {
          if (!section.trim()) return null
          
          const [title, ...contentParts] = section.split('\n')
          const content = contentParts.join('\n').trim()
          
          if (!title) return null
          
          let icon = <Lightbulb className="h-4 w-4" />
          let bgColor = "bg-blue-500/10"
          let borderColor = "border-blue-500/20"
          let titleColor = "text-blue-400"
          
          if (title.toLowerCase().includes('sql') || title.toLowerCase().includes('consulta sql')) {
            icon = <Code className="h-4 w-4" />
            bgColor = "bg-green-500/10"
            borderColor = "border-green-500/20"
            titleColor = "text-green-400"
          } else if (title.toLowerCase().includes('resultado')) {
            icon = <Database className="h-4 w-4" />
            bgColor = "bg-purple-500/10"
            borderColor = "border-purple-500/20"
            titleColor = "text-purple-400"
          } else if (title.toLowerCase().includes('justificativa')) {
            icon = <Lightbulb className="h-4 w-4" />
            bgColor = "bg-yellow-500/10"
            borderColor = "border-yellow-500/20"
            titleColor = "text-yellow-400"
          } else if (title.toLowerCase().includes('técnicas') || title.toLowerCase().includes('execução')) {
            icon = <Clock className="h-4 w-4" />
            bgColor = "bg-gray-500/10"
            borderColor = "border-gray-500/20"
            titleColor = "text-gray-400"
          } else if (title.toLowerCase().includes('realizada')) {
            icon = <Calendar className="h-4 w-4" />
            bgColor = "bg-indigo-500/10"
            borderColor = "border-indigo-500/20"
            titleColor = "text-indigo-400"
          }
          
          return (
            <div key={index} className={`${bgColor} ${borderColor} border rounded-lg p-4`}>
              <div className="flex items-center gap-2 mb-3">
                {icon}
                <h4 className={`font-semibold ${titleColor}`}>{title}</h4>
              </div>
              <div className="text-white/90">
                {content.startsWith('```sql') ? (
                  <pre className="bg-black/20 p-3 rounded overflow-x-auto">
                    <code className="text-green-400">{content.replace(/```sql\n?|\n?```/g, '')}</code>
                  </pre>
                ) : content.includes('**') ? (
                  // Renderizar markdown básico
                  <div className="space-y-2">
                    {content.split('\n').map((line, lineIndex) => {
                      if (line.includes('**')) {
                        // Renderizar texto em negrito
                        const parts = line.split('**')
                        return (
                          <p key={lineIndex} className="mb-2 leading-relaxed">
                            {parts.map((part, partIndex) => 
                              partIndex % 2 === 1 ? 
                                <strong key={partIndex} className="text-white font-semibold">{part}</strong> : 
                                part
                            )}
                          </p>
                        )
                      } else if (line.startsWith('- ')) {
                        // Renderizar listas
                        return (
                          <div key={lineIndex} className="flex items-start gap-2 mb-2">
                            <span className="text-white/60 mt-1">•</span>
                            <span className="text-white/90">{line.substring(2)}</span>
                          </div>
                        )
                      } else if (line.trim()) {
                        return (
                          <p key={lineIndex} className="mb-2 leading-relaxed">
                            {line}
                          </p>
                        )
                      }
                      return null
                    })}
                  </div>
                ) : (
                  content.split('\n').map((line, lineIndex) => (
                    <p key={lineIndex} className="mb-2 leading-relaxed">
                      {line}
                    </p>
                  ))
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  const renderMessageContent = (message: Message) => {
    if (message.sender === "ai" && message.content.includes('## ')) {
      return formatRAGResponse(message.content)
    }
    
    return (
      <div className="prose prose-invert max-w-none">
        {message.content.split("\n").map((line, index) => (
          <p key={index} className="text-white leading-relaxed mb-2">
            {line}
          </p>
        ))}
      </div>
    )
  }

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
            {renderMessageContent(message)}

            {message.sender === "ai" && (
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
            <span>Consultando dados de telemetria...</span>
          </div>
        </div>
      )}
    </div>
  )
}
