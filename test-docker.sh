#!/bin/bash

# Script para testar o build Docker
# =================================

set -e

echo "🧪 Testando builds Docker..."
echo "============================="

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker e tente novamente."
    exit 1
fi

# Função para testar build
test_build() {
    local service=$1
    local dockerfile=$2
    local context=$3
    
    echo ""
    echo "🔨 Testando build do $service..."
    echo "   Dockerfile: $dockerfile"
    echo "   Contexto: $context"
    
    if docker build -f "$context/$dockerfile" -t "test-$service" "$context"; then
        echo "✅ Build do $service bem-sucedido!"
        # Limpar imagem de teste
        docker rmi "test-$service" > /dev/null 2>&1 || true
    else
        echo "❌ Build do $service falhou!"
        return 1
    fi
}

# Testar builds individuais
echo ""
echo "🎯 Testando builds individuais..."

# Testar frontend (produção)
if test_build "frontend" "Dockerfile" "DEMO"; then
    echo "✅ Frontend (produção) - OK"
else
    echo "❌ Frontend (produção) - FALHOU"
fi

# Testar frontend (desenvolvimento)
if test_build "frontend-dev" "Dockerfile.dev" "DEMO"; then
    echo "✅ Frontend (desenvolvimento) - OK"
else
    echo "❌ Frontend (desenvolvimento) - FALHOU"
fi

# Testar API RAG
if test_build "rag-api" "Dockerfile" "RAG"; then
    echo "✅ API RAG - OK"
else
    echo "❌ API RAG - FALHOU"
fi

echo ""
echo "🚀 Testando docker-compose..."

# Testar docker-compose de desenvolvimento
if docker-compose -f docker-compose.dev.yml config > /dev/null 2>&1; then
    echo "✅ docker-compose.dev.yml - Configuração válida"
else
    echo "❌ docker-compose.dev.yml - Configuração inválida"
fi

# Testar docker-compose de produção
if docker-compose config > /dev/null 2>&1; then
    echo "✅ docker-compose.yml - Configuração válida"
else
    echo "❌ docker-compose.yml - Configuração inválida"
fi

echo ""
echo "🎉 Testes concluídos!"
echo ""
echo "📋 Resumo:"
echo "   - Frontend produção: $(docker build -f DEMO/Dockerfile -t test-frontend DEMO > /dev/null 2>&1 && echo "✅" || echo "❌")"
echo "   - Frontend dev: $(docker build -f DEMO/Dockerfile.dev -t test-frontend-dev DEMO > /dev/null 2>&1 && echo "✅" || echo "❌")"
echo "   - API RAG: $(docker build -f RAG/Dockerfile -t test-rag RAG > /dev/null 2>&1 && echo "✅" || echo "❌")"
echo ""
echo "🧹 Limpando imagens de teste..."
docker rmi test-frontend test-frontend-dev test-rag > /dev/null 2>&1 || true
echo "✅ Limpeza concluída!" 