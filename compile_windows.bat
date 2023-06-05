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
  
