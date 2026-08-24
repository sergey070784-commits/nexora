@echo off

cd /d C:\Users\server\Documents\project\nexora

echo ========================================
echo       NEXORA SERVER START
echo       17 PROCESSES - SEQUENTIAL
echo       5 SECONDS BETWEEN STARTS
echo ========================================
echo.


echo [1/17] Starting Memory Data...

start "NEXORA Memory Data" cmd /k "python -m bots.memory_data"

timeout /t 5 /nobreak >nul


echo [2/17] Starting Contact Worker Telegram...

start "NEXORA Contact Worker Telegram" cmd /k "python -m bots.contact_worker"

timeout /t 5 /nobreak >nul


echo [3/17] Starting Router Telegram 1...

start "NEXORA Router Telegram 1" cmd /k "python -m bots.command_router bot1_config.json"

timeout /t 5 /nobreak >nul


echo [4/17] Starting Router Telegram 2...

start "NEXORA Router Telegram 2" cmd /k "python -m bots.command_router bot2_config.json"

timeout /t 5 /nobreak >nul


echo [5/17] Starting File Worker...

start "NEXORA File Worker" cmd /k "python -m Core.file_worker"

timeout /t 5 /nobreak >nul


echo [6/17] Starting Partner Worker Telegram 1...

start "NEXORA Partner Worker Telegram 1" cmd /k "python -m Core.file_partner_worker bot1_config.json"

timeout /t 5 /nobreak >nul


echo [7/17] Starting Partner Worker Telegram 2...

start "NEXORA Partner Worker Telegram 2" cmd /k "python -m Core.file_partner_worker bot2_config.json"

timeout /t 5 /nobreak >nul


echo [8/17] Starting Lead Bot 1...

start "NEXORA Lead Bot 1" cmd /k "python -m bots.lead-demo"

timeout /t 5 /nobreak >nul


echo [9/17] Starting Lead Bot 2...

start "NEXORA Lead Bot 2" cmd /k "python -m bots.lead-demo2"

timeout /t 5 /nobreak >nul


echo [10/17] Starting WhatsApp Contact Worker 1...

start "NEXORA WhatsApp Contact Worker 1" cmd /k "python -m bots.contact_worker_wa whatsapp_bot1_config.json"

timeout /t 5 /nobreak >nul


echo [11/17] Starting WhatsApp Contact Worker 2...

start "NEXORA WhatsApp Contact Worker 2" cmd /k "python -m bots.contact_worker_wa whatsapp_bot2_config.json"

timeout /t 5 /nobreak >nul


echo [12/17] Starting WhatsApp Partner Worker 1...

start "NEXORA WhatsApp Partner Worker 1" cmd /k "python -m Core.file_partner_worker whatsapp_bot1_config.json"

timeout /t 5 /nobreak >nul


echo [13/17] Starting WhatsApp Partner Worker 2...

start "NEXORA WhatsApp Partner Worker 2" cmd /k "python -m Core.file_partner_worker whatsapp_bot2_config.json"

timeout /t 5 /nobreak >nul


echo [14/17] Starting WhatsApp Bot 1...

start "NEXORA WhatsApp Bot 1" cmd /k "python -m bots.demo_lead_1_wa"

timeout /t 5 /nobreak >nul


echo [15/17] Starting WhatsApp Bot 2...

start "NEXORA WhatsApp Bot 2" cmd /k "python -m bots.demo_lead_2_wa"

timeout /t 5 /nobreak >nul


echo [16/17] Starting Router WhatsApp 1...

start "NEXORA Router WhatsApp 1" cmd /k "python -m bots.command_router whatsapp_bot1_config.json"

timeout /t 5 /nobreak >nul


echo [17/17] Starting Router WhatsApp 2...

start "NEXORA Router WhatsApp 2" cmd /k "python -m bots.command_router whatsapp_bot2_config.json"

timeout /t 5 /nobreak >nul


echo.
echo ========================================
echo       NEXORA SERVER STARTED
echo       17 PROCESSES RUNNING
echo       TELEGRAM + WHATSAPP ENABLED
echo ========================================
echo.

pause