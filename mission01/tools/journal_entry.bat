@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

set "DR_ACCOUNT=%~1"
set "CR_ACCOUNT=%~2"
set "AMOUNT=%~3"
set "REMARK=%~4"
set "YEAR=%~5"
set "MONTH=%~6"
set "DAY=%~7"
set "HOUR=%~8"
set "MIN=%~9"
shift & shift & shift & shift & shift & shift & shift & shift & shift
set "SEC=%~1"

for /f %%a in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMddHHmmss\")"') do set "DATETIME=%%a"
if "%YEAR%"==""  set "YEAR=!DATETIME:~0,4!"
if "%MONTH%"=="" set "MONTH=!DATETIME:~4,2!"
if "%DAY%"==""   set "DAY=!DATETIME:~6,2!"
if "%HOUR%"==""  set "HOUR=!DATETIME:~8,2!"
if "%MIN%"==""   set "MIN=!DATETIME:~10,2!"
if "%SEC%"==""   set "SEC=!DATETIME:~12,2!"

for /f %%i in ('powershell -NoProfile -Command "[guid]::NewGuid().ToString()"') do set "UUID=%%i"

if not "%REMARK%"=="" (
  for /f "usebackq delims=" %%S in (`powershell -NoProfile -Command "$env:REMARK -replace '[\\/:*?\""<>|= ]','_'"`) do set "SAFE_REMARK=%%S"
  set "TIMESTAMP=!YEAR!!MONTH!!DAY!!HOUR!!MIN!!SEC!.!UUID!_!SAFE_REMARK!"
) else (
  set "TIMESTAMP=!YEAR!!MONTH!!DAY!!HOUR!!MIN!!SEC!.!UUID!"
)

set "BASE_DIR=C:\Users\lambda-tuber\Desktop\data"
set "DR_DIR=%BASE_DIR%\%YEAR%\%MONTH%\%DR_ACCOUNT%"
set "CR_DIR=%BASE_DIR%\%YEAR%\%MONTH%\%CR_ACCOUNT%"

mkdir "%DR_DIR%\dr" 2>nul
mkdir "%DR_DIR%\cr" 2>nul
mkdir "%CR_DIR%\dr" 2>nul
mkdir "%CR_DIR%\cr" 2>nul

set "DR_FILE=%DR_DIR%\dr\%TIMESTAMP%"
set "CR_FILE=%CR_DIR%\cr\%TIMESTAMP%"
fsutil file createnew "%DR_FILE%" %AMOUNT% > nul
fsutil file createnew "%CR_FILE%" %AMOUNT% > nul

echo {
echo   "status": "success",
echo   "year": "%YEAR%",
echo   "month": "%MONTH%",
echo   "amount": %AMOUNT%,
echo   "dr_account": "%DR_ACCOUNT%",
echo   "cr_account": "%CR_ACCOUNT%",
echo   "dr_file": "%DR_FILE%",
echo   "cr_file": "%CR_FILE%"
echo }

set "LOG_FILE=journal_entry.csv"
if not exist "%LOG_FILE%" (
  echo datetime,dr_account,cr_account,amount,year,month,day,time,uuid,dr_file,cr_file>>"%LOG_FILE%"
)
set "NOW=%DATE% %TIME%"
echo "%NOW%","%DR_ACCOUNT%","%CR_ACCOUNT%","%AMOUNT%","%YEAR%","%MONTH%","%DAY%","%HOUR%%MIN%%SEC%","%UUID%","%DR_FILE%","%CR_FILE%">>"%LOG_FILE%"

endlocal
exit /b 0
