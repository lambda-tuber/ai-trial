@echo off
rem ==========================================
rem Get current mouse position and scale by target width
rem ==========================================

rem 引数で最大幅を受け取る
set maxWidth=%1

rem PowerShell に渡す
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\mousepoint.ps1" %maxWidth%
