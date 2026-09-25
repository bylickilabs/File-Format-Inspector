@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title BYLICKILABS File Format Inspector - Start

set "APP_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%APP_PYTHON%" (
  echo [FEHLER] Die lokale Python-Umgebung fehlt.
  echo [ERROR] Python environment not found.
  echo.
  echo Bitte zuerst install.bat im entpackten Projektordner ausfuehren.
  echo Run install.bat in the extracted project directory first.
  echo.
  pause
  exit /b 1
)
if not exist "%~dp0file_format_inspector.py" (
  echo [FEHLER] Hauptdatei file_format_inspector.py nicht gefunden.
  echo Bitte das vollstaendige ZIP-Archiv entpacken.
  echo.
  pause
  exit /b 1
)

"%APP_PYTHON%" -c "import PySide6, numpy, scipy"
if errorlevel 1 (
  echo.
  echo [FEHLER] Mindestens ein erforderliches Python-Paket fehlt oder kann nicht geladen werden.
  echo Bitte install.bat ausfuehren und danach erneut starten.
  echo [ERROR] A required Python package is missing or could not be imported.
  echo.
  pause
  exit /b 1
)

"%APP_PYTHON%" "%~dp0file_format_inspector.py"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
  echo.
  echo [FEHLER] Die Anwendung wurde mit Fehlercode %EXIT_CODE% beendet.
  echo Bitte die oben angezeigte Python-Fehlermeldung pruefen.
  echo.
  pause
)
exit /b %EXIT_CODE%
