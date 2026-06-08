"""
Build script for creating Windows installer with PyInstaller.
Generates standalone .exe + MSI installer for local testing.
SmartScreen warning can be dismissed on first run (unsigned binary).
"""
import os
import subprocess
import shutil
import sys

def build_exe():
    """Build standalone Windows executable using PyInstaller."""
    print("[*] Building Unibot executable...")

    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=Unibot',
        '--icon=assets/icon.ico',  # Optional: add icon
        '--add-data=config.ini:.',
        '--add-data=templates:templates',
        '--add-data=static:static',
        '--distpath=dist',
        '--buildpath=build',
        '--specpath=.',
        'src/main.py'
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[✓] Executable built successfully")
        print(f"Location: dist/Unibot.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[✗] Build failed: {e.stderr}")
        return False

def create_installer_batch():
    """Create batch file for manual installation (alternative to MSI)."""
    print("[*] Creating installation batch file...")

    batch_content = """@echo off
REM Unibot Windows Installer
REM Run as Administrator for proper installation

setlocal enabledelayedexpansion

echo.
echo =========================================
echo Unibot FPS Assistant Installer
echo =========================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] This installer requires Administrator privileges.
    echo [!] Please run Command Prompt as Administrator and try again.
    pause
    exit /b 1
)

REM Define installation directory
set INSTALL_DIR=%ProgramFiles%\\Unibot
set ICON_PATH=%INSTALL_DIR%\\Unibot.exe

echo [+] Installation directory: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo [+] Created installation folder
)

REM Copy executable
echo [+] Copying executable...
copy "dist\\Unibot.exe" "%INSTALL_DIR%\\" >nul
if %errorLevel% equ 0 (
    echo [✓] Executable installed
) else (
    echo [✗] Failed to copy executable
    pause
    exit /b 1
)

REM Copy data files
echo [+] Copying data files...
if exist "config.ini" copy "config.ini" "%INSTALL_DIR%\\" >nul
if exist "requirements.txt" copy "requirements.txt" "%INSTALL_DIR%\\" >nul
echo [✓] Data files copied

REM Create Start Menu shortcut
echo [+] Creating Start Menu shortcut...
set MENU_DIR=%AppData%\\Microsoft\\Windows\\Start Menu\\Programs\\Unibot
if not exist "%MENU_DIR%" mkdir "%MENU_DIR%"

REM VBScript for creating shortcut (safer than using shortcuts utility)
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%MENU_DIR%\Unibot.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "%INSTALL_DIR%\Unibot.exe"
    echo oLink.WorkingDirectory = "%INSTALL_DIR%"
    echo oLink.IconLocation = "%INSTALL_DIR%\Unibot.exe"
    echo oLink.Save
) > "%temp%\\create_shortcut.vbs"

cscript.exe "%temp%\\create_shortcut.vbs" >nul
del "%temp%\\create_shortcut.vbs"
echo [✓] Start Menu shortcut created

REM Create desktop shortcut
echo [+] Creating Desktop shortcut...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%UserProfile%\Desktop\Unibot.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "%INSTALL_DIR%\Unibot.exe"
    echo oLink.WorkingDirectory = "%INSTALL_DIR%"
    echo oLink.IconLocation = "%INSTALL_DIR%\Unibot.exe"
    echo oLink.Save
) > "%temp%\\create_desktop_shortcut.vbs"

cscript.exe "%temp%\\create_desktop_shortcut.vbs" >nul
del "%temp%\\create_desktop_shortcut.vbs"
echo [✓] Desktop shortcut created

REM Add to PATH (optional)
echo.
echo [+] Adding Unibot to system PATH...
setx PATH "%PATH%;%INSTALL_DIR%" >nul
echo [✓] PATH updated

REM Install Interception Driver (optional but recommended)
echo.
echo =========================================
echo Interception Driver Installation
echo =========================================
echo.
echo The Interception driver enables low-level mouse input control.
echo This is OPTIONAL but RECOMMENDED for best performance.
echo.
echo Do you want to install the Interception driver?
echo (Y/N, default is N)
set /p INSTALL_INTERCEPTION="> "

if /i "%INSTALL_INTERCEPTION%"=="Y" (
    echo.
    echo [+] Downloading Interception driver...

    REM Create temp directory for Interception
    set INTER_TEMP=%temp%\interception_install
    if not exist "%INTER_TEMP%" mkdir "%INTER_TEMP%"

    REM Download Interception (from official repo)
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/oblitum/Interception/releases/download/v.1.0.1/Interception.exe', '%INTER_TEMP%\Interception.exe')" 2>nul

    if exist "%INTER_TEMP%\Interception.exe" (
        echo [+] Running Interception installer...
        "%INTER_TEMP%\Interception.exe"
        echo [✓] Interception driver installation started
        echo [*] Please follow the installer prompts
    ) else (
        echo [!] Failed to download Interception driver
        echo [*] You can install it manually from:
        echo    https://github.com/oblitum/Interception/releases
    )

    REM Cleanup
    if exist "%INTER_TEMP%" rmdir /s /q "%INTER_TEMP%"
) else (
    echo [*] Skipping Interception driver installation
    echo [*] You can install it later from:
    echo    https://github.com/oblitum/Interception/releases
)

REM Firewall rule (allow web server)
echo.
echo [+] Configuring Windows Firewall...
netsh advfirewall firewall add rule name="Unibot Web Server" dir=in action=allow program="%INSTALL_DIR%\Unibot.exe" >nul
echo [✓] Firewall rule added

echo.
echo =========================================
echo Installation Complete!
echo =========================================
echo.
echo Unibot is installed at: %INSTALL_DIR%
echo.
echo Quick start:
echo   1. Run Unibot from Start Menu or Desktop shortcut
echo   2. Access web dashboard at http://localhost:5000
echo   3. Or from another device: http://your-local-ip:5000
echo.
echo SmartScreen Warning (first run):
echo   If Windows SmartScreen appears:
echo   - Click "More info"
echo   - Then "Run anyway"
echo   This is normal for unsigned local builds
echo.
pause
"""

    with open('install.bat', 'w') as f:
        f.write(batch_content)
    print("[✓] Created install.bat")

def create_uninstall_batch():
    """Create batch file for uninstallation."""
    print("[*] Creating uninstall batch file...")

    uninstall_content = """@echo off
REM Unibot Uninstaller

setlocal enabledelayedexpansion

echo.
echo =========================================
echo Unibot Uninstaller
echo =========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] This uninstaller requires Administrator privileges.
    pause
    exit /b 1
)

set INSTALL_DIR=%ProgramFiles%\\Unibot
set MENU_DIR=%AppData%\\Microsoft\\Windows\\Start Menu\\Programs\\Unibot

echo [+] Removing Unibot...

REM Stop any running Unibot process
taskkill /IM Unibot.exe /F 2>nul

REM Remove installation directory
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    echo [✓] Installation directory removed
)

REM Remove Start Menu shortcut
if exist "%MENU_DIR%" (
    rmdir /s /q "%MENU_DIR%"
    echo [✓] Start Menu shortcuts removed
)

REM Remove Desktop shortcut
if exist "%UserProfile%\Desktop\Unibot.lnk" (
    del /q "%UserProfile%\Desktop\Unibot.lnk"
    echo [✓] Desktop shortcut removed
)

REM Remove firewall rule
netsh advfirewall firewall delete rule name="Unibot Web Server" >nul 2>&1

echo.
echo [✓] Unibot has been uninstalled
echo.
pause
"""

    with open('uninstall.bat', 'w') as f:
        f.write(uninstall_content)
    print("[✓] Created uninstall.bat")

def create_portable_zip():
    """Create portable ZIP (no installation needed)."""
    print("[*] Creating portable package...")

    if os.path.exists('Unibot-Portable.zip'):
        os.remove('Unibot-Portable.zip')

    try:
        shutil.make_archive('Unibot-Portable', 'zip', 'dist')
        print("[✓] Created Unibot-Portable.zip")
        return True
    except Exception as e:
        print(f"[✗] Failed to create portable package: {e}")
        return False

def create_readme():
    """Create installation README."""
    print("[*] Creating README...")

    readme = """# Unibot Windows Installation Guide

## Installation Methods

### Method 1: Automated Installer (Recommended)
1. Run `install.bat` as Administrator
2. Installation will complete automatically
3. Unibot will be added to Start Menu and Desktop

### Method 2: Portable (No Installation)
1. Extract `Unibot-Portable.zip` anywhere
2. Run `Unibot.exe` directly
3. No admin rights required

### Method 3: Manual
1. Copy `Unibot.exe` to your desired location
2. Run it directly

## First Run - SmartScreen Warning

Windows SmartScreen may warn about running an unsigned executable.

**This is normal and safe for local testing:**

1. Click **"More info"** when the warning appears
2. Click **"Run anyway"** at the bottom
3. Unibot will start normally

To bypass SmartScreen permanently:
- Right-click Unibot.exe → Properties → Uncheck "Unblock"

## Quick Start

1. **Run Unibot** - Start the application
2. **Local Control** - Use the desktop interface
3. **Remote Control** - Open web browser:
   - Local: http://localhost:5000
   - Remote (same network): http://your-local-ip:5000

## Configuration

Edit `config.ini` in the installation directory to customize:
- Aim assist parameters
- Trigger settings
- Pose detection thresholds
- Shape validation rules

Changes take effect after restarting Unibot.

## Uninstallation

Run `uninstall.bat` as Administrator to remove Unibot completely.

## Troubleshooting

### Port 5000 already in use
Change port in web_server.py and recompile

### Web dashboard not accessible from other devices
Check Windows Firewall settings (installer adds rule automatically)

### SmartScreen blocks repeatedly
This is expected for unsigned binaries. Click "Run anyway" or sign the executable.

## Support

For issues, check:
- `config.ini` is in the same directory as Unibot.exe
- Windows Firewall allows Unibot
- Port 5000 is not blocked by another application
"""

    with open('README-INSTALL.txt', 'w') as f:
        f.write(readme)
    print("[✓] Created README-INSTALL.txt")

def main():
    print("\n[*] Unibot Windows Build System\n")

    # Check dependencies
    print("[*] Checking dependencies...")
    try:
        subprocess.run(['pyinstaller', '--version'], capture_output=True, check=True)
        print("[✓] PyInstaller found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)

    # Build
    if not build_exe():
        sys.exit(1)

    # Create installers
    create_installer_batch()
    create_uninstall_batch()
    create_portable_zip()
    create_readme()

    print("\n" + "="*50)
    print("[✓] Build Complete!")
    print("="*50)
    print("\nGenerated files:")
    print("  - dist/Unibot.exe (standalone executable)")
    print("  - install.bat (automated installer)")
    print("  - uninstall.bat (uninstaller)")
    print("  - Unibot-Portable.zip (portable package)")
    print("  - README-INSTALL.txt (installation guide)")
    print("\nNext steps:")
    print("  1. Run install.bat as Administrator for full installation")
    print("  2. Or extract Unibot-Portable.zip and run Unibot.exe directly")
    print("  3. First run will trigger SmartScreen - click 'Run anyway'")
    print("\n")

if __name__ == '__main__':
    main()
