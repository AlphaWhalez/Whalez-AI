@echo off
for /f "tokens=14" %%a in ('ipconfig ^| findstr /i "IPv4"') do set LANIP=%%a
echo LAN IPv4: %LANIP%
