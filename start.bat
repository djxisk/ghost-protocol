@echo off
cd /d "%~dp0"
if not defined GHQ_HOST set GHQ_HOST=127.0.0.1
if not defined GHQ_PORT set GHQ_PORT=18788
python server.py
pause
