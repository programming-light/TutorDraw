#!/bin/bash
# Build script for Linux/macOS
echo "Building TutorDraw for Linux/macOS..."

# Install required packages
pip install pyinstaller pyside6

# Build executable
pyinstaller --onefile --windowed --icon=src/tutorDraw-logoX92.png --add-data "src:tutorDraw/src" --name "TutorDraw" main.py

echo "Linux/macOS build completed!"
