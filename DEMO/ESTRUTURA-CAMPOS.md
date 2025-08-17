# 🎯 Estrutura dos Campos SQL_QUERY e JUSTIFICATION

## ✨ Campos do Backend Implementados

A API agora retorna uma resposta estruturada com os campos específicos do backend:

### 1. **Campo `sql_query`**
- **O que é**: A consulta SQL gerada pela IA
- **Como é exibido**: Em um bloco de código formatado
- **Localização**: Seção "## Código SQL"

### 2. **Campo `justification`**
- **O que é**: O processo de pensamento da IA
- **Como é exibido**: Em uma seção separada
- **Localização**: Seção "## Justificativa"

## 🏗️ Estrutura da Resposta

```
# Consulta SQL Gerada

## Código SQL
```sql
SELECT Chassi, SUM(Valor) AS Tempo_Total_Uso_Motor_Horas
FROM Telemetria
WHERE Categoria = 'Uso do Motor' AND Serie != 'Chave-Ligada'
GROUP BY Chassi;
```

## Justificativa

[Processo de pensamento da AI - campo justification]

## Resultados

| Chassi | Tempo_Total_Uso_Motor_Horas |
|--------|-----------------------------|
| 20382  | 516.3107941666659           |
| 20396  | 5.364380555555547           |
...
```

## 🔧 Lógica de Implementação

### **Prioridade dos Campos**
1. **`sql_query`** - Sempre exibido primeiro (campo obrigatório)
2. **`justification`** - Exibido se disponível (campo opcional)
3. **`result`** - Exibido apenas se não duplicar o sql_query

### **Limpeza de Duplicação**
- **Justificativa**: Remove seções "### Consulta:" e "### Resposta:" se existirem
- **Resultados**: Extrai apenas dados de tabela, evitando duplicação do SQL
- **Verificação**: Confirma que o conteúdo não está duplicado antes de exibir

## 📱 Como o Frontend Renderiza

O frontend recebe a resposta já formatada em markdown e a renderiza usando:
- **Títulos**: Diferentes níveis (#, ##, ###) com estilos responsivos
- **Código SQL**: Blocos de código com formatação adequada
- **Tabelas**: Renderização responsiva com layout adaptativo
- **Texto**: Parágrafos bem espaçados e legíveis

## 🎉 Benefícios da Nova Estrutura

1. **✅ Campos específicos**: sql_query e justification claramente separados
2. **✅ Sem duplicação**: Cada campo aparece apenas uma vez
3. **✅ Organização clara**: Estrutura hierárquica bem definida
4. **✅ Flexibilidade**: Funciona mesmo se algum campo estiver ausente
5. **✅ Manutenibilidade**: Código limpo e fácil de entender

## 🔍 Como Testar

1. **Envie uma consulta** no frontend
2. **Verifique se aparecem**:
   - Título "Consulta SQL Gerada"
   - Seção "Código SQL" com a consulta
   - Seção "Justificativa" com o processo de pensamento
   - Seção "Resultados" com os dados (se disponível)
3. **Confirme que não há duplicação** de conteúdo
4. **Teste a responsividade** em diferentes tamanhos de tela 