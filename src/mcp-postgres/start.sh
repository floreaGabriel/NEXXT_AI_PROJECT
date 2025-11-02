#!/bin/bash

# Script pentru build și pornire containere
# ARM64: folosește buildx pentru postgres + docker-compose up
# AMD64: doar docker-compose up normal

set -e

echo "🔍 Detectare arhitectură..."
ARCH=$(uname -m)

if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    echo "✅ ARM64 detectat"
    
    # Verifică buildx
    if ! docker buildx version &> /dev/null; then
        echo "❌ Docker buildx nu este disponibil!"
        echo "💡 Instalează: docker buildx create --use"
        exit 1
    fi
    
    echo "🏗️  Pull imagine postgres cu buildx pentru ARM64..."
    docker pull --platform linux/arm64 postgres:16-alpine
    
    echo "🐳 Opresc containere existente..."
    docker-compose down 2>/dev/null || true
    
    echo "🚀 Pornesc containere cu suport ARM64..."
    DOCKER_DEFAULT_PLATFORM=linux/arm64 docker-compose up -d
    
elif [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then
    echo "✅ AMD64 detectat"
    
    echo "🐳 Opresc containere existente..."
    docker-compose down 2>/dev/null || true
    
    echo "🚀 Pornesc containere normal..."
    docker-compose up -d
    
else
    echo "⚠️  Arhitectură necunoscută: $ARCH"
    echo "💡 Încerc cu docker-compose normal..."
    docker-compose down 2>/dev/null || true
    docker-compose up -d
fi

echo ""
echo "✅ Containere pornite!"
echo ""
docker-compose ps

echo ""
echo "💡 Comenzi utile:"
echo "   docker-compose logs -f      # Vezi logs"
echo "   docker-compose down         # Oprește"
echo "   docker exec app-postgres psql -U app -d app  # Conectează la DB"
