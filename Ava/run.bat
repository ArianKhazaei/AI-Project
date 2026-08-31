@echo off
setlocal EnableExtensions

cls

set "ROOT=%~dp0"
set "FRONTEND_DIR=%ROOT%frontend"
set "REQUIREMENTS_FILE=%ROOT%requirements.txt"
set "SETUP_MARKER=%ROOT%.ava_setup_done"
set "VENV_DIR=%ROOT%.venv"
set "ENV_FILE=%ROOT%.env"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"

echo ========================================
echo                 AVA
echo ========================================
echo.

echo [1/7] Checking Python...

where python >nul 2>nul

if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo ERROR: Python was not found.
        echo Please install Python 3.11 or newer.
        pause
        exit /b 1
    )
    set "PY_CMD=py -3"
) else (
    set "PY_CMD=python"
)

call %PY_CMD% --version

if errorlevel 1 (
    echo ERROR: Python could not be executed.
    pause
    exit /b 1
)

echo.

echo [2/7] Checking .env...

if not exist "%ENV_FILE%" (
    echo ERROR: .env file was not found.
    pause
    exit /b 1
)

echo .env OK
echo.

echo [3/7] Checking requirements.txt...

if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: requirements.txt was not found.
    pause
    exit /b 1
)

echo requirements.txt OK
echo.

if not exist "%FRONTEND_DIR%" (
    echo ERROR: frontend directory was not found.
    pause
    exit /b 1
)

echo frontend OK
echo.

echo [4/7] Checking Virtual Environment...

if not exist "%PYTHON%" (
    echo Creating Virtual Environment...
    call %PY_CMD% -m venv "%VENV_DIR%"

    if errorlevel 1 (
        echo ERROR: Could not create Virtual Environment.
        pause
        exit /b 1
    )
)

if not exist "%PYTHON%" (
    echo ERROR: Virtual Environment Python was not found.
    pause
    exit /b 1
)

"%PYTHON%" --version
echo.

echo [5/7] Checking dependencies...

"%PYTHON%" -m pip install -r "%REQUIREMENTS_FILE%"

if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed.
    pause
    exit /b 1
)

echo Dependencies OK.
echo.

echo [6/7] Checking Backend...

"%PYTHON%" -c "import backend.main; print('BACKEND_IMPORT_OK')"

if errorlevel 1 (
    echo.
    echo ERROR: Backend import failed.
    pause
    exit /b 1
)

echo Backend import OK.
echo.

echo Starting Backend...

start "AVA Backend" "%PYTHON%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

echo Backend process started.
echo.

echo Waiting for Backend...

set "BACKEND_READY="

for /L %%i in (1,1,20) do (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r=Invoke-WebRequest -Uri 'http://127.0.0.1:8000/docs' -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

    if not errorlevel 1 (
        set "BACKEND_READY=1"
        goto BACKEND_OK
    )

    timeout /t 1 /nobreak >nul
)

:BACKEND_OK

if not defined BACKEND_READY (
    echo ERROR: Backend did not become ready.
    pause
    exit /b 1
)

echo Backend is READY.
echo.

echo [7/7] Starting Frontend...

start "AVA Frontend" "%PYTHON%" -m http.server 5500 --directory "%FRONTEND_DIR%"

echo Frontend process started.
echo.

timeout /t 2 /nobreak >nul

start "" "http://127.0.0.1:5500/index.html"

echo.
echo ========================================
echo             AVA IS RUNNING
echo ========================================
echo.
echo Backend : http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:5500
echo.

endlocal
exit /b 0
