from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    """Modelo para requisição de consulta"""
    query: str = Field(..., description="Pergunta ou consulta em linguagem natural")
    similarity_threshold: Optional[float] = Field(0.7, description="Threshold para similaridade de consultas")

class QueryResponse(BaseModel):
    """Modelo para resposta da consulta"""
    query: str = Field(..., description="Pergunta original")
    sql_query: str = Field(..., description="Consulta SQL gerada")
    result: Any = Field(..., description="Resultado da consulta")
    justification: str = Field(..., description="Justificativa da consulta gerada")
    execution_time: float = Field(..., description="Tempo de execução em segundos")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da execução")

class ErrorResponse(BaseModel):
    """Modelo para respostas de erro"""
    error: str = Field(..., description="Descrição do erro")
    detail: Optional[str] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")

class HealthResponse(BaseModel):
    """Modelo para resposta de health check"""
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do check")
    database_connected: bool = Field(..., description="Status da conexão com o banco")
    gemini_configured: bool = Field(..., description="Status da configuração do Gemini") 