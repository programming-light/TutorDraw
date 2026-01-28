@echo off
REM Build script for Windows
echo Building TutorDraw for Windows...

REM Install required packages
pip install pyinstaller pyside6

REM Build executable
pyinstaller --onefile --windowed --icon=src/tutorDraw-logoX92.png --add-data "src;tutorDraw/src" --name "TutorDraw" main.py

echo Windows build completed!
pause
