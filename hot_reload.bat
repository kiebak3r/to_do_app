@echo off

REM Launches Hot Reloader
python to_do_app.py ^
  --directory ^
  --recursive

REM Notify on close of Hot Reloader
echo Hot Reloader Closed.
