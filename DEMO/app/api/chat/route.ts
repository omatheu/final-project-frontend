export async function POST(req: Request) {
  try {
    const { message } = await req.json()
    
    // Usar o nome do container Docker para comunicação interna
    const ragApiUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://visagio-rag-api:8000'
    
    console.log(`Enviando mensagem para API RAG: ${ragApiUrl}/query`)
    console.log(`Mensagem: ${message}`)
    
    const response = await fetch(`${ragApiUrl}/query`, {
      method: "POST",
      headers: {
        "accept": "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: message
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`API RAG error: ${response.status} - ${errorText}`)
      throw new Error(`API RAG error: ${response.status}`)
    }

    const data = await response.json()
    console.log('Resposta da API RAG:', data)

    let formattedResponse = ""
    if (data.sql_query && data.result) {
      formattedResponse = `## 🔍 **Consulta Realizada**
**Pergunta:** ${data.query}

## 💻 **Consulta SQL Gerada**
\`\`\`sql
${data.sql_query}
\`\`\`

## 📊 **Resultado**
${data.result}

## 💡 **Justificativa**
${data.justification}

## ⏱️ **Informações Técnicas**
- **Tempo de execução:** ${data.execution_time?.toFixed(2)}s
- **Timestamp:** ${data.timestamp ? new Date(data.timestamp).toLocaleString('pt-BR') : 'N/A'}`
    } else if (data.error) {
      formattedResponse = `❌ **Erro na Consulta**
${data.error}`
    } else {
      formattedResponse = data.result || "Desculpe, não consegui processar sua consulta."
    }

    return Response.json({
      response: formattedResponse,
      ragData: data
    })
  } catch (error) {
    console.error("Error in chat API:", error)
    
    if (error instanceof Error && error.message.includes('fetch')) {
      return Response.json({
        error: "Erro de conexão com a API RAG. Verifique se o serviço está rodando."
      }, { status: 503 })
    }
    
    return Response.json({
      error: "Erro interno do servidor"
    }, { status: 500 })
  }
}
