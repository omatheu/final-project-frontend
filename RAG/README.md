# Visagio RAG API

API para consultas RAG (Retrieval-Augmented Generation) em banco de dados SQLite usando LangChain e Google Gemini.

## 🚀 Funcionalidades

- **Consultas em Linguagem Natural**: Faça perguntas em português sobre dados de telemetria
- **Geração Automática de SQL**: O sistema gera consultas SQL otimizadas automaticamente
- **Análise de Dados**: Extraia insights de dados de maquinário agrícola
- **API RESTful**: Interface HTTP completa com documentação Swagger
- **Documentação Automática**: OpenAPI/Swagger integrado

## 📊 Sobre os Dados

O sistema trabalha com dados de telemetria de uma empresa locadora de maquinário agrícola, incluindo:

- **Tabela Chassis**: Relaciona clientes, contratos e modelos de equipamentos
- **Tabela Telemetria**: Dados sensoriais dos veículos (uso do motor, combustível, configurações)

### Categorias de Dados Disponíveis

- **Uso do Motor**: Tempo em cada status (Chave-Ligada, Marcha Lenta, Carga Baixa/Média/Alta)
- **Uso do Combustível**: Consumo por status do motor
- **Configuração do Motor**: Tempo em cada modo (HP - Alta Potência, P - Padrão, E - Econômico)

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **LangChain**: Framework para aplicações de IA
- **Google Gemini**: Modelo de linguagem para geração de consultas
- **SQLite**: Banco de dados local
- **Pydantic**: Validação de dados
- **Uvicorn**: Servidor ASGI

## 📁 Estrutura do Projeto

```
RAG/
├── api/                    # Código da API
│   ├── models/            # Modelos Pydantic
│   ├── services/          # Lógica de negócio
│   ├── utils/             # Utilitários
│   └── main.py            # Aplicação FastAPI
├── config/                 # Configurações
│   ├── settings.py        # Configurações da aplicação
│   └── config.env.example # Template de variáveis de ambiente
├── tests/                  # Testes automatizados
├── requirements.txt        # Dependências Python
├── run.py                 # Script de inicialização
└── README.md              # Esta documentação
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- Python 3.8+
- Chave da API do Google Gemini
- Banco de dados SQLite (`Bases_VAI - oficial real.db`)

### 2. Clone e Instale

```bash
# Navegue para o diretório do projeto
cd RAG

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configure as Variáveis de Ambiente

```bash
# Copie o template de configuração
cp config.env.example .env

# Edite o arquivo .env com sua chave da API
nano .env  # ou use seu editor preferido
```

Configure no arquivo `.env`:
```env
GOOGLE_API_KEY=sua_chave_da_api_aqui
DATABASE_PATH=Bases_VAI - oficial real.db
```

### 4. Verifique o Banco de Dados

Certifique-se de que o arquivo `Bases_VAI - oficial real.db` está no diretório `RAG/`.

## 🏃‍♂️ Executando a API

### Opção 1: Script de Inicialização (Recomendado)

```bash
python run.py
```

### Opção 2: Uvicorn Direto

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Opção 3: Módulo Python

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Documentação da API

Após iniciar a API, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔍 Endpoints Disponíveis

### GET `/`
- **Descrição**: Informações básicas da API
- **Resposta**: Versão e links para documentação

### GET `/health`
- **Descrição**: Status de saúde da API
- **Resposta**: Status do banco de dados e configuração do Gemini

### POST `/query`
- **Descrição**: Executa uma consulta RAG
- **Body**: `{"query": "sua pergunta aqui"}`
- **Resposta**: Consulta SQL, resultado e justificativa

### GET `/examples`
- **Descrição**: Exemplos de consultas que podem ser feitas
- **Resposta**: Lista de consultas de exemplo

### GET `/database/schema`
- **Descrição**: Esquema do banco de dados
- **Resposta**: Estrutura das tabelas e categorias

## 💡 Exemplos de Uso

### 1. Consulta Básica

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Qual foi o tempo total de uso do motor por chassi?"}'
```

### 2. Análise de Eficiência

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Qual cliente apresenta maior proporção de tempo improdutivo?"}'
```

### 3. Verificação de Saúde

```bash
curl "http://localhost:8000/health"
```

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest tests/
```

## 🔧 Configurações Avançadas

### Ajustar Threshold de Similaridade

No arquivo `.env`:
```env
SIMILARITY_THRESHOLD=0.8
```

### Mudar Modelo do Gemini

No arquivo `.env`:
```env
MODEL_NAME=gemini-2.0-flash-exp
TEMPERATURE=0.1
```

### Configurar CORS

Edite `api/main.py` para restringir origens:
```python
allow_origins=["http://localhost:3000", "https://seudominio.com"]
```

## 🚨 Solução de Problemas

### Erro: "GOOGLE_API_KEY não configurada"
- Verifique se o arquivo `.env` existe
- Confirme se a chave está configurada corretamente

### Erro: "Banco de dados não encontrado"
- Verifique se o arquivo do banco está no local correto
- Confirme o caminho em `DATABASE_PATH`

### Erro: "Erro ao inicializar serviço RAG"
- Verifique se todas as dependências estão instaladas
- Confirme se a chave da API é válida

### Performance Lenta
- Ajuste o `TEMPERATURE` para valores mais baixos
- Considere usar um modelo mais rápido do Gemini

### Dados Duplicados na Resposta
- **PROBLEMA RESOLVIDO**: A API estava retornando conteúdo duplicado entre os campos `result` e `justification`
- **SOLUÇÃO IMPLEMENTADA**: 
  - Parsing inteligente da resposta da AI para extrair apenas o resultado final
  - Separação clara entre processo de pensamento e resultado
  - Validação Pydantic para evitar duplicações
- **TESTE**: Use o endpoint `/test/response-structure` para verificar a estrutura da resposta
- **SCRIPT**: Execute `python test_duplication.py` para análise detalhada

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Consulte a documentação da API em `/docs`
- Verifique os logs da aplicação

## 🔮 Roadmap

- [ ] Cache de consultas frequentes
- [ ] Autenticação e autorização
- [ ] Métricas de uso e performance
- [ ] Suporte a outros bancos de dados
- [ ] Interface web para consultas
- [ ] Exportação de resultados em múltiplos formatos 