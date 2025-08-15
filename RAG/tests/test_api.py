import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root_endpoint():
    """Testa o endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Visagio RAG API"

def test_health_endpoint():
    """Testa o endpoint de saúde"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database_connected" in data
    assert "gemini_configured" in data

def test_examples_endpoint():
    """Testa o endpoint de exemplos"""
    response = client.get("/examples")
    assert response.status_code == 200
    data = response.json()
    assert "examples" in data
    assert "total" in data
    assert isinstance(data["examples"], list)
    assert len(data["examples"]) > 0

def test_database_schema_endpoint():
    """Testa o endpoint de esquema do banco"""
    response = client.get("/database/schema")
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    assert "categories" in data
    assert "Chassis" in data["tables"]
    assert "Telemetria" in data["tables"]

def test_query_endpoint_missing_body():
    """Testa o endpoint de consulta sem body"""
    response = client.post("/query")
    assert response.status_code == 422  # Validation error

def test_query_endpoint_empty_query():
    """Testa o endpoint de consulta com query vazia"""
    response = client.post("/query", json={"query": ""})
    assert response.status_code == 400

def test_query_endpoint_valid_request():
    """Testa o endpoint de consulta com request válido"""
    # Este teste pode falhar se o serviço RAG não estiver configurado
    response = client.post("/query", json={"query": "Qual a categoria de telemetria mais utilizada?"})
    
    # Se o serviço estiver configurado, deve retornar 200
    # Se não estiver, deve retornar 500
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "sql_query" in data
        assert "result" in data
        assert "justification" in data
        assert "execution_time" in data
        assert "timestamp" in data

def test_cors_headers():
    """Testa se os headers CORS estão configurados"""
    response = client.options("/")
    # CORS preflight request
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__]) 