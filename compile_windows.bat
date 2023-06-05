@echo off

REM Set variable data
set APP=to_do_app.py
set NAME="To Do App"
set VERSION="1.0"
set DESCRIPTION="To Do List"
set COPYRIGHT="kiesus"

REM Compile Command
flet pack %APP% ^
  --product-name=%NAME% ^
  --product-version=%VERSION% ^
  --file-description=%DESCRIPTION% ^
  --copyright=%COPYRIGHT%

REM Check if the compilation is successful
if %errorlevel% equ 0 (
  echo Compilation completed.

  REM Ask user to launch compiled file
  set /p launch=Do you want to launch the compiled file? (Y/N): 

  REM Check user's input
  if /i "%launch%"=="Y" (
    REM Launch the compiled file
    start dist\to_do_app.exe
  ) else if /i "%launch%"=="N" (
    REM Do nothing
  ) else (
    REM Invalid input
    echo Invalid input. No action taken.
  )
) else (
  echo Compilation failed.
)

