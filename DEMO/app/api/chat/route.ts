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
    
    // Verificar se é um erro (sql_query contém mensagem de erro ou result contém ERRO)
    if (data.sql_query === "Consulta não encontrada na resposta" || data.result?.includes("**ERRO:**")) {
      formattedResponse = `# ❌ Erro na Consulta
      
${data.result || "Desculpe, não consegui processar sua consulta."}`
      
      // Adicionar justificativa se disponível e diferente do padrão
      if (data.justification && data.justification !== "Processo de análise da consulta") {
        formattedResponse += `

## Justificativa

${data.justification}`
      }
      
      // Adicionar informações de execução mesmo em caso de erro
      if (data.execution_time !== undefined) {
        formattedResponse += `

## Informações de Execução

**Tempo de execução:** ${data.execution_time.toFixed(3)} segundos`
      }
      
      if (data.timestamp) {
        const timestamp = new Date(data.timestamp)
        const formattedTime = timestamp.toLocaleString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
        
        formattedResponse += `
**Timestamp:** ${formattedTime}`
      }
    } else if (data.sql_query && data.sql_query !== "Consulta não encontrada na resposta") {
      // Caso de sucesso - consulta SQL válida
      formattedResponse = `# Consulta SQL Gerada
      
## Código SQL
\`\`\`sql
${data.sql_query}
\`\`\``
      
      // Adicionar justificativa se disponível e diferente do padrão
      if (data.justification && data.justification !== "Processo de análise da consulta") {
        formattedResponse += `

## Justificativa

${data.justification}`
      }
      
      // Adicionar resultados se disponível e não for erro
      if (data.result && !data.result.includes("**ERRO:**")) {
        // Verificar se o result já contém dados de tabela
        if (data.result.includes('| Chassi |') || data.result.includes('|--------|')) {
          // Extrair apenas os dados da tabela se existirem
          if (data.result.includes('| Chassi |')) {
            const tableStart = data.result.indexOf('| Chassi |')
            const tableEnd = data.result.indexOf('\n\n', tableStart)
            
            if (tableStart !== -1) {
              const tableData = tableEnd !== -1 
                ? data.result.substring(tableStart, tableEnd)
                : data.result.substring(tableStart)
              
              formattedResponse += `

## Resultados

${tableData}`
            }
          } else {
            // Se não for tabela específica, mostrar o result completo
            formattedResponse += `

## Resultados

${data.result}`
          }
        } else {
          // Se não for tabela, mostrar o result completo
          formattedResponse += `

## Resultados

${data.result}`
        }
      }
      
      // Adicionar informações de execução
      if (data.execution_time !== undefined) {
        formattedResponse += `

## Informações de Execução

**Tempo de execução:** ${data.execution_time.toFixed(3)} segundos`
      }
      
      if (data.timestamp) {
        const timestamp = new Date(data.timestamp)
        const formattedTime = timestamp.toLocaleString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
        
        formattedResponse += `
**Timestamp:** ${formattedTime}`
      }
    } else {
      // Fallback para outros casos
      formattedResponse = `# Resposta
      
${data.result || "Desculpe, não consegui processar sua consulta."}`
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
