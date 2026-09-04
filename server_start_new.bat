@echo off

cd /d C:\Users\server\Documents\project\nexora

echo ========================================
echo       NEXORA SERVER START
echo       21 PROCESSES - SEQUENTIAL
echo       5 SECONDS BETWEEN STARTS
echo ========================================
echo.

echo [1/21] Starting Memory Data...
start "NEXORA Memory Data" cmd /k "python -m bots.memory_data"
timeout /t 5 /nobreak >nul

echo [2/21] Starting Contact Worker Telegram...
start "NEXORA Contact Worker Telegram" cmd /k "python -m bots.contact_worker"
timeout /t 5 /nobreak >nul

echo [3/21] Starting Router Telegram 1...
start "NEXORA Router Telegram 1" cmd /k "python -m bots.command_router bot1_config.json"
timeout /t 5 /nobreak >nul

echo [4/21] Starting Router Telegram 2...
start "NEXORA Router Telegram 2" cmd /k "python -m bots.command_router bot2_config.json"
timeout /t 5 /nobreak >nul

echo [5/21] Starting File Worker...
start "NEXORA File Worker" cmd /k "python -m Core.file_worker"
timeout /t 5 /nobreak >nul

echo [6/21] Starting Partner Worker Telegram 1...
start "NEXORA Partner Worker Telegram 1" cmd /k "python -m Core.file_partner_worker bot1_config.json"
timeout /t 5 /nobreak >nul

echo [7/21] Starting Partner Worker Telegram 2...
start "NEXORA Partner Worker Telegram 2" cmd /k "python -m Core.file_partner_worker bot2_config.json"
timeout /t 5 /nobreak >nul

echo [8/21] Starting Lead Bot 1...
start "NEXORA Lead Bot 1" cmd /k "python -m bots.lead-demo"
timeout /t 5 /nobreak >nul

echo [9/21] Starting Lead Bot 2...
start "NEXORA Lead Bot 2" cmd /k "python -m bots.lead-demo2"
timeout /t 5 /nobreak >nul

echo [10/21] Starting WhatsApp Partner Worker 1...
start "NEXORA WhatsApp Partner Worker 1" cmd /k "python -m Core.file_partner_worker whatsapp_bot1_config.json"
timeout /t 5 /nobreak >nul

echo [11/21] Starting WhatsApp Partner Worker 2...
start "NEXORA WhatsApp Partner Worker 2" cmd /k "python -m Core.file_partner_worker whatsapp_bot2_config.json"
timeout /t 5 /nobreak >nul

echo [12/21] Starting WhatsApp Bot 1...
start "NEXORA WhatsApp Bot 1" cmd /k "python -m bots.demo_lead_1_wa"
timeout /t 5 /nobreak >nul

echo [13/21] Starting WhatsApp Bot 2...
start "NEXORA WhatsApp Bot 2" cmd /k "python -m bots.demo_lead_2_wa"
timeout /t 5 /nobreak >nul

echo [14/21] Starting Router WhatsApp 1...
start "NEXORA Router WhatsApp 1" cmd /k "python -m bots.command_router whatsapp_bot1_config.json"
timeout /t 5 /nobreak >nul

echo [15/21] Starting Router WhatsApp 2...
start "NEXORA Router WhatsApp 2" cmd /k "python -m bots.command_router whatsapp_bot2_config.json"
timeout /t 5 /nobreak >nul

echo [16/21] Starting User Text Specialist 1...
start "NEXORA User Text Specialist 1" cmd /k "python -m bots.user_text_specialist"
timeout /t 5 /nobreak >nul

echo [17/21] Starting User Text Specialist 2...
start "NEXORA User Text Specialist 2" cmd /k "python -m bots.user_text_specialist_2"
timeout /t 5 /nobreak >nul

echo [18/21] Starting User Text Specialist 3...
start "NEXORA User Text Specialist 3" cmd /k "python -m bots.user_text_specialist_3"
timeout /t 5 /nobreak >nul

echo [19/21] Starting User Text Specialist 4...
start "NEXORA User Text Specialist 4" cmd /k "python -m bots.user_text_specialist_4"
timeout /t 5 /nobreak >nul

echo [20/21] Starting User Text Specialist 5...
start "NEXORA User Text Specialist 5" cmd /k "python -m bots.user_text_specialist_5"
timeout /t 5 /nobreak >nul

echo [21/21] Starting User Text Specialist 6...
start "NEXORA User Text Specialist 6" cmd /k "python -m bots.user_text_specialist_6"
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo       NEXORA SERVER STARTED
echo       21 PROCESSES RUNNING
echo       TELEGRAM + WHATSAPP ENABLED
echo       USER TEXT SPECIALISTS 1-6 ENABLED
echo ========================================
echo.

pause