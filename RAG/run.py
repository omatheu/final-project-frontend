#!/usr/bin/env python3
"""
Script de inicialização da API Visagio RAG
"""

import uvicorn
import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Função principal para executar a API"""
    
    # Verificar se o arquivo .env existe
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado!")
        print("📝 Copie config.env.example para .env e configure sua GOOGLE_API_KEY")
        print("🔑 Exemplo: cp config.env.example .env")
        print("📝 Edite o arquivo .env com sua chave da API do Gemini")
        return
    
    # Verificar se a API_KEY está configurada
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY não configurada no arquivo .env")
        print("🔑 Configure sua chave da API do Gemini no arquivo .env")
        return
    
    # Verificar se o banco existe
    from config.settings import settings
    db_path = Path(settings.database_path)
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        print("💾 Verifique se o arquivo do banco está no local correto")
        return
    
    print("🚀 Iniciando Visagio RAG API...")
    print(f"📊 Banco de dados: {db_path}")
    print(f"🤖 Modelo: {settings.model_name}")
    print(f"🌐 API disponível em: http://localhost:8000")
    print(f"📚 Documentação: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        # Executar a API
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar a API: {e}")

if __name__ == "__main__":
    main() 