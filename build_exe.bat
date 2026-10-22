@echo off
cd /d "%~dp0"
py -3 -m pip install --upgrade pyinstaller
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name AfnanDawakhana main.py
echo.
echo Build complete. EXE should be in the dist folder.
pause
