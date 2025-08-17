from pydantic import BaseModel, ConfigDict
from pathlib import Path
import os
from typing import Optional

class Settings(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    # API Settings
    api_title: str = "Visagio RAG API"
    api_version: str = "1.0.0"
    api_description: str = "API para consultas RAG em banco de dados SQLite usando LangChain e Gemini"
    
    # Database Settings
    database_path: str = "Bases_VAI - oficial real.db"
    
    # Gemini Settings
    google_api_key: str = ""
    
    # LangChain Settings
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.0
    
    # Similarity Settings
    similarity_threshold: float = 0.7

def load_settings() -> Settings:
    """Carrega as configurações do arquivo .env ou variáveis de ambiente"""
    # Tentar carregar do arquivo .env
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # Criar configurações com valores das variáveis de ambiente
    settings = Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        database_path=os.getenv("DATABASE_PATH", "Bases_VAI - oficial real.db"),
        api_title=os.getenv("API_TITLE", "Visagio RAG API"),
        api_version=os.getenv("API_VERSION", "1.0.0"),
        api_description=os.getenv("API_DESCRIPTION", "API para consultas RAG em banco de dados SQLite usando LangChain e Gemini"),
        model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
        temperature=float(os.getenv("TEMPERATURE", "0.0")),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    )
    
    # Garantir que o caminho do banco seja absoluto
    if not os.path.isabs(settings.database_path):
        settings.database_path = str(Path(__file__).parent.parent / settings.database_path)
    
    return settings

# Instância global das configurações
settings = load_settings() 