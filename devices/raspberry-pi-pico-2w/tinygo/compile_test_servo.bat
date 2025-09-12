@echo off
setlocal

REM Absolute path of this script's directory (trailing backslash preserved)
set "SCRIPT_DIR=%~dp0"

REM Path to the test main.go and output file
set "MAIN_GO=%SCRIPT_DIR%cmd\tests\servo\main.go"
set "OUTPUT_DIR=%SCRIPT_DIR%output\bin\tests\servo"
set "OUTPUT_FILE=%OUTPUT_DIR%\flash.uf2"

REM Check tinygo availability
where tinygo >nul 2>&1
if errorlevel 1 (
  echo Error: tinygo not found in PATH.
  exit /b 1
)

REM Ensure source file exists
if not exist "%MAIN_GO%" (
  echo Error: Test file not found: %MAIN_GO%
  exit /b 1
)

REM Ensure output directory exists
if not exist "%OUTPUT_DIR%" (
  mkdir "%OUTPUT_DIR%"
  if errorlevel 1 (
    echo Error: Failed to create output directory: %OUTPUT_DIR%
    exit /b 1
  )
)

echo Compiling TinyGo Servo test...

tinygo build -o="%OUTPUT_FILE%" -target=pico2-w -size=full -print-allocs=. "%MAIN_GO%"
if errorlevel 1 (
  echo Error: Compilation failed.
  exit /b 1
)

echo Done.
endlocal