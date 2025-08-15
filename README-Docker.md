# 🐳 Executando o Projeto Visagio com Docker

Este documento explica como executar o projeto completo (Frontend Next.js + API RAG) usando Docker.

## 🚀 Início Rápido

### 1. Pré-requisitos

- Docker e Docker Compose instalados
- Chave da API do Google Gemini
- Banco de dados `Bases_VAI - oficial real.db` no diretório `RAG/`

### 2. Configuração Inicial

```bash
# Copiar arquivo de configuração
cp config.env.example .env

# Editar configurações
nano .env
```

Configure no arquivo `.env`:
```env
GOOGLE_API_KEY=sua_chave_da_api_aqui
```

### 3. Executar com Script Automático

```bash
# Tornar o script executável
chmod +x start.sh

# Executar
./start.sh
```

## 🎯 Opções de Execução

### Opção A: Script Interativo (Recomendado)
```bash
./start.sh
```

O script oferece um menu interativo com opções para:
- 🚀 Iniciar em modo produção
- 🔧 Iniciar em modo desenvolvimento
- 🛑 Parar serviços
- 📊 Ver status
- 🧹 Limpar containers
- 📚 Ver logs

### Opção B: Comandos Docker Diretos

#### Desenvolvimento
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

#### Produção
```bash
docker-compose up -d --build
```

#### Parar Serviços
```bash
docker-compose down
docker-compose -f docker-compose.dev.yml down
```

## 🌐 Acessos

Após iniciar os serviços:

- **Frontend Next.js**: http://localhost:3000
- **API RAG**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Nginx (produção)**: http://localhost:80

## 📁 Estrutura dos Arquivos Docker

```
visagio-project/
├── docker-compose.yml          # Produção completa
├── docker-compose.dev.yml      # Desenvolvimento
├── DEMO/
│   └── Dockerfile             # Frontend Next.js
├── RAG/
│   └── Dockerfile             # API RAG
├── nginx/
│   └── nginx.conf             # Configuração Nginx
├── start.sh                    # Script de inicialização
├── config.env.example          # Template de configuração
└── README-Docker.md            # Esta documentação
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `GOOGLE_API_KEY` | Chave da API Gemini | **Obrigatório** |
| `DATABASE_PATH` | Caminho do banco SQLite | `Bases_VAI - oficial real.db` |
| `API_TITLE` | Título da API | `Visagio RAG API` |
| `MODEL_NAME` | Modelo Gemini | `gemini-2.5-flash` |
| `TEMPERATURE` | Temperatura do modelo | `0.0` |
| `NODE_ENV` | Ambiente Node.js | `development` |

### Portas

| Serviço | Porta Externa | Porta Interna |
|---------|---------------|----------------|
| Frontend | 3000 | 3000 |
| API RAG | 8000 | 8000 |
| Nginx | 80 | 80 |
| Redis | 6379 | 6379 |
| PostgreSQL | 5432 | 5432 |

## 🐳 Comandos Docker Úteis

### Ver Status dos Serviços
```bash
docker-compose ps
docker ps
```

### Ver Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f visagio-frontend
docker-compose logs -f visagio-rag-api
```

### Acessar Container
```bash
# Frontend
docker exec -it visagio-project_visagio-frontend_1 sh

# API RAG
docker exec -it visagio-project_visagio-rag-api_1 bash
```

### Rebuild de Serviço
```bash
# Rebuild específico
docker-compose build visagio-frontend
docker-compose build visagio-rag-api

# Rebuild completo
docker-compose build --no-cache
```

## 🚨 Solução de Problemas

### Erro: "Port already in use"
```bash
# Verificar portas em uso
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000

# Parar serviços conflitantes
docker-compose down
```

### Erro: "Permission denied"
```bash
# Dar permissão ao script
chmod +x start.sh

# Executar com sudo se necessário
sudo ./start.sh
```

### Erro: "Container failed to start"
```bash
# Ver logs do container
docker-compose logs visagio-rag-api

# Verificar configurações
docker-compose config
```

### Erro: "Database not found"
```bash
# Verificar se o banco existe
ls -la RAG/Bases_VAI\ -\ oficial\ real.db

# Verificar volume no container
docker exec -it visagio-project_visagio-rag-api_1 ls -la
```

## 🔒 Segurança

### Usuário Não-Root
- Todos os containers rodam com usuários não-root
- Permissões mínimas necessárias

### Volumes
- Banco de dados montado como volume somente leitura
- Arquivos de configuração protegidos

### Rede
- Containers isolados em rede Docker
- Portas expostas apenas quando necessário

## 📊 Monitoramento

### Health Checks
- Frontend: Verifica se responde na porta 3000
- API RAG: Verifica endpoint `/health`
- Nginx: Verifica se está respondendo

### Logs
- Logs centralizados via Docker Compose
- Rotação automática de logs
- Níveis de log configuráveis

## 🚀 Deploy em Produção

### 1. Configurar Variáveis de Produção
```env
NODE_ENV=production
GOOGLE_API_KEY=sua_chave_producao
```

### 2. Executar com Perfil de Produção
```bash
docker-compose --profile production up -d
```

### 3. Configurar SSL (opcional)
- Editar `nginx/nginx.conf`
- Adicionar certificados SSL
- Configurar domínio

### 4. Backup e Persistência
```bash
# Backup do banco
docker cp visagio-project_visagio-rag-api_1:/app/Bases_VAI\ -\ oficial\ real.db ./backup/

# Backup de volumes
docker run --rm -v visagio-project_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 🤝 Contribuindo

Para contribuir com melhorias Docker:

1. Teste localmente com `docker-compose.dev.yml`
2. Verifique se não quebra a configuração de produção
3. Atualize esta documentação
4. Teste em diferentes ambientes

## 📞 Suporte

- **Issues**: Abra uma issue no repositório
- **Logs**: Use `docker-compose logs` para debug
- **Documentação**: Consulte os READMEs específicos de cada serviço

---

🎉 **Seu projeto Visagio está rodando com Docker!** 