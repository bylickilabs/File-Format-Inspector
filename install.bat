@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title BYLICKILABS File Format Inspector - Installation

where py >nul 2>nul
if not errorlevel 1 (
  set "PY_LAUNCHER=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden. Python 3.11 oder neuer installieren.
    pause
    exit /b 1
  )
  set "PY_LAUNCHER=python"
)
%PY_LAUNCHER% -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
  echo [FEHLER] Python 3.11 oder neuer wird benoetigt.
  echo.
  pause
  exit /b 1
)

%PY_LAUNCHER% -m venv .venv
if errorlevel 1 (
  echo [FEHLER] Die virtuelle Python-Umgebung konnte nicht erstellt werden.
  echo.
  pause
  exit /b 1
)
"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo [WARNUNG] pip-Upgrade nicht erfolgreich. Paketinstallation wird dennoch versucht.
)
"%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
  echo [FEHLER] Installation der Abhaengigkeiten fehlgeschlagen.
  echo Pruefen Sie die angezeigte pip-Fehlermeldung sowie die Internetverbindung.
  echo.
  pause
  exit /b 1
)
"%~dp0.venv\Scripts\python.exe" -c "import PySide6, numpy, scipy; print('Paketpruefung erfolgreich / Dependency check passed.')"
if errorlevel 1 (
  echo [FEHLER] Die installierten Python-Pakete konnten nicht geladen werden.
  echo.
  pause
  exit /b 1
)
echo.
echo Installation erfolgreich. Bitte start.bat ausfuehren.
pause
exit /b 0
