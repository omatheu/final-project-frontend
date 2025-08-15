# 🔗 Integração Next.js + API RAG

## 🎯 **Objetivo**

Integrar o frontend Next.js com a API RAG para criar um chat funcional que permite aos usuários fazerem perguntas em linguagem natural sobre dados de telemetria e receberem respostas estruturadas com consultas SQL, resultados e justificativas.

## ✅ **O que foi implementado:**

### **1. API Route Integrada (`/api/chat`)**
- ✅ **Comunicação com API RAG**: Envia mensagens para `http://localhost:8000/query`
- ✅ **Formatação de respostas**: Converte respostas da API RAG em formato legível
- ✅ **Tratamento de erros**: Mensagens específicas para diferentes tipos de erro
- ✅ **Logs detalhados**: Para debugging e monitoramento

### **2. Interface de Chat Melhorada**
- ✅ **Formatação inteligente**: Respostas da API RAG são exibidas em seções organizadas
- ✅ **Sintaxe SQL destacada**: Consultas SQL são exibidas com formatação de código
- ✅ **Ícones contextuais**: Diferentes ícones para SQL, resultados e justificativas
- ✅ **Loading states**: Indicadores visuais durante consultas

### **3. Componentes Atualizados**
- ✅ **ChatArea**: Formatação inteligente para respostas RAG
- ✅ **MessageInput**: Placeholder específico para consultas de telemetria
- ✅ **ExampleQueries**: Exemplos pré-definidos de consultas
- ✅ **Página principal**: Interface adaptada para consultas RAG

### **4. Configuração de Ambiente**
- ✅ **Variáveis de ambiente**: Configuração da URL da API RAG
- ✅ **Fallbacks**: URLs padrão para desenvolvimento

## 🚀 **Como Funciona:**

### **Fluxo de Integração:**
```
1. Usuário digita pergunta → MessageInput
2. Pergunta enviada → API Route (/api/chat)
3. API Route faz requisição → API RAG (localhost:8000/query)
4. API RAG processa → Retorna SQL + Resultado + Justificativa
5. Resposta formatada → ChatArea com formatação inteligente
```

### **Exemplo de Integração:**
```typescript
// 1. Usuário digita: "Qual foi o tempo total de uso do motor por chassi?"

// 2. Frontend envia para API Route
fetch("/api/chat", {
  method: "POST",
  body: JSON.stringify({ message: "Qual foi o tempo total..." })
})

// 3. API Route envia para API RAG
fetch("http://localhost:8000/query", {
  method: "POST",
  body: JSON.stringify({ 
    query: "Qual foi o tempo total..."
  })
})

// 4. API RAG retorna:
{
  "query": "Qual foi o tempo total...",
  "sql_query": "SELECT Chassi, SUM(Valor) as TempoTotal...",
  "result": "Resultado da consulta...",
  "justification": "Explicação da consulta..."
}

// 5. Frontend formata e exibe:
## Consulta SQL Gerada:
```sql
SELECT Chassi, SUM(Valor) as TempoTotal...
```

## Resultado:
Resultado da consulta...

## Justificativa:
Explicação da consulta...
```

## 🔧 **Configuração:**

### **1. Variáveis de Ambiente:**
```bash
# Frontend (.env.local)
NEXT_PUBLIC_RAG_API_URL=http://localhost:8000

# API RAG (.env)
GOOGLE_API_KEY=sua_chave_aqui
```

### **2. URLs de Acesso:**
- **Frontend**: http://localhost:3000
- **API RAG**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs

## 🧪 **Testando a Integração:**

### **1. Verificar se ambos os serviços estão rodando:**
```bash
# Frontend
docker ps | grep visagio-frontend

# API RAG
docker ps | grep visagio-rag-api
```

### **2. Testar comunicação:**
```bash
# Testar API RAG diretamente
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Qual foi o tempo total de uso do motor por chassi?"}'

# Testar API Route do Next.js
curl -X POST "http://localhost:3000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Qual foi o tempo total de uso do motor por chassi?"}'
```

### **3. Testar no navegador:**
1. Acesse http://localhost:3000
2. Clique em "Iniciar Nova Consulta"
3. Digite uma pergunta sobre telemetria
4. Veja a resposta formatada da API RAG

## 📱 **Exemplos de Consultas:**

### **Consultas Básicas:**
- "Qual foi o tempo total de uso do motor por chassi?"
- "Qual a categoria de telemetria mais utilizada?"

### **Consultas Avançadas:**
- "Qual cliente apresenta maior proporção de tempo improdutivo?"
- "É possível identificar equipamentos com manutenção preventiva necessária?"

## 🚨 **Solução de Problemas:**

### **Erro: "Erro de conexão com a API RAG"**
- ✅ Verificar se a API RAG está rodando na porta 8000
- ✅ Verificar se a variável `NEXT_PUBLIC_RAG_API_URL` está configurada
- ✅ Verificar logs da API RAG: `docker logs visagio-project-visagio-rag-api-1`

### **Erro: "GOOGLE_API_KEY não configurada"**
- ✅ Configurar `GOOGLE_API_KEY` no arquivo `.env` da API RAG
- ✅ Reiniciar o container da API RAG

### **Erro: "Banco de dados não encontrado"**
- ✅ Verificar se `Bases_VAI - oficial real.db` está no diretório `RAG/`
- ✅ Verificar se o volume está montado corretamente no Docker

## 🎨 **Personalizações:**

### **1. Adicionar novos tipos de consulta:**
```typescript
// Em components/example-queries.tsx
const exampleQueries = [
  // ... consultas existentes
  {
    icon: <NewIcon className="h-4 w-4" />,
    title: "Nova Consulta",
    query: "Sua nova consulta aqui",
    description: "Descrição da nova consulta"
  }
]
```

### **2. Modificar formatação de respostas:**
```typescript
// Em components/chat-area.tsx
const formatRAGResponse = (content: string) => {
  // Sua lógica de formatação personalizada
}
```

### **3. Adicionar novos endpoints:**
```typescript
// Em app/api/chat/route.ts
// Adicionar lógica para diferentes tipos de consulta
```

## 🔮 **Próximos Passos:**

### **Funcionalidades Futuras:**
- [ ] **Cache de consultas**: Evitar consultas repetidas
- [ ] **Histórico de consultas**: Salvar consultas realizadas
- [ ] **Exportação de resultados**: CSV, PDF, Excel
- [ ] **Gráficos e visualizações**: Charts.js ou Recharts
- [ ] **Autenticação**: Sistema de login para usuários
- [ ] **Rate limiting**: Limitar número de consultas por usuário

### **Melhorias de UX:**
- [ ] **Sugestões inteligentes**: Baseadas em consultas anteriores
- [ ] **Validação de entrada**: Verificar se a pergunta é válida
- [ ] **Feedback visual**: Indicadores de qualidade da resposta
- [ ] **Modo escuro/claro**: Tema personalizável

## 📚 **Recursos Adicionais:**

- **Documentação FastAPI**: https://fastapi.tiangolo.com/
- **Documentação Next.js**: https://nextjs.org/docs
- **LangChain**: https://python.langchain.com/
- **Google Gemini**: https://ai.google.dev/

---

🎉 **Integração completa e funcional!** 

Agora você pode fazer perguntas em linguagem natural sobre seus dados de telemetria e receber respostas estruturadas com consultas SQL, resultados e justificativas. 