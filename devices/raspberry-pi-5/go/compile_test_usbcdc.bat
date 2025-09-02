@echo off
setlocal

REM Absolute path of this script's directory (trailing backslash preserved)
set "SCRIPT_DIR=%~dp0"

REM Path to the source directory and output directory
set "SOURCE_DIR=%SCRIPT_DIR%cmd\tests\usbcdc"
set "OUTPUT_DIR=%SCRIPT_DIR%output\bin\tests"

REM Check go availability
where go >nul 2>&1
if errorlevel 1 (
  echo Error: go not found in PATH.
  exit /b 1
)

REM Ensure source directory exists
if not exist "%SOURCE_DIR%" (
  echo Error: Source directory not found: %SOURCE_DIR%
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

echo Compiling Go test program for USB-CDC...

go build -o "%OUTPUT_DIR%\usbcdc.exe" "%SOURCE_DIR%"
if errorlevel 1 (
  echo Error: Build failed.
  exit /b 1
)

echo Done.
endlocal