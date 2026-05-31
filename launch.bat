@echo off
REM Double-click me to start Khor Bros Menu Maker.
cd /d "%~dp0"

if not exist KhorBrosMenu.exe (
    echo Could not find KhorBrosMenu.exe next to this launcher.
    echo Make sure both files are in the same folder.
) else (
    KhorBrosMenu.exe
)

echo.
pause
