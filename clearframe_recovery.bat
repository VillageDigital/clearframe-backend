@echo off
:: 🚀 ClearFrame Auto-Recovery Script
:: Checks if the container is running, cleans up, and restarts if needed.

echo Checking if ClearFrame is running...
docker ps | findstr /i "clearframe-backend" >nul && (
    echo ✅ ClearFrame is already running!
    exit /b 0
)

echo ⚠️ ClearFrame is NOT running. Restarting...

:: Stop any running containers
docker-compose down

:: Clean up unused Docker resources (optional but recommended)
docker system prune -f

:: Restart ClearFrame in the background
docker-compose up -d

echo ✅ Recovery complete! 🚀
exit /b 0
