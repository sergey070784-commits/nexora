@echo off

echo ========================================
echo       NEXORA SERVER STOP
echo ========================================
echo.

powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'bots.memory_data|bots.contact_worker|bots.command_router|Core.file_worker|Core.file_partner_worker|bots.user_text_specialist|bots.lead-demo|bots.lead-demo2|bots.demo_lead_1_wa|bots.demo_lead_2_wa' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

echo.
echo ========================================
echo       NEXORA SERVER STOPPED
echo       TELEGRAM + WHATSAPP STOPPED
echo       SPECIALISTS 1-6 STOPPED
echo ========================================
echo.

pause