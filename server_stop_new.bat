@echo off

echo ========================================
echo       NEXORA SERVER STOP
echo ========================================
echo.

powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'bots.memory_data|bots.contact_worker|bots.command_router|Core.file_worker|Core.file_partner_worker|bots.lead-demo|bots.lead-demo2' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

echo.
echo ========================================
echo       NEXORA SERVER STOPPED
echo       WHATSAPP WAS NOT STARTED
echo ========================================
echo.

pause