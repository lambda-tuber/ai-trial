@echo off
chcp 65001 >nul

if "%~3"=="" (
    echo Usage: %~nx0 YEAR MONTH ACCOUNT_NAME
    exit /b 1
)

set "YEAR=%~1"
set "MONTH_RAW=%~2"
set "ACCOUNT=%~3"

set "JOURNAL_DIR=C:\Users\lambda-tuber\Desktop\data"

set "MM=0%MONTH_RAW%"
set "MM=%MM:~-2%"

set /a sum_dr=0
set /a sum_cr=0

set "dir_dr=%JOURNAL_DIR%\%YEAR%\%MM%\%ACCOUNT%\dr"
set "dir_cr=%JOURNAL_DIR%\%YEAR%\%MM%\%ACCOUNT%\cr"

if exist "%dir_dr%" (
    for /f "tokens=3" %%A in ('dir /s /-c "%dir_dr%" ^| find "File(s)"') do (
        set /a sum_dr=%%A
    )
)

if exist "%dir_cr%" (
    for /f "tokens=3" %%A in ('dir /s /-c "%dir_cr%" ^| find "File(s)"') do (
        set /a sum_cr=%%A
    )
)

set /a balance=sum_dr - sum_cr

if %balance% gtr 0 (
    set "balance_side=debit"
    set "balance_value=%balance%"
) else if %balance% lss 0 (
    set "balance_side=credit"
    set /a balance_value=-balance
) else (
    set "balance_side=none"
    set "balance_value=0"
)

echo {
echo   "account": "%ACCOUNT%",
echo   "debit": %sum_dr%,
echo   "credit": %sum_cr%,
echo   "balance": {
echo     "side": "%balance_side%",
echo     "value": %balance_value%
echo   }
echo }

exit /b 0
