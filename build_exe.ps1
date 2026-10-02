# Build a standalone Windows executable with PyInstaller.
# Usage:  pip install pyinstaller ; .\build_exe.ps1
pyinstaller --onefile --windowed --name "MythoskullPayloadBuilder" payload_builder.py
Write-Host "Done. Executable is in .\dist\MythoskullPayloadBuilder.exe"
