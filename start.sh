#!/bin/bash

# Script de inicialização do Projeto Visagio
# =========================================

set -e

echo "🚀 Iniciando Projeto Visagio..."
echo "================================"

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker e tente novamente."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Copiando config.env.example para .env..."
    cp config.env.example .env
    echo "🔑 Edite o arquivo .env com sua GOOGLE_API_KEY antes de continuar."
    echo "   Exemplo: nano .env"
    exit 1
fi

# Carregar variáveis de ambiente
source .env

# Verificar se a API_KEY está configurada
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_gemini_api_key_here" ]; then
    echo "❌ GOOGLE_API_KEY não configurada no arquivo .env"
    echo "🔑 Configure sua chave da API do Gemini no arquivo .env"
    exit 1
fi

# Verificar se o banco de dados existe
if [ ! -f "RAG/Bases_VAI - oficial real.db" ]; then
    echo "❌ Banco de dados não encontrado: RAG/Bases_VAI - oficial real.db"
    echo "💾 Verifique se o arquivo do banco está no local correto"
    exit 1
fi

# Função para mostrar menu
show_menu() {
    echo ""
    echo "🎯 Escolha uma opção:"
    echo "1) 🚀 Iniciar projeto completo (produção)"
    echo "2) 🔧 Iniciar projeto para desenvolvimento"
    echo "3) 🛑 Parar todos os serviços"
    echo "4) 📊 Status dos serviços"
    echo "5) 🧹 Limpar containers e volumes"
    echo "6) 📚 Mostrar logs"
    echo "7) 🧪 Testar builds Docker"
    echo "8) 🚪 Sair"
    echo ""
    read -p "Digite sua opção (1-8): " choice
}

# Função para iniciar produção
start_production() {
    echo "🚀 Iniciando projeto em modo produção..."
    docker-compose up -d --build
    echo ""
    echo "✅ Projeto iniciado com sucesso!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔌 API RAG: http://localhost:8000"
    echo "📚 Documentação: http://localhost:8000/docs"
    echo "🌍 Nginx: http://localhost:80"
}

# Função para iniciar desenvolvimento
start_development() {
    echo "🔧 Iniciando projeto em modo desenvolvimento..."
    docker-compose -f docker-compose.dev.yml up -d --build
    echo ""
    echo "✅ Projeto iniciado em modo desenvolvimento!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔌 API RAG: http://localhost:8000"
    echo "📚 Documentação: http://localhost:8000/docs"
}

# Função para parar serviços
stop_services() {
    echo "🛑 Parando todos os serviços..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    echo "✅ Serviços parados!"
}

# Função para mostrar status
show_status() {
    echo "📊 Status dos serviços:"
    echo ""
    docker-compose ps
    echo ""
    echo "🔍 Status dos containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Função para limpar
clean_up() {
    echo "🧹 Limpando containers e volumes..."
    read -p "Tem certeza? Isso removerá todos os containers e volumes. (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        docker-compose down -v --remove-orphans
        docker-compose -f docker-compose.dev.yml down -v --remove-orphans
        docker system prune -f
        echo "✅ Limpeza concluída!"
    else
        echo "❌ Operação cancelada."
    fi
}

# Função para mostrar logs
show_logs() {
    echo "📚 Escolha o serviço para ver logs:"
    echo "1) Frontend"
    echo "2) API RAG"
    echo "3) Todos os serviços"
    read -p "Digite sua opção (1-3): " log_choice
    
    case $log_choice in
        1)
            docker-compose logs -f visagio-frontend
            ;;
        2)
            docker-compose logs -f visagio-rag-api
            ;;
        3)
            docker-compose logs -f
            ;;
        *)
            echo "❌ Opção inválida"
            ;;
    esac
}

# Função para testar Docker
test_docker() {
    echo "🧪 Testando builds Docker..."
    if [ -f "./test-docker.sh" ]; then
        ./test-docker.sh
    else
        echo "❌ Script de teste não encontrado"
        echo "📝 Execute: ./test-docker.sh"
    fi
}

# Loop principal
while true; do
    show_menu
    
    case $choice in
        1)
            start_production
            ;;
        2)
            start_development
            ;;
        3)
            stop_services
            ;;
        4)
            show_status
            ;;
        5)
            clean_up
            ;;
        6)
            show_logs
            ;;
        7)
            test_docker
            ;;
        8)
            echo "👋 Até logo!"
            exit 0
            ;;
        *)
            echo "❌ Opção inválida. Tente novamente."
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para continuar..."
done 