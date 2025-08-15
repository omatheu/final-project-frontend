from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Dict, Any

from config.settings import settings
from api.models.query_models import QueryRequest, QueryResponse, ErrorResponse, HealthResponse
from api.services.rag_service import rag_service

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    try:
        # Verificar se o serviço RAG está funcionando
        health_status = rag_service.get_health_status()
        if health_status["status"] != "healthy":
            print(f"Aviso: Serviço RAG não está saudável: {health_status}")
        else:
            print("✅ Serviço RAG inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar serviço RAG: {e}")

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Visagio RAG API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Verificar o status de saúde da API"""
    try:
        health_status = rag_service.get_health_status()
        return HealthResponse(
            status=health_status["status"],
            database_connected=health_status["database_connected"],
            gemini_configured=health_status["gemini_configured"]
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            database_connected=False,
            gemini_configured=False
        )

@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def execute_query(request: QueryRequest):
    """
    Executa uma consulta RAG usando linguagem natural
    
    - **query**: Pergunta ou consulta em linguagem natural
    - **similarity_threshold**: Threshold para similaridade de consultas (opcional)
    
    Retorna:
    - A consulta SQL gerada
    - O resultado da consulta
    - Justificativa da consulta
    - Tempo de execução
    """
    try:
        start_time = time.time()
        
        # Executar a consulta RAG
        result = rag_service.query(request.query)
        
        # Criar resposta estruturada
        response = QueryResponse(
            query=result["query"],
            sql_query=result["sql_query"],
            result=result["result"],
            justification=result["justification"],
            execution_time=result["execution_time"]
        )
        
        return response
        
    except ValueError as e:
        # Erro de validação
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Erro de execução
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Erro genérico
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/examples", tags=["Examples"])
async def get_example_queries():
    """Retorna exemplos de consultas que podem ser feitas"""
    examples = [
        {
            "query": "Qual foi o tempo total de uso do motor (em horas) por chassi?",
            "description": "Consulta sobre tempo de uso do motor por equipamento"
        },
        {
            "query": "Qual a categoria de telemetria mais utilizada?",
            "description": "Análise de categorias de dados de telemetria"
        },
        {
            "query": "Qual cliente apresenta maior proporção de tempo improdutivo (marcha lenta) ou em baixo uso (carga baixa) em relação ao tempo total do motor?",
            "description": "Análise de eficiência por cliente"
        },
        {
            "query": "É possível identificar equipamentos com manutenção preventiva necessária com base nos padrões de uso?",
            "description": "Análise preditiva de manutenção"
        }
    ]
    
    return {
        "examples": examples,
        "total": len(examples),
        "note": "Estas são consultas de exemplo. Você pode fazer qualquer pergunta relacionada aos dados de telemetria."
    }

@app.get("/database/schema", tags=["Database"])
async def get_database_schema():
    """Retorna informações sobre o esquema do banco de dados"""
    try:
        # Obter informações das tabelas
        tables_info = {}
        
        # Informações sobre a tabela Chassis
        tables_info["Chassis"] = {
            "description": "Tabela relacionando dados de clientes e seus contratos de locação de veículos",
            "columns": {
                "Chassi": {"type": "INTEGER", "description": "ID do chassi"},
                "Contrato": {"type": "INTEGER", "description": "ID do contrato"},
                "Cliente": {"type": "INTEGER", "description": "ID do cliente"},
                "Modelo": {"type": "INTEGER", "description": "ID do modelo"}
            }
        }
        
        # Informações sobre a tabela Telemetria
        tables_info["Telemetria"] = {
            "description": "Tabela contendo dados diários dos veículos obtidos por sensores",
            "columns": {
                "Chassi": {"type": "INTEGER", "description": "ID do chassi"},
                "UnidadeMedida": {"type": "TEXT", "description": "Unidade de medida ('l' para litros ou 'hr' para horas)"},
                "Categoria": {"type": "TEXT", "description": "Nome da categoria da informação sensoriada"},
                "Data": {"type": "TIMESTAMP", "description": "Data e hora de captação do dado"},
                "Serie": {"type": "TEXT", "description": "Nome da subcategoria do tipo de dado sensoriado"},
                "Valor": {"type": "REAL", "description": "Valor capturado pelo sensor"}
            }
        }
        
        # Categorias e séries disponíveis
        categories_info = {
            "Uso do Motor": {
                "description": "Tempo (em horas 'hr') em cada status de motor",
                "series": ["Chave-Ligada", "Marcha Lenta", "Carga Baixa", "Carga Média", "Carga Alta"]
            },
            "Uso do Combustível do Motor": {
                "description": "Consumo de combustível (em litros 'l') em cada status de motor",
                "series": ["Chave-Ligada", "Marcha Lenta", "Carga Baixa", "Carga Média", "Carga Alta"]
            },
            "Uso da Configuração do Modo do Motor": {
                "description": "Tempo (em horas 'hr') em cada configuração de motor",
                "series": ["HP", "P", "E"]
            }
        }
        
        return {
            "database_path": str(settings.database_path),
            "tables": tables_info,
            "categories": categories_info,
            "note": "Este esquema representa dados de telemetria de uma empresa locadora de maquinário agrícola."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter esquema: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc),
            "timestamp": time.time()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 