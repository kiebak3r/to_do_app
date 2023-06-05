@echo off

set APP=to_do_app.py
set NAME="To Do App"
set VERSION="1.0"
set DESCRIPTION="To Do List"
set CR="kiesus"

flet pack %APP% --product-name=%NAME% --product-version=%VERSION% --file-description=%DESCRIPTION% --copyright=%CR%
