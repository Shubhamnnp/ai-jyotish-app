@echo off
REM Batch Verification Script for JyotishOS (Phase U0, Task U0-T4)
cd /d "%~dp0\.."
py -3 scripts\verify.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Verification failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
