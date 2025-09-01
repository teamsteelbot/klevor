@echo off
setlocal

REM Absolute path of this script's directory (trailing backslash preserved)
set "SCRIPT_DIR=%~dp0"

REM Path to the main.go
set "MAIN_GO=%SCRIPT_DIR%cmd\main\main.go"

REM Check tinygo availability
where tinygo >nul 2>&1
if errorlevel 1 (
  echo Error: tinygo not found in PATH.
  exit /b 1
)

REM Ensure source file exists
if not exist "%MAIN_GO%" (
  echo Error: Main file not found: %MAIN_GO%
  exit /b 1
)

echo Compiling and flashing TinyGo program to Raspberry Pi Pico 2W...

tinygo flash -target pico2-w "%MAIN_GO%"
if errorlevel 1 (
  echo Error: Flash failed.
  exit /b 1
)

echo Done.
endlocal