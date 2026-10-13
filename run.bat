@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  HIPPO PRODUCT JOURNAL
 echo ======================
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version
if errorlevel 1 goto no_python
if not exist .venv\Scripts\python.exe (
 echo Creating virtual environment...
 %PY% -m venv .venv
 if errorlevel 1 goto fail
)
echo Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo.
echo Starting Hippo Product Journal at http://127.0.0.1:5000
start "" http://127.0.0.1:5000/
.venv\Scripts\python.exe app.py
pause
goto end
:no_python
echo Python was not found. Install Python 3.10+ from https://www.python.org/downloads/ and enable Add Python to PATH.
pause
goto end
:fail
echo Setup failed. Check the messages above. Internet access is required for first-time package installation.
pause
:end
