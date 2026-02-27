@echo off
title Keda1021 Exam Tool Builder

set APP_NAME=shuffled

echo Closing running application...
taskkill /f /im %APP_NAME%.exe >nul 2>&1

echo Cleaning old build artifacts...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist %APP_NAME%.spec del /q %APP_NAME%.spec

echo.
echo Activating virtual environment and starting build...

call .venv\Scripts\activate.bat

echo.
echo Executing PyInstaller for %APP_NAME%.py...
python -m PyInstaller --noconsole --onefile --clean --collect-all customtkinter %APP_NAME%.py

echo.
echo ===========================================
echo DONE! Opening 'dist' folder...
echo ===========================================

start "" "dist"
pause