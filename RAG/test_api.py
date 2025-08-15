#!/usr/bin/env python3
"""
Script de teste para verificar se a API está funcionando
"""

import requests
import json
import time

def test_api():
    """Testa os endpoints da API"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testando Visagio RAG API...")
    print("=" * 50)
    
    # Teste 1: Endpoint raiz
    print("1. Testando endpoint raiz...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso: {data['message']} v{data['version']}")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 2: Health check
    print("2. Testando health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Banco conectado: {data['database_connected']}")
            print(f"   Gemini configurado: {data['gemini_configured']}")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 3: Exemplos
    print("3. Testando endpoint de exemplos...")
    try:
        response = requests.get(f"{base_url}/examples")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Exemplos encontrados: {data['total']}")
            for i, example in enumerate(data['examples'][:2], 1):
                print(f"   {i}. {example['query'][:50]}...")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 4: Schema do banco
    print("4. Testando endpoint de schema...")
    try:
        response = requests.get(f"{base_url}/database/schema")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Schema carregado")
            print(f"   Tabelas: {', '.join(data['tables'].keys())}")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 5: Documentação
    print("5. Verificando documentação...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Swagger UI disponível")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("🎯 Testes concluídos!")
    print(f"📚 Acesse a documentação em: {base_url}/docs")
    print(f"🔍 Teste uma consulta em: {base_url}/query")

if __name__ == "__main__":
    test_api() 