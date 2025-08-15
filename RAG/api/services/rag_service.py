import time
import pandas as pd
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from langchain.agents import ZeroShotAgent
from langchain.agents.agent import AgentExecutor
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.chains import LLMMathChain
from langchain.agents import Tool

from config.settings import settings
import os
from datetime import datetime

def simple_similarity(str1: str, str2: str) -> float:
    """Função simples de similaridade para substituir jellyfish temporariamente"""
    str1_lower = str1.lower()
    str2_lower = str2.lower()
    
    if str1_lower == str2_lower:
        return 1.0
    
    # Contar palavras em comum
    words1 = set(str1_lower.split())
    words2 = set(str2_lower.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

class RAGService:
    """Serviço para gerenciar consultas RAG usando LangChain e Gemini"""
    
    def __init__(self):
        self.db = None
        self.agent_executor = None
        self.llm = None
        self.df_consultas_validadas = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa o serviço RAG"""
        try:
            # Configurar o LLM
            if not settings.google_api_key:
                raise ValueError("GOOGLE_API_KEY não configurada")
            
            os.environ['GOOGLE_API_KEY'] = settings.google_api_key
            self.llm = ChatGoogleGenerativeAI(
                model=settings.model_name, 
                temperature=settings.temperature
            )
            
            # Conectar ao banco
            self._connect_database()
            
            # Carregar consultas validadas (se existir)
            self._load_validated_queries()
            
            # Inicializar o agente
            self._initialize_agent()
            
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar serviço RAG: {str(e)}")
    
    def _connect_database(self):
        """Conecta ao banco de dados SQLite"""
        try:
            db_path = Path(settings.database_path)
            if not db_path.exists():
                raise FileNotFoundError(f"Banco de dados não encontrado: {db_path}")
            
            self.db = SQLDatabase.from_uri(f'sqlite:///{db_path}')
            
        except Exception as e:
            raise RuntimeError(f"Erro ao conectar ao banco: {str(e)}")
    
    def _load_validated_queries(self):
        """Carrega consultas validadas (opcional)"""
        try:
            # Por enquanto, vamos usar um DataFrame vazio
            # Em produção, você pode carregar de um arquivo Excel ou banco
            self.df_consultas_validadas = pd.DataFrame(columns=['Pedido', 'Consulta'])
        except Exception as e:
            print(f"Aviso: Não foi possível carregar consultas validadas: {e}")
            self.df_consultas_validadas = pd.DataFrame(columns=['Pedido', 'Consulta'])
    
    def _get_system_prompt(self, query: str) -> str:
        """Gera o prompt do sistema baseado na consulta"""
        shots = self._get_similar_shots(query)
        
        system_prompt = f"""
Você é um sistema especialista em escrever consultas SQLite a partir de descrições textuais. Seu papel é
interpretar um pedido do usuário sobre alguma informação dedutível de um banco de dados fornecido, identificando
o objetivo da consulta e elementos do esquema físico que devem ser utilizados. Usando essas informações, você
deve elaborar uma consulta SQLite SINTATICAMENTE e SEMANTICAMENTE válida para aquele fim, visando concisão, eficiência
e clareza (use nomes descritivos nas colunas das tabelas resultantes). Você precisa ter CERTEZA ABSOLUTA de que a consulta
sugerida cumpre os seguintes requisitos:

- É sintaticamente correta (não contém erros sintáticos de SQLite)
- Usa tabelas e campos que existem no esquema do banco de dados
- É semanticamente correta (retorna EXATAMENTE o que o usuário pediu, sem sobras e faltas)
- NÃO faz modificações no banco de dados (se baseia inteiramente em cláusulas 'SELECT')

SOMENTE depois de verificar a consulta gerada quanto aos critérios elencados, você deve consultar o banco de dados
(via a ferramenta correspondente) usando a consulta validada. Sua resposta final ('Final Answer') deve conter tanto
o trecho de código SQLite para a consulta quanto o resultado dela, além de sua justificativa, em formato de dado (número,
string, tabela) compatível com o identificado no pedido do usuário. A formatação da resposta final deve ser (trechos entre
parênteses angulados '<<>>' são placeholders):

---

Final Answer:

### Consulta:
```sql
<<consulta SQLite VALIDADA, em pretty-print>>
```

### Resposta:
<<resultado obtido da consulta feita, em formato de dado condizente com o objetivo do usuário e mais simples possível>>

### Justificativa:
<<explicação da relação entre a pergunta e a consulta gerada, explicitando suposições feitas no processo>>

---

Existem dois casos de pedidos de usuário que você NÃO deve atender (e retornar imediatamente):

- Pedidos que não têm relação com o banco de dados
- Pedidos que envolvem modificação do banco de dados (inclusão, exclusão e alteração de elementos)

Se o pedido do usuário se encontrar em um dos dois casos acima, retorne imediatamente a resposta final no seguinte formato:

---

Final Answer:

**ERRO:** <<justificativa para o lançamento do erro>>

---

O banco de dados que você usará consiste de dados de telemetria de uma empresa locadora de maquinário agrícola. As perguntas
feitas para você serão realizadas por analistas de dados da empresa que buscam elaborar relatórios informativos eficientes
para a gerência e os clientes. Segue o esquema físico do banco de dados da empresa:

```sql
-- Tabela relacionando dados de clientes e seus contratos de locação de veículos
CREATE TABLE Chassis (
  Chassi INTEGER, -- ID do chassi
  Contrato INTEGER, -- ID do contrato
  Cliente INTEGER, -- ID do cliente
  Modelo INTEGER -- ID do modelo
);

-- Tabela contendo dados diários dos veículos obtidos por sensores
CREATE TABLE Telemetria (
  Chassi INTEGER, -- ID do chassi
  UnidadeMedida TEXT, -- Unidade de medida do valor descrito no campo Valor ('l' para litros ou 'hr' para horas)
  Categoria TEXT, -- Nome da categoria da informação sensoriada
  Data TIMESTAMP, -- Data e hora de captação do dado
  Serie TEXT, -- Nome da subcategoria do tipo de dado sensoriado pelo sensor
  Valor REAL -- Valor capturado pelo sensor, medido na UnidadeMedida, sobre a informação descrita pela Categoria e Serie
);
```

Além disso, temos a caracterização do conjunto de valores assumidos pelos campos de Categoria e Serie. As categorias são
expressas pelas strings nos tópicos principais e as séries, nas strings dos subtópicos (cada uma é descrita pelos comentários
entre colchetes e em itálico):

- Uso do Motor _[Tempo (em horas 'hr') em cada status de motor]_
  - Chave-Ligada _[Motor desligado]_
  - Marcha Lenta _[Motor ligado, mas improdutivo]_
  - Carga Baixa _[Motor ligado, mas com baixo uso]_
  - Carga Média _[Motor ligado com uso regular]_
  - Carga Alta _[Motor ligado com uso intenso]_
- Uso do Combustível do Motor _[Consumo de combustível (em litros 'l') em cada status de motor]_
  - Chave-Ligada _[Motor desligado]_
  - Marcha Lenta _[Motor ligado, mas improdutivo]_
  - Carga Baixa _[Motor ligado, mas com baixo uso]_
  - Carga Média _[Motor ligado com uso regular]_
  - Carga Alta _[Motor ligado com uso intenso]_
- Uso da Configuração do Modo do Motor _[Tempo (em horas 'hr') em cada configuração de motor]_
  - HP _[Modo de Alta Potência]_
  - P _[Modo Padrão]_
  - E _[Modo Econômico]_

Antes de pensar em qualquer consulta, verifique se é possível extrair elementos desse esquema físico do pedido do usuário.
Lembre-se que o seu papel é ajudar no processo de extração de dados do banco da empresa, e que você deve ser capaz tanto
de raciocinar sobre os pedidos quanto de escrever consultas SQLite efetivas e bem explicadas. Serão humanos os principais
consumidores de suas respostas.

---

Se você precisar supor métricas e critérios para responder ao pedido do usuário, você pode realizar consultas auxiliares ao
banco de dados para embasar suas escolhas (ex.: se for necessário, você pode calcular a média de algum campo numérico para
usá-lo como critério). Essas escolhas DEVEM ser explicadas na justificativa, incluindo o porquê de ter feito a escolha e
como ela foi feita/calculada.

Você DEVE escrever o seu raciocínio passo-a-passo no campo 'Thought' designado. Somente retorne a resposta final depois que
tiver feito a consulta no banco de dados. Quando quiser retornar a resposta final, inclua o campo 'Final Answer' com a
resposta final no formato exigido, contendo a consulta, a resposta e a justificativa. A consulta SQLite na resposta final
deve estar escrita em pretty-print. SEMPRE converta o formato do resultado da resposta final de acordo com o que foi pedido
originalmente pelo usuário (ex.: se a resposta para o pedido for uma lista de valores, escreva a resposta final como uma
tabela Markdown; se for um número, escreva como um número). Se a resposta definitiva for em formato de tabela, USE a notação
Markdown para descrevê-la. Caso contrário, se a resposta para a pergunta do usuário puder ser descrita usando um único valor
(numérico ou string), preencha o campo 'Action Input' em conformidade.

Para realizar essas tarefas, você tem acesso a um conjunto de ferramentas. Para usar alguma, você deve dizer
explicitamente porque você quer invocar aquela ferramenta e qual o nome da ferramenta a ser invocada. Será
fornecida uma lista com os nomes e descrições de cada uma das ferramentas disponíveis, na qual você deve se
basear ao fazer uma chamada. Caso não tenha a resposta imediata para alguma questão, USE a respectiva ferramenta
para sua obtenção. NUNCA alucine respostas. NUNCA preencha o campo 'Action Input' com blocos Markdown.

{shots}

---
A formatação do output deve ser da seguinte maneira (parênteses angulados '<<>>' são placeholders, colchetes são comentários):
⚠️ Atenção: o output DEVE seguir o formato ReAct:
---
[USE TODOS OS CAMPOS LISTADOS ABAIXO EM TODAS AS SUAS RESPOSTAS]

Thought: <<mensagem que SEMPRE DEVE ser conter TODO o seu raciocínio>>
Action: <<nome da ferramenta, ex: sql_db_list_tables>>
Action Input: <<input da ferramenta>>

[ESTE CAMPO É OPCIONAL]

Final Answer: <<se quiser encerrar, use este campo como resposta final>>
"""
        
        return system_prompt.format(shots=shots)
    
    def _get_similar_shots(self, query: str) -> str:
        """Obtém exemplos similares de consultas"""
        if self.df_consultas_validadas.empty:
            return ""
        
        shots = ""
        for idx, linha in self.df_consultas_validadas.iterrows():
            if simple_similarity(linha['Pedido'], query) > settings.similarity_threshold:
                shots += f"""
---
**PEDIDO DO USUÁRIO:** {linha['Pedido']}

**CONSULTA GERADA:**
```sql
{linha['Consulta']}
```
"""
        
        if shots:
            shots = """Eis alguns exemplos de conversões de pedidos para consultas SQLite bem-sucedidas:
---
""" + shots
        
        return shots
    
    def _initialize_agent(self):
        """Inicializa o agente RAG"""
        try:
            print("🔧 Inicializando agente RAG...")
            
            # Configurar o modelo Gemini
            print("📝 Configurando modelo Gemini...")
            llm = ChatGoogleGenerativeAI(
                model=settings.model_name,
                google_api_key=settings.google_api_key,
                temperature=0.1,
                max_output_tokens=2048
            )
            print("✅ Modelo Gemini configurado")
            
            # Configurar ferramentas
            print("🔧 Configurando ferramentas...")
            toolkit = SQLDatabaseToolkit(db=self.db, llm=llm)
            tools = toolkit.get_tools()
            print(f"✅ {len(tools)} ferramentas configuradas")
            
            # Configurar o agente
            print("🤖 Configurando agente...")
            prompt = ZeroShotAgent.create_prompt(
                tools,
                prefix=self._get_system_prompt(""),
                suffix="",
                input_variables=["input", "agent_scratchpad"]
            )
            print("✅ Prompt configurado")
            
            # Criar o agente
            print("🔗 Criando agente...")
            self.agent = ZeroShotAgent(
                llm_chain=LLMChain(llm=llm, prompt=prompt),
                allowed_tools=[tool.name for tool in tools],
                verbose=True
            )
            print("✅ Agente criado")
            
            # Criar o executor
            print("⚙️ Configurando executor...")
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self.agent,
                tools=tools,
                verbose=True,
                max_iterations=5,
                handle_parsing_errors=True
            )
            print("✅ Executor configurado")
            
        except Exception as e:
            print(f"❌ Erro detalhado na inicialização: {str(e)}")
            print(f"   Tipo do erro: {type(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Erro ao inicializar agente: {str(e)}")
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """Executa uma consulta usando o agente RAG"""
        start_time = time.time()
        
        try:
            print(f"🔍 Executando consulta: {query_text}")
            print(f"🔧 Agente configurado: {self.agent_executor is not None}")
            
            if not self.agent_executor:
                raise RuntimeError("Agente não foi inicializado corretamente")
            
            # Executar a consulta real
            print("🚀 Invocando agente...")
            try:
                response = self.agent_executor.invoke({
                    "input": query_text,
                    "agent_scratchpad": ""
                })
                print(f"✅ Resposta do agente recebida: {type(response)}")
                print(f"📝 Conteúdo da resposta: {response}")
            except Exception as agent_error:
                print(f"❌ Erro na invocação do agente: {str(agent_error)}")
                print(f"   Tipo do erro: {type(agent_error)}")
                import traceback
                print(f"   Traceback do agente: {traceback.format_exc()}")
                raise agent_error
            
            execution_time = time.time() - start_time
            
            # Extrair informações da resposta
            output = response.get("output", "")
            print(f"📤 Output extraído: {output[:200]}...")
            
            # Tentar extrair a consulta SQL e resultado
            sql_query, result, justification = self._parse_agent_response(output)
            
            return {
                "query": query_text,
                "sql_query": sql_query,
                "result": result,
                "justification": justification,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "raw_response": output
            }
            
        except Exception as e:
            print(f"❌ Erro na execução da consulta: {str(e)}")
            print(f"   Tipo do erro: {type(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Erro na execução da consulta: {str(e)}")
    
    def _parse_agent_response(self, output: str) -> tuple:
        """Extrai informações estruturadas da resposta do agente"""
        try:
            print(f"🔍 Parsing resposta do agente: {output[:200]}...")
            
            # Buscar pela consulta SQL
            sql_query = "Consulta não encontrada na resposta"
            if "```sql" in output and "```" in output:
                sql_start = output.find("```sql") + 6
                sql_end = output.find("```", sql_start)
                if sql_end > sql_start:
                    sql_query = output[sql_start:sql_end].strip()
            
            # Buscar pela resposta
            result = "Resultado não encontrado na resposta"
            if "### Resposta:" in output:
                response_start = output.find("### Resposta:") + 13
                response_end = output.find("###", response_start)
                if response_end == -1:
                    response_end = len(output)
                if response_start < response_end:
                    result = output[response_start:response_end].strip()
            
            # Buscar pela justificativa
            justification = "Justificativa não encontrada na resposta"
            if "### Justificativa:" in output:
                justification_start = output.find("### Justificativa:") + 18
                justification_end = output.find("---", justification_start)
                if justification_end == -1:
                    justification_end = len(output)
                if justification_start < justification_end:
                    justification = output[justification_start:justification_end].strip()
            
            print(f"✅ Parsing concluído:")
            print(f"   SQL: {sql_query[:100]}...")
            print(f"   Resultado: {result[:100]}...")
            print(f"   Justificativa: {justification[:100]}...")
            
            return sql_query, result, justification
            
        except Exception as e:
            print(f"❌ Erro no parsing: {str(e)}")
            print(f"   Output recebido: {output[:200]}...")
            return "Erro ao processar resposta", "Erro", f"Erro no parsing: {str(e)}"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna o status de saúde do serviço"""
        try:
            # Testar conexão com banco
            db_connected = self.db is not None
            
            # Testar configuração do Gemini
            gemini_configured = bool(settings.google_api_key)
            
            return {
                "status": "healthy" if db_connected and gemini_configured else "unhealthy",
                "database_connected": db_connected,
                "gemini_configured": gemini_configured,
                "database_path": str(settings.database_path)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "database_connected": False,
                "gemini_configured": False
            }

# Instância global do serviço
rag_service = RAGService() 