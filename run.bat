@echo off
REM Mythoskull Payload Builder launcher
where python >nul 2>&1 && (python payload_builder.py & goto :eof)
where py >nul 2>&1 && (py payload_builder.py & goto :eof)
echo Python was not found. Install Python 3.8+ from https://www.python.org/downloads/ (check "Add to PATH").
pause
