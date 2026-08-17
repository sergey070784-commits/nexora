@echo off
cd /d C:\Users\server\Documents\project\nexora

echo ========================================
echo       NEXORA SERVER START
echo       13 PROCESSES
echo ========================================
echo.

REM ===== CORE =====
start "NEXORA Memory Data" cmd /k "python -m bots.memory_data"
start "NEXORA Contact Worker" cmd /k "python -m bots.contact_worker"

REM ===== COMMAND ROUTERS =====
REM Commands are handled through command_router configs.
REM No separate command process is needed.
start "NEXORA Router Telegram 1" cmd /k "python -m bots.command_router bot1_config.json"
start "NEXORA Router Telegram 2" cmd /k "python -m bots.command_router bot2_config.json"
start "NEXORA Router WhatsApp 1" cmd /k "python -m bots.command_router whatsapp_bot1_config.json"
start "NEXORA Router WhatsApp 2" cmd /k "python -m bots.command_router whatsapp_bot2_config.json"

REM ===== FILE SYSTEM =====
start "NEXORA File Worker" cmd /k "python -m Core.file_worker"
start "NEXORA Partner Worker Bot 1" cmd /k "python -m Core.file_partner_worker bot1_config.json"
start "NEXORA Partner Worker Bot 2" cmd /k "python -m Core.file_partner_worker bot2_config.json"

REM ===== BOTS =====
start "NEXORA Lead Bot 1" cmd /k "python -m bots.lead-demo"
start "NEXORA Lead Bot 2" cmd /k "python -m bots.lead-demo2"
start "NEXORA WhatsApp Bot 1" cmd /k "python -m bots.demo_lead_1_wa"
start "NEXORA WhatsApp Bot 2" cmd /k "python -m bots.demo_lead_2_wa"

echo.
echo ========================================
echo   NEXORA SERVER STARTED
echo   13 PROCESSES
echo ========================================
pause
