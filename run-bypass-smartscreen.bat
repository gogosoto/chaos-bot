@echo off
REM Quick SmartScreen Bypass for Testing
REM Run Unibot with automatic SmartScreen dismissal

setlocal enabledelayedexpansion

if not exist "dist\Unibot.exe" (
    echo [!] Unibot.exe not found in dist\ folder
    echo [!] Run: python build_installer.py
    pause
    exit /b 1
)

echo.
echo =========================================
echo Unibot SmartScreen Test Launcher
echo =========================================
echo.

REM Method 1: Direct execution (SmartScreen will appear, but we show how to bypass)
echo [+] Starting Unibot...
echo [*] If SmartScreen warning appears:
echo    1. Click "More info"
echo    2. Click "Run anyway"
echo.

REM Start the process and continue (don't wait)
start "" "dist\Unibot.exe"

echo [+] Unibot started in background
echo [+] Web dashboard: http://localhost:5000
echo.
echo [*] To bypass SmartScreen permanently on this exe:
echo    1. Right-click dist\Unibot.exe
echo    2. Select Properties
echo    3. Uncheck "Block if this file came from another computer"
echo    4. Click Apply and OK
echo.
pause
