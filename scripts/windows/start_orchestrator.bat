@echo off
setlocal enabledelayedexpansion

pushd %~dp0\..
set ROOT=%CD%\..
cd %ROOT%

set PYTHONPATH=%CD%

set LOOP=%GOVERNANCE_LOOP_INTERVAL%
if "%LOOP%"=="" set LOOP=30

set EXEC_FLAG=
if "%GOVERNANCE_EXECUTE%"=="1" set EXEC_FLAG=--execute

python -m core.controllers.orchestrator --loop %LOOP% %EXEC_FLAG% %*
popd
