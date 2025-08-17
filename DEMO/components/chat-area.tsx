"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ThumbsUp, ThumbsDown, Copy, RotateCcw, Share, Loader2 } from "lucide-react"

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
  const renderMessageContent = (message: Message) => {
    
    if (message.sender === "ai") {
      const lines = message.content.split('\n')
      const elements = []
      let inCodeBlock = false
      let codeContent = []
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        
        if (line.startsWith('```sql')) {
          inCodeBlock = true
          codeContent = []
          continue
        }
        
        if (line === '```' && inCodeBlock) {
          inCodeBlock = false
          // Renderizar o bloco de código completo
          elements.push(
            <pre key={`code-${i}`} className="bg-black/20 p-3 sm:p-4 rounded-lg overflow-x-auto my-2 sm:my-3">
              <code className="text-green-400 text-xs sm:text-sm whitespace-pre-wrap break-words">{codeContent.join('\n')}</code>
            </pre>
          )
          continue
        }
        
        if (inCodeBlock) {
          codeContent.push(line)
          continue
        }
        
        if (line.startsWith('# ')) {
          // Título nível 1
          elements.push(
            <h1 key={i} className="text-2xl sm:text-3xl font-bold text-white mb-3 sm:mb-4 mt-4 sm:mt-6 first:mt-0">
              {line.replace('# ', '')}
            </h1>
          )
        } else if (line.startsWith('## ')) {
          // Título nível 2
          elements.push(
            <h2 key={i} className="text-xl sm:text-2xl font-semibold text-white mb-2 sm:mb-3 mt-3 sm:mt-5">
              {line.replace('## ', '')}
            </h2>
          )
        } else if (line.startsWith('### ')) {
          // Título nível 3
          elements.push(
            <h3 key={i} className="text-lg sm:text-xl font-semibold text-white mb-2 mt-3 sm:mt-4">
              {line.replace('### ', '')}
            </h3>
          )
        } else if (line.startsWith('|') && line.endsWith('|')) {
          // Linha de tabela
          if (line.includes('---')) {
            // Separador de tabela
            elements.push(
              <div key={i} className="border-t border-white/20 my-2"></div>
            )
          } else {
            // Dados da tabela
            const cells = line.split('|').filter(cell => cell.trim())
            const isHeader = elements.length > 0 && elements[elements.length - 1].type === 'div' && 
                           elements[elements.length - 1].props.className.includes('border-t')
            
            elements.push(
              <div key={i} className={`flex flex-col sm:flex-row gap-2 sm:gap-4 py-2 ${isHeader ? 'font-semibold text-white' : 'text-white/90'}`}>
                {cells.map((cell, cellIndex) => (
                  <span key={cellIndex} className="flex-1 text-center px-2 text-sm sm:text-base break-words">
                    {cell.trim()}
                  </span>
                ))}
              </div>
            )
          }
                      } else if (line.trim()) {
          // Renderizar texto normal com suporte a markdown básico
          let processedLine = line
          
          // Processar negrito (**texto**)
          if (line.includes('**')) {
            const parts = line.split('**')
            const elements = []
            
            for (let j = 0; j < parts.length; j++) {
              if (j % 2 === 1) {
                // Texto entre ** (negrito)
                elements.push(
                  <strong key={j} className="font-bold text-white">
                    {parts[j]}
                  </strong>
                )
              } else if (parts[j]) {
                // Texto normal
                elements.push(parts[j])
              }
            }
            
            elements.push(
              <p key={i} className="text-white/90 leading-relaxed mb-2 text-sm sm:text-base px-2 sm:px-0">
                {elements}
              </p>
            )
          } else {
            // Texto normal sem markdown
            elements.push(
              <p key={i} className="text-white/90 leading-relaxed mb-2 text-sm sm:text-base px-2 sm:px-0">
                {line}
              </p>
            )
          }
        }
      } 
      
      return (
        <div className="prose prose-invert max-w-none px-2 sm:px-0">
          {elements}
      </div>
    )
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
    <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-4 sm:space-y-6">
      {messages.map((message) => (
        <div key={message.id} className="flex gap-2 sm:gap-4">
          {message.sender === "ai" && (
            <Avatar className="h-6 w-6 sm:h-8 sm:w-8 flex-shrink-0">
              <AvatarFallback className="bg-primary text-primary-foreground text-xs">AI</AvatarFallback>
            </Avatar>
          )}

          <div className="flex-1 space-y-2">
            {renderMessageContent(message)}

            {message.sender === "ai" && (
              <div className="flex items-center gap-1 sm:gap-2 mt-2 sm:mt-3">
                <Button variant="ghost" size="sm" className="h-6 w-6 sm:h-8 sm:w-8 p-0 text-white/80 hover:text-white">
                  <ThumbsUp className="h-2 w-2 sm:h-3 sm:w-3" />
                </Button>
                <Button variant="ghost" size="sm" className="h-6 w-6 sm:h-8 sm:w-8 p-0 text-white/80 hover:text-white">
                  <ThumbsDown className="h-2 w-2 sm:h-3 sm:w-3" />
                </Button>
                <Button variant="ghost" size="sm" className="h-6 w-6 sm:h-8 sm:w-8 p-0 text-white/80 hover:text-white">
                  <Copy className="h-2 w-2 sm:h-3 sm:w-3" />
                </Button>
                <Button variant="ghost" size="sm" className="h-6 w-6 sm:h-8 sm:w-8 p-0 text-white/80 hover:text-white">
                  <RotateCcw className="h-2 w-2 sm:h-3 sm:w-3" />
                </Button>
                <Button variant="ghost" size="sm" className="h-6 w-6 sm:h-8 sm:w-8 p-0 text-white/80 hover:text-white">
                  <Share className="h-2 w-2 sm:h-3 sm:w-3" />
                </Button>
              </div>
            )}
          </div>

          {message.sender === "user" && (
            <div className="flex items-center gap-1 sm:gap-2">
              <div className="text-xs text-white">6/75</div>
              <Avatar className="h-6 w-6 sm:h-8 sm:w-8 flex-shrink-0">
                <AvatarImage src="/placeholder.svg?height=32&width=32" />
                <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">U</AvatarFallback>
              </Avatar>
            </div>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="flex gap-2 sm:gap-4">
          <Avatar className="h-6 w-6 sm:h-8 sm:w-8 flex-shrink-0">
            <AvatarFallback className="bg-primary text-primary-foreground text-xs">AI</AvatarFallback>
          </Avatar>
          <div className="flex items-center gap-2 text-white">
            <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
            <span className="text-sm sm:text-base">Consultando dados de telemetria...</span>
          </div>
        </div>
      )}
    </div>
  )
}
