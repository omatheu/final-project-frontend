#!/usr/bin/env python3
"""
Script para testar e detectar duplicações na API RAG
"""

import requests
import json
import time

def test_duplication():
    """Testa a API para detectar duplicações"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testando API RAG para detectar duplicações...")
    print("=" * 60)
    
    # Teste 1: Verificar estrutura da resposta
    print("1. Testando estrutura da resposta...")
    try:
        response = requests.get(f"{base_url}/test/response-structure")
        if response.status_code == 200:
            data = response.json()
            print("✅ Teste de estrutura executado com sucesso")
            
            # Analisar resultados
            analysis = data.get("analysis", {})
            response_analysis = analysis.get("response_analysis", {})
            duplication_check = analysis.get("duplication_check", {})
            recommendations = analysis.get("recommendations", [])
            
            print(f"   📊 Análise da resposta:")
            print(f"      - SQL Query: {response_analysis.get('sql_query_length', 0)} chars")
            print(f"      - Result: {response_analysis.get('result_length', 0)} chars")
            print(f"      - Justification: {response_analysis.get('justification_length', 0)} chars")
            print(f"      - Raw Response: {response_analysis.get('raw_response_length', 0)} chars")
            
            print(f"   🔍 Verificação de duplicação:")
            print(f"      - Result vs Justification similares: {duplication_check.get('result_vs_justification_similar', False)}")
            print(f"      - Result extraído da resposta bruta: {duplication_check.get('result_vs_raw_similar', False)}")
            
            print(f"   💡 Recomendações:")
            for rec in recommendations:
                print(f"      {rec}")
                
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 2: Fazer consulta real e verificar duplicações
    print("2. Testando consulta real...")
    try:
        test_query = {
            "query": "Qual a categoria de telemetria mais utilizada?",
            "similarity_threshold": 0.7
        }
        
        response = requests.post(f"{base_url}/query", json=test_query)
        if response.status_code == 200:
            data = response.json()
            print("✅ Consulta executada com sucesso")
            
            # Verificar duplicações manualmente
            query = data.get("query", "")
            sql_query = data.get("sql_query", "")
            result = data.get("result", "")
            justification = data.get("justification", "")
            
            print(f"   📝 Query: {query[:50]}...")
            print(f"   🗃️ SQL: {sql_query[:50]}...")
            print(f"   📊 Result: {str(result)[:100]}...")
            print(f"   💭 Justification: {str(justification)[:100]}...")
            
            # Verificar se result e justification são similares
            if result == justification:
                print("   ⚠️ ALERTA: Result e Justification são idênticos!")
            elif str(result) in str(justification) or str(justification) in str(result):
                print("   ⚠️ ALERTA: Result e Justification têm conteúdo sobreposto!")
            else:
                print("   ✅ Result e Justification são diferentes")
                
        else:
            print(f"❌ Erro na consulta: Status {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 3: Verificar health da API
    print("3. Verificando saúde da API...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            print(f"   Banco conectado: {data.get('database_connected', False)}")
            print(f"   Gemini configurado: {data.get('gemini_configured', False)}")
        else:
            print(f"❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("🎯 Teste de duplicação concluído!")
    print(f"📚 Acesse a documentação em: {base_url}/docs")
    print(f"🔍 Teste manual em: {base_url}/test/response-structure")

if __name__ == "__main__":
    test_duplication() 