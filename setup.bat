@echo off
REM Multi-Agent Lead Research System - Windows Setup Script

echo 🎯 Multi-Agent Lead Research System Setup
echo ========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    echo    Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env >nul
    echo ⚠️  Please edit .env file and add your API keys:
    echo    - OPENROUTER_API_KEY ^(required^)
    echo    - APOLLO_API_KEY ^(optional^)
    echo.
    echo    Get OpenRouter API key from: https://openrouter.ai
    echo    Get Apollo API key from: https://apollo.io
    echo.
    pause
) else (
    echo ✅ .env file already exists
)

REM Build and start the services
echo 🚀 Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check if backend is running
echo 🔍 Checking backend health...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running at http://localhost:8000
    echo 📖 API docs available at http://localhost:8000/docs
) else (
    echo ❌ Backend is not responding. Check logs with: docker-compose logs backend
)

REM Check if frontend is running
echo 🔍 Checking frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running at http://localhost:3000
) else (
    echo ⚠️  Frontend may still be starting. Check logs with: docker-compose logs frontend
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Open http://localhost:3000 in your browser
echo 2. Try the API at http://localhost:8000/docs
echo 3. Run the demo script: python demo.py
echo.
echo Useful commands:
echo   docker-compose logs backend     # View backend logs
echo   docker-compose logs frontend    # View frontend logs
echo   docker-compose down            # Stop all services
echo   docker-compose up -d           # Start services
echo.
echo For support, check the README.md file
pause
