@echo off
chcp 65001 >nul
cls

cd /d "%~dp0"

echo ==========================================
echo              AVA RESET
echo ==========================================
echo.
echo WARNING:
echo All users, lessons, attempts and database
echo data will be permanently deleted.
echo PDF and audio files will also be deleted.
echo.
echo Project source code and .env will NOT
echo be deleted.
echo.

choice /C YN /N /M "Are you sure? [Y/N]: "

if errorlevel 2 (
    cls
    echo Reset cancelled.
    pause
    exit /b 0
)

cls

echo ==========================================
echo          RESETTING AVA
echo ==========================================
echo.

if exist "ava.db" (
    del /f /q "ava.db"
    echo [OK] Database deleted.
) else (
    echo [--] Database not found.
)

if exist "audio" (
    del /f /q "audio\*.mp3" 2>nul
    echo [OK] Audio files deleted.
) else (
    echo [--] Audio folder not found.
)

if exist "notes" (
    del /f /q "notes\*.pdf" 2>nul
    echo [OK] PDF files deleted.
) else (
    echo [--] Notes folder not found.
)

echo.
echo ==========================================
echo            RESET COMPLETE
echo ==========================================
echo.
echo AVA is now in a fresh state.
echo.

pause
