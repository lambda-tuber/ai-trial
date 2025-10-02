@echo off
rem ==========================================
rem 縮小付きスクショを取得してJSON出力
rem ==========================================

rem バッチの1番目の引数を PowerShell に渡す
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\screenshot.ps1" %1
