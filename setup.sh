#!/bin/bash

# Multi-Agent Lead Research System - Setup Script
# This script helps you get started quickly

echo "🎯 Multi-Agent Lead Research System Setup"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENROUTER_API_KEY (required)"
    echo "   - APOLLO_API_KEY (optional)"
    echo ""
    echo "   Get OpenRouter API key from: https://openrouter.ai"
    echo "   Get Apollo API key from: https://apollo.io"
    echo ""
    read -p "Press Enter when you've added your API keys..."
else
    echo "✅ .env file already exists"
fi

# Build and start the services
echo "🚀 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if backend is running
echo "🔍 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
    echo "📖 API docs available at http://localhost:8000/docs"
else
    echo "❌ Backend is not responding. Check logs with: docker-compose logs backend"
fi

# Check if frontend is running
echo "🔍 Checking frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "⚠️  Frontend may still be starting. Check logs with: docker-compose logs frontend"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Try the API at http://localhost:8000/docs"
echo "3. Run the demo script: python demo.py"
echo ""
echo "Useful commands:"
echo "  docker-compose logs backend     # View backend logs"
echo "  docker-compose logs frontend    # View frontend logs"
echo "  docker-compose down            # Stop all services"
echo "  docker-compose up -d           # Start services"
echo ""
echo "For support, check the README.md file"
