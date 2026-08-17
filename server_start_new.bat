@echo off
cd /d C:\Users\server\Documents\project\nexora

echo ========================================
echo       NEXORA SERVER START
echo       9 PROCESSES - SEQUENTIAL
echo       5 SECONDS BETWEEN STARTS
echo ========================================
echo.

echo [1/9] Starting Memory Data...
start "NEXORA Memory Data" cmd /k "python -m bots.memory_data"
timeout /t 5 /nobreak >nul

echo [2/9] Starting Contact Worker...
start "NEXORA Contact Worker" cmd /k "python -m bots.contact_worker"
timeout /t 5 /nobreak >nul

echo [3/9] Starting Router Telegram 1...
start "NEXORA Router Telegram 1" cmd /k "python -m bots.command_router bot1_config.json"
timeout /t 5 /nobreak >nul

echo [4/9] Starting Router Telegram 2...
start "NEXORA Router Telegram 2" cmd /k "python -m bots.command_router bot2_config.json"
timeout /t 5 /nobreak >nul

echo [5/9] Starting File Worker...
start "NEXORA File Worker" cmd /k "python -m Core.file_worker"
timeout /t 5 /nobreak >nul

echo [6/9] Starting Partner Worker Bot 1...
start "NEXORA Partner Worker Bot 1" cmd /k "python -m Core.file_partner_worker bot1_config.json"
timeout /t 5 /nobreak >nul

echo [7/9] Starting Partner Worker Bot 2...
start "NEXORA Partner Worker Bot 2" cmd /k "python -m Core.file_partner_worker bot2_config.json"
timeout /t 5 /nobreak >nul

echo [8/9] Starting Lead Bot 1...
start "NEXORA Lead Bot 1" cmd /k "python -m bots.lead-demo"
timeout /t 5 /nobreak >nul

echo [9/9] Starting Lead Bot 2...
start "NEXORA Lead Bot 2" cmd /k "python -m bots.lead-demo2"
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo       NEXORA SERVER STARTED
echo       9 PROCESSES RUNNING
echo       WHATSAPP DISABLED
echo ========================================
echo.

pause