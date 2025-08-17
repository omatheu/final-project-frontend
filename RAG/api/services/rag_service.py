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
from typing import List, Any

from config.settings import settings
import os
from datetime import datetime

def simple_similarity(str1: str, str2: str) -> float:
    """Função simples de similaridade para substituir jellyfish temporariamente"""
    try:
        # Verificar se os parâmetros são strings válidas
        if not isinstance(str1, str) or not isinstance(str2, str):
            return 0.0
        
        # Verificar se as strings não estão vazias
        if not str1.strip() or not str2.strip():
            return 0.0
        
        str1_lower = str1.lower().strip()
        str2_lower = str2.lower().strip()
        
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
        
    except Exception as e:
        print(f"⚠️ Aviso: Erro na função simple_similarity: {e}")
        return 0.0

class RAGService:
    """Serviço para gerenciar consultas RAG usando LangChain e Gemini"""
    
    def __init__(self):
        self.db = None
        self.llm = None
        self.toolkit = None
        self.tools = None
        self.df_consultas_validadas = None
        self.agent_executor = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa o serviço RAG seguindo o fluxo do case_agentes_projeto_final.py"""
        try:
            # Configurar o LLM com Gemini
            if not settings.google_api_key:
                raise ValueError("GOOGLE_API_KEY não configurada")
            
            os.environ['GOOGLE_API_KEY'] = settings.google_api_key
            self.llm = ChatGoogleGenerativeAI(
                model=settings.model_name, 
                temperature=0
            )
            
            # Conectar ao banco
            self._connect_database()
            
            # Carregar consultas validadas (se existir)
            self._load_validated_queries()
            
            # Inicializar o agente seguindo o fluxo original
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
        """Gera o prompt do sistema baseado na consulta, seguindo o formato original"""
        try:
            # Garantir que query seja uma string válida
            if not isinstance(query, str):
                query = str(query) if query is not None else ""
            
            shots = self._get_similar_shots(query)
            
            system_prompt = f"""
Você é um sistema especialista em escrever consultas SQLite a partir de descrições textuais. Seu papel é
interpretar um pedido do usuário sobre alguma informação dedutível de um banco de dados fornecido, identificando
o objetivo da consulta e elementos do esquema físico que devem ser utilizados. Usando essas informações, você
deve elaborar uma consulta SQLite SINTATICAMENTE e SEMANTICAMENTE válida para aquele fim, visando concisão
(responda somente o necessário, incluindo SOMENTE colunas extremamente neessárias), eficiência
e clareza (use nomes descritivos nas colunas das tabelas resultantes). TODO pedido do usuário deve ser analisado
mediante embasamento em consultas concretas ao banco de dados. Se um pedido tiver relação com o contexto do banco de dados,
mas parecer amplo demais, você pode fazer suposições embasadas em dados concretos obtidos por consultas de apoio.

Você precisa ter CERTEZA ABSOLUTA de que a consulta sugerida cumpre os seguintes requisitos:

- Sintaxe correta: não contém erros sintáticos de SQLite
- Consistência com o BD: usa tabelas e campos que existem no esquema do banco de dados
- Semântica correta: retorna EXATAMENTE o que o usuário pediu, sem colunas a mais ou a menos
- Imutabilidade do BD: NÃO faz modificações no banco de dados (se baseia inteiramente em cláusulas 'SELECT')
- Concisão: SOMENTE possui colunas estritamente necessárias

Depois de verificar a consulta gerada quanto aos critérios elencados, você DEVE consultar o banco de dados
(via a ferramenta correspondente) usando a consulta validada. O seu raciocínio deve seguir o seguinte esquema, na ordem:

1. Entender o pedido do usuário, relacionando-o com os tipos de informações contidas no banco de dados e falando qual deve ser o formato de dado da solução para a questão do usuário
2. Verificar, vocalmente, se houve algum erro retornado na observação da ferramenta. Se sim, descreva o erro e ajuste seu retorno para corrigí-lo
2. Traçar o passo-a-passo de como encontrar a resposta para o pedido do usuário, destacando possíveis suposições e necessidade de consultas auxiliares
3. Esclarecer o que será feito nesta iteração, explicando qual o objetivo da ação e relembrando as restrições do prompt
4. Dizer, explicitamente, se o resultado conclusivo já foi obtido. Se não, NÃO inclua o campo 'Final Answer' em seu retorno.
5. Retornar output EXATAMENTE como no formato ReAct de Chain-of-Thought, segundo formatação exigida neste prompt

A formatação do output DEVE, OBRIGATORIAMENTE, seguir EXATAMENTE uma das duas possibilidades (parênteses angulados '<<>>' são placeholders):

- Caso haja uma chamada de ferramenta:

---

Thought: <<mensagem que SEMPRE DEVE conter TODO o seu raciocínio>>

Action: <<nome da ferramenta, ex: sql_db_query>>

Action Input: <<input da ferramenta, string pura SEM incluir blocos markdown, ex: SELECT... (restante da consulta)>>

---

- Caso deva retornar a resposta definitiva:

---

Thought: <<mensagem confirmando que todos os passos para obtenção da solução final foram concluídos>>

Final Answer: <<resposta conclusiva>>

---

JAMAIS misture esses dois formatos. Na área 'Thought', avalie em qual das duas situações a iteração atual se encaixa.

A formatação do campo 'Final Answer', que SOMENTE será incluído no output ReAct da resposta para o usuário, deve ser:

---

Thought: <<raciocínio de confirmação da decisão>>

Final Answer:

### Consulta:
```sql
<<consulta SQLite VALIDADA, em pretty-print>>
```

### Resposta:
<<resultado obtido da consulta feita, em formato de dado condizente com o objetivo do usuário e mais enxuto possível>>

### Justificativa:
<<explicação da relação entre a pergunta e a consulta gerada, explicitando suposições feitas no processo>>

---

Existem dois casos de pedidos de usuário que você NÃO deve atender (e retornar imediatamente):

- Pedidos que não têm relação com o banco de dados
- Pedidos que envolvem modificação do banco de dados (inclusão, exclusão e alteração de elementos)

Se o pedido do usuário se encontrar em um dos dois casos acima, retorne imediatamente a resposta definitiva no seguinte
formato:

---

Thought: <<raciocínio de confirmação da decisão>>

Final Answer:

**ERRO:** <<justificativa para o lançamento do erro>>

---

O banco de dados que você usará consiste de dados de telemetria de uma empresa locadora de maquinário agrícola. As perguntas
feitas para você serão realizadas por analistas de dados da empresa que buscam elaborar relatórios informativos eficientes
para os clientes. Segue o esquema físico do banco de dados da empresa:

```sql
-- Tabela relacionando dados de clientes e seus contratos de locação de veículos
CREATE TABLE Chassis (
  Chassi INTEGER PRIMARY KEY, -- ID do chassi, que identifica uma máquina
  Contrato INTEGER, -- ID do contrato, que pode incluir vários chassis
  Cliente INTEGER, -- ID do cliente, que pode estar envolvido em vários contratos e ter vários chassis
  Modelo INTEGER -- ID do modelo, que pode categorizar vários chassis
);

-- Tabela contendo dados diários dos veículos obtidos por sensores
CREATE TABLE Telemetria (
  Chassi INTEGER, -- ID do chassi
  UnidadeMedida TEXT, -- Unidade de medida do valor descrito no campo Valor ('l' para litros ou 'hr' para horas)
  Categoria TEXT, -- Nome da categoria da informação sensoriada
  Data TIMESTAMP, -- Data e hora de captação do dado
  Serie TEXT, -- Nome da subcategoria do tipo de dado sensoriado pelo sensor
  Valor REAL -- Valor capturado pelo sensor, medido na UnidadeMedida, sobre a informação descrita pela Categoria e Serie
  PRIMARY KEY (Chassi, Categoria, Serie, Data)
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
de raciocinar sobre os pedidos quanto de escrever consultas SQLite efetivas, concisas e bem explicadas. Serão humanos os
principais consumidores de suas respostas.

---

Algumas restrições que você DEVE seguir em qualquer resposta sua é:

- Inclusão do campo 'Thought': você SEMPRE DEVE escrever o seu raciocínio no campo 'Thought' designado
- Resolução de problemas complexos: para perguntas que exigem múltiplos cálculos ou junções, ou se precisar supor métricas, é PREFERÍVEL que você quebre o problema em ações menores e sequenciais. Explique essa estratégia no seu 'Thought'
- Teste de sanidade: na resposta definitiva, inclua o campo 'Thought' certificando que a resposta é totalmente baseada na 'Observation' da consulta definitiva e que todas as etapas planejadas foram seguidas
- A prova final: O conteúdo do campo 'Resposta', dentro da 'Final Answer', DEVE ser o resultado direto e inalterado da 'Observation' obtida na ÚLTIMA chamada de ferramenta
- Formatação da resposta para a pergunta: converta o formato da resposta exibida no campo 'Resposta' de acordo com o identificado no pedido do usuário
  - Tabelas: caso o valor natural da resposta seja uma tabela, USE a notação Markdown para escrevê-la
- Uso OBRIGATÓRIO de ferramentas: você SEMPRE deve usar uma ferramenta caso não saiba a resposta imediata para alguma questão
- Tratamento de erros: você SEMPRE deve tratar os erros que receber de observações de ferramentas, declarando qual seu motivo e como consertá-lo
- Proibição de alucinação: NUNCA alucine respostas
- String pura no 'Action Input': o campo 'Action Input' só deve ser preenchido com strings puras, NUNCA com blocos Markdown

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
            
            return system_prompt
            
        except Exception as e:
            print(f"⚠️ Aviso: Erro ao gerar system prompt: {e}")
            # Retornar um prompt básico em caso de erro
            return """Você é um sistema especialista em escrever consultas SQLite. Use as ferramentas disponíveis para responder às perguntas."""
    
    def _get_similar_shots(self, query: str) -> str:
        """Obtém exemplos similares de consultas"""
        try:
            # Verificar se o DataFrame está vazio ou se a query é inválida
            if (self.df_consultas_validadas is None or 
                self.df_consultas_validadas.empty or 
                not isinstance(query, str) or 
                not query.strip()):
                return ""
            
            shots = ""
            for idx, linha in self.df_consultas_validadas.iterrows():
                # Verificar se as colunas existem e contêm strings válidas
                if ('Pedido' in linha and 'Consulta' in linha and 
                    isinstance(linha['Pedido'], str) and 
                    isinstance(linha['Consulta'], str)):
                    
                    if simple_similarity(linha['Pedido'], query) > 0.7:
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
            
        except Exception as e:
            print(f"⚠️ Aviso: Erro ao obter shots similares: {e}")
            return ""
    
    def _initialize_agent(self):
        """Inicializa o agente seguindo o fluxo do case_agentes_projeto_final.py"""
        try:
            print("🔧 Inicializando agente RAG...")
            
            # Criar o Toolkit SQL
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            
            # Criar a Calculadora com LLMMathChain (como no original)
            math_chain = LLMMathChain.from_llm(llm=self.llm, verbose=True)
            math_tool = Tool(
                name="Calculadora Matemática",
                func=math_chain.run,
                description="""
Use esta ferramenta para realizar operações aritméticas.
Use se precisar realizar alguma operação matemática não suportada por SQLite em algum conjunto de dados.
A entrada é uma expressão aritmética a ser resolvida.
A saída é o resultado do cálculo da expressão aritmética.
"""
            )
            
            # Obter ferramentas do toolkit SQL e adicionar a calculadora
            self.tools = self.toolkit.get_tools() + [math_tool]
            
            # Criar o prompt personalizado com o contexto do schema
            try:
                prompt_prefix = self._get_system_prompt("") + "\n\nUse as ferramentas disponíveis."
                prompt_suffix = "\n\nPergunta: {input}\n{agent_scratchpad}"
                
                # Prompt final do agente
                agent_prompt = PromptTemplate(
                    input_variables=["input", "agent_scratchpad"],
                    template=prompt_prefix + prompt_suffix
                )
            except Exception as prompt_error:
                print(f"⚠️ Aviso: Erro ao criar prompt personalizado, usando prompt padrão: {prompt_error}")
                # Usar prompt padrão em caso de erro
                agent_prompt = PromptTemplate(
                    input_variables=["input", "agent_scratchpad"],
                    template="""Você é um sistema especialista em escrever consultas SQLite. Use as ferramentas disponíveis para responder às perguntas.

Pergunta: {input}
{agent_scratchpad}"""
                )
            
            # Criar a LLMChain com o prompt customizado
            llm_chain = LLMChain(llm=self.llm, prompt=agent_prompt)
            
            # Criar o agente com a LLMChain
            agent = ZeroShotAgent(llm_chain=llm_chain, tools=self.tools)
            
            # Executor final do agente
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True
            )
            
            print("✅ Agente RAG inicializado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar agente: {str(e)}")
            raise RuntimeError(f"Erro ao inicializar agente: {str(e)}")
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """Executa uma consulta usando o agente RAG seguindo o fluxo original"""
        start_time = time.time()
        
        try:
            print(f"🔍 Executando consulta: {query_text}")
            
            # Garantir que query_text seja uma string válida
            if not isinstance(query_text, str):
                query_text = str(query_text) if query_text is not None else ""
            
            if not self.agent_executor:
                raise RuntimeError("Agente não foi inicializado corretamente")
            
            # Executar a consulta usando o agente (como no original)
            response = self.agent_executor.invoke({
                "input": query_text,
                "agent_scratchpad": ""
            })
            
            execution_time = time.time() - start_time
            
            # Extrair informações da resposta
            output = response.get("output", "")
            
            # Garantir que output seja uma string válida
            if not isinstance(output, str):
                output = str(output) if output is not None else ""
            
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
            raise RuntimeError(f"Erro na execução da consulta: {str(e)}")
    
    def _parse_agent_response(self, output: str) -> tuple:
        """Extrai informações estruturadas da resposta do agente"""
        try:
            print(f"🔍 Parsing resposta do agente: {output[:200]}...")
            
            # Garantir que output seja uma string válida
            if not isinstance(output, str):
                output = str(output) if output is not None else ""
            
            # Para a consulta SQL, procurar por qualquer coisa que pareça SQL
            sql_query = "Consulta não encontrada na resposta"
            if "SELECT" in output.upper():
                # Procurar por linhas que contenham SELECT
                lines = output.split('\n')
                for line in lines:
                    if 'SELECT' in line.upper() and len(line.strip()) > 10:
                        sql_query = line.strip()
                        break
            
            # Para o resultado, extrair apenas a parte final da resposta (Final Answer)
            result = self._extract_final_answer(output)
            
            # Para a justificativa, extrair apenas o processo de pensamento
            justification = self._extract_thought_process(output)
            
            print(f"✅ Parsing concluído - SQL: {len(sql_query)}, Result: {len(str(result))}, Justification: {len(justification)}")
            
            return sql_query, result, justification
            
        except Exception as e:
            print(f"❌ Erro no parsing: {str(e)}")
            # Garantir que sempre retornamos strings válidas
            error_msg = str(e) if e is not None else "Erro desconhecido"
            return "Erro ao processar resposta", error_msg, f"Processo da AI: {error_msg}"
    
    def _extract_final_answer(self, output: str) -> str:
        """Extrai apenas a resposta final da AI, eliminando duplicações"""
        try:
            # Procurar por "Final Answer:" ou similar
            if "Final Answer:" in output:
                # Extrair apenas a parte após "Final Answer:"
                final_answer_start = output.find("Final Answer:")
                final_answer = output[final_answer_start:].strip()
                
                # Limpar formatação desnecessária
                final_answer = final_answer.replace("Final Answer:", "").strip()
                
                # Se encontrar múltiplas seções, pegar apenas a última
                if "---" in final_answer:
                    sections = final_answer.split("---")
                    final_answer = sections[-1].strip()
                
                return final_answer
            
            # Se não encontrar "Final Answer:", procurar por padrões de resposta
            elif "### Resposta:" in output:
                resposta_start = output.find("### Resposta:")
                resposta_end = output.find("###", resposta_start + 3)
                
                if resposta_end == -1:
                    resposta_end = len(output)
                
                resposta = output[resposta_start:resposta_end].strip()
                return resposta.replace("### Resposta:", "").strip()
            
            # Fallback: retornar apenas as últimas linhas relevantes
            lines = output.split('\n')
            relevant_lines = []
            for line in reversed(lines):
                if line.strip() and not line.startswith("Thought:"):
                    relevant_lines.insert(0, line.strip())
                if len(relevant_lines) >= 5:  # Limitar a 5 linhas
                    break
            
            return "\n".join(relevant_lines) if relevant_lines else output[-500:]  # Últimos 500 caracteres
            
        except Exception as e:
            print(f"⚠️ Aviso: Erro ao extrair resposta final: {e}")
            return output[-500:]  # Fallback: últimos 500 caracteres
    
    def _extract_thought_process(self, output: str) -> str:
        """Extrai apenas o processo de pensamento da AI"""
        try:
            thoughts = []
            lines = output.split('\n')
            
            for line in lines:
                if line.strip().startswith("Thought:"):
                    thought = line.replace("Thought:", "").strip()
                    if thought:
                        thoughts.append(thought)
            
            if thoughts:
                return "Processo de pensamento:\n" + "\n".join(thoughts)
            else:
                # Se não encontrar "Thought:", procurar por outras indicações de processo
                if "Action:" in output:
                    return "Processo de execução da consulta (sem detalhes de pensamento)"
                else:
                    return "Processo de análise da consulta"
                    
        except Exception as e:
            print(f"⚠️ Aviso: Erro ao extrair processo de pensamento: {e}")
            return "Processo de análise da consulta"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna o status de saúde do serviço"""
        try:
            # Testar conexão com banco
            db_connected = self.db is not None
            
            # Testar configuração do Gemini
            gemini_configured = bool(settings.google_api_key)
            
            # Testar se o agente foi inicializado
            agent_initialized = self.agent_executor is not None
            
            return {
                "status": "healthy" if db_connected and gemini_configured and agent_initialized else "unhealthy",
                "database_connected": db_connected,
                "gemini_configured": gemini_configured,
                "agent_initialized": agent_initialized,
                "database_path": str(settings.database_path)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "database_connected": False,
                "gemini_configured": False,
                "agent_initialized": False
            }

# Instância global do serviço
rag_service = RAGService() 