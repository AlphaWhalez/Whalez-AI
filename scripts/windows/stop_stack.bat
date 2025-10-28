@echo off
echo [*] Stopping Whalez-AI stack...
taskkill /FI "WINDOWTITLE eq whalez-backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq whalez-web*" /F >nul 2>&1
for /f "tokens=2 delims==:" %%p in ('wmic process where "CommandLine like '%%vite preview%%'" get ProcessId /value ^| find "="') do taskkill /PID %%p /F >nul 2>&1
echo [*] Done.
