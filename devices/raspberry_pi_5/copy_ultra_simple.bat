@echo off
setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "SRC=%SCRIPT_DIR%\rplidar-sdk\output\Linux\Release\ultra_simple"
set "DST1=%SCRIPT_DIR%\go\output\bin\tests\bin"
set "DST2=%SCRIPT_DIR%\go\output\bin\main\bin"

echo Copy Slamtec ultra_simple program from rplidar-sdk folder to output binary folders...

if not exist "%SRC%" (
    echo Source file not found: %SRC%
    exit /b 0
)

for %%D in ("%DST1%" "%DST2%") do (
    if not exist "%%D" (
        echo Destination directory not found: %%D, creating it.
        mkdir "%%D"
    )
)

copy "%SRC%" "%DST1%"
copy "%SRC%" "%DST2%"
echo Done.