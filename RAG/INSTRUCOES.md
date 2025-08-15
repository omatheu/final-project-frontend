# 🚀 Instruções para Executar a Visagio RAG API

## ✅ Projeto Convertido com Sucesso!

O projeto foi convertido do Google Colab para uma API FastAPI completa com:
- ✅ Estrutura organizada em pastas
- ✅ Documentação Swagger automática
- ✅ Configuração de ambiente (.env)
- ✅ API RESTful completa
- ✅ Serviço RAG com LangChain e Gemini

## 🏃‍♂️ Como Executar

### 1. Configurar a API Key do Gemini

```bash
# Edite o arquivo .env
nano .env

# Configure sua chave da API:
GOOGLE_API_KEY=sua_chave_da_api_aqui
```

### 2. Ativar o Ambiente Virtual

```bash
source venv/bin/activate
```

### 3. Executar a API

#### Opção A: Script de Inicialização (Recomendado)
```bash
python run.py
```

#### Opção B: Uvicorn Direto
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acessar a API

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

## 🧪 Testar a API

### Executar Testes Automatizados
```bash
python test_api.py
```

### Testar Endpoints Manualmente

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Exemplos de Consultas
```bash
curl http://localhost:8000/examples
```

#### Schema do Banco
```bash
curl http://localhost:8000/database/schema
```

#### Fazer uma Consulta RAG
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Qual foi o tempo total de uso do motor por chassi?"}'
```

## 📁 Estrutura do Projeto

```
RAG/
├── api/                    # Código da API
│   ├── models/            # Modelos Pydantic
│   ├── services/          # Lógica de negócio (RAG)
│   ├── utils/             # Utilitários
│   └── main.py            # Aplicação FastAPI
├── config/                 # Configurações
│   ├── settings.py        # Configurações da aplicação
│   └── config.env.example # Template de variáveis
├── tests/                  # Testes automatizados
├── requirements.txt        # Dependências Python
├── run.py                 # Script de inicialização
├── test_api.py            # Script de teste da API
├── Dockerfile             # Containerização
├── docker-compose.yml     # Orquestração Docker
└── README.md              # Documentação completa
```

## 🔧 Configurações Disponíveis

### Variáveis de Ambiente (.env)

```env
# Obrigatório
GOOGLE_API_KEY=sua_chave_aqui

# Opcionais
DATABASE_PATH=Bases_VAI - oficial real.db
API_TITLE=Visagio RAG API
API_VERSION=1.0.0
MODEL_NAME=gemini-2.5-flash
TEMPERATURE=0.0
SIMILARITY_THRESHOLD=0.7
```

## 🐳 Executar com Docker

### Build e Execução
```bash
docker-compose up --build
```

### Apenas Execução
```bash
docker-compose up
```

## 🚨 Solução de Problemas

### Erro: "GOOGLE_API_KEY não configurada"
- Verifique se o arquivo `.env` existe
- Confirme se a chave está configurada

### Erro: "Banco de dados não encontrado"
- Verifique se `Bases_VAI - oficial real.db` está no diretório
- Confirme o caminho em `DATABASE_PATH`

### Erro: "Módulo não encontrado"
- Ative o ambiente virtual: `source venv/bin/activate`
- Reinstale as dependências: `pip install -r requirements.txt`

### Performance Lenta
- Ajuste `TEMPERATURE` para valores mais baixos
- Use modelo mais rápido do Gemini

## 📚 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações da API |
| GET | `/health` | Status de saúde |
| POST | `/query` | Executar consulta RAG |
| GET | `/examples` | Exemplos de consultas |
| GET | `/database/schema` | Esquema do banco |
| GET | `/docs` | Documentação Swagger |

## 🎯 Próximos Passos

1. **Configure sua API Key do Gemini** no arquivo `.env`
2. **Execute a API** com `python run.py`
3. **Teste os endpoints** em http://localhost:8000/docs
4. **Faça consultas RAG** usando o endpoint `/query`

## 🆘 Suporte

- **Documentação**: http://localhost:8000/docs
- **Logs**: Verifique o terminal onde a API está rodando
- **Issues**: Abra uma issue no repositório

---

🎉 **Parabéns! Sua API RAG está pronta para uso!** 