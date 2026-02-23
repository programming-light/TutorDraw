"""
Enhanced Build System for TutorDraw
Supports Windows, macOS, Linux, and Android builds with portable and installer options
"""
import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path
import argparse

def get_platform_info():
    """Get detailed platform information"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    arch = "64" if "64" in machine or "amd64" in machine or "x86_64" in machine else "32"
    
    return {
        "system": system,
        "architecture": arch,
        "machine": machine,
        "full_platform": platform.platform()
    }

def create_build_directory():
    """Create build directory structure"""
    build_dir = Path("build_dist")
    build_dir.mkdir(exist_ok=True)
    
    # Create platform-specific directories
    platforms = ["windows", "macos", "linux", "android"]
    for plat in platforms:
        (build_dir / plat).mkdir(exist_ok=True)
        (build_dir / plat / "portable").mkdir(exist_ok=True)
        (build_dir / plat / "installer").mkdir(exist_ok=True)
    
    return build_dir

def create_windows_build_scripts(build_dir):
    """Create Windows build scripts for portable and installer"""
    
    # Windows 64-bit Portable
    win64_portable_script = f'''@echo off
REM Build TutorDraw Windows 64-bit Portable
echo Building TutorDraw Windows 64-bit Portable...

REM Create working directory
set BUILD_DIR=%~dp0\\temp_win64
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

REM Copy source files
xcopy /E /I /Y ".\\src" "%BUILD_DIR%\\src"
copy ".\\main.py" "%BUILD_DIR%\\" >nul
copy ".\\tutordraw_settings.json" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\tutordraw_config.json" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\README.md" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\LICENSE" "%BUILD_DIR%\\" >nul 2>&1

REM Change to build directory
cd /d "%BUILD_DIR%"

REM Install required packages
pip install pyqt5 pyinstaller

REM Build portable executable
pyinstaller --onefile --windowed --clean --noconsole ^
    --icon="src\\\\tutorDraw-logoX92.png" ^
    --add-data="src;src" ^
    --name="TutorDraw-Win64-Portable" ^
    main.py

REM Create final distribution
if exist "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win64-Portable" rd /s /q "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win64-Portable"
mkdir "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win64-Portable"
xcopy /E /I /Y "dist\\\\TutorDraw-Win64-Portable.exe" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win64-Portable\\\\"
copy "README.md" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win64-Portable\\\\" >nul 2>&1
copy "tutordraw_settings.json" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win64-Portable\\\\" >nul 2>&1
copy "LICENSE" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win64-Portable\\\\" >nul 2>&1

REM Cleanup
cd /d "%~dp0"
rd /s /q "%BUILD_DIR%"

echo Windows 64-bit Portable build completed!
pause
'''

    # Windows 32-bit Portable
    win32_portable_script = f'''@echo off
REM Build TutorDraw Windows 32-bit Portable
echo Building TutorDraw Windows 32-bit Portable...

REM Create working directory
set BUILD_DIR=%~dp0\\temp_win32
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

REM Copy source files
xcopy /E /I /Y ".\\src" "%BUILD_DIR%\\src"
copy ".\\main.py" "%BUILD_DIR%\\" >nul
copy ".\\tutordraw_settings.json" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\tutordraw_config.json" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\README.md" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\LICENSE" "%BUILD_DIR%\\" >nul 2>&1

REM Change to build directory
cd /d "%BUILD_DIR%"

REM Install required packages for 32-bit
pip install pyqt5 pyinstaller

REM Build portable executable
pyinstaller --onefile --windowed --clean --noconsole ^
    --icon="src\\\\tutorDraw-logoX92.png" ^
    --add-data="src;src" ^
    --name="TutorDraw-Win32-Portable" ^
    main.py

REM Create final distribution
if exist "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win32-Portable" rd /s /q "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win32-Portable"
mkdir "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win32-Portable"
xcopy /E /I /Y "dist\\\\TutorDraw-Win32-Portable.exe" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win32-Portable\\\\"
copy "README.md" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win32-Portable\\\\" >nul 2>&1
copy "tutordraw_settings.json" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win32-Portable\\\\" >nul 2>&1
copy "LICENSE" "..\\..\\{build_dir}\\windows\\portable\\TutorDraw-Win32-Portable\\\\" >nul 2>&1

REM Cleanup
cd /d "%~dp0"
rd /s /q "%BUILD_DIR%"

echo Windows 32-bit Portable build completed!
pause
'''

    # Windows Installer
    win_installer_script = f'''@echo off
REM Build TutorDraw Windows Installer
echo Building TutorDraw Windows Installer...

REM Create working directory
set BUILD_DIR=%~dp0\\temp_win_installer
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

REM Copy source files
xcopy /E /I /Y ".\\src" "%BUILD_DIR%\\src"
copy ".\\main.py" "%BUILD_DIR%\\" >nul
copy ".\\tutordraw_settings.json" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\tutordraw_config.json" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\README.md" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\LICENSE" "%BUILD_DIR%\\" >nul 2>&1
copy ".\\icons" "%BUILD_DIR%\\icons" /E >nul 2>&1

REM Change to build directory
cd /d "%BUILD_DIR%"

REM Install required packages
pip install pyqt5 pyinstaller

REM Build installer executable (one directory)
pyinstaller --onedir --windowed --clean --noconsole ^
    --icon="src\\\\tutorDraw-logoX92.png" ^
    --add-data="src;src" ^
    --add-data="icons;icons" ^
    --name="TutorDraw-Installer" ^
    main.py

REM Create installer distribution
if exist "..\\..\\{build_dir}\\windows\\installer\\TutorDraw-Installer" rd /s /q "..\\..\\{build_dir}\\windows\\installer\\TutorDraw-Installer"
xcopy /E /I /Y "dist\\\\TutorDraw-Installer" "..\\..\\{build_dir}\\windows\\installer\\\\TutorDraw-Installer"

REM Cleanup
cd /d "%~dp0"
rd /s /q "%BUILD_DIR%"

echo Windows Installer build completed!
echo To create a real installer, use Inno Setup or NSIS with the output folder.
pause
'''

    # Write scripts
    with open(f"{build_dir}/windows/build_win64_portable.bat", "w", encoding='utf-8') as f:
        f.write(win64_portable_script)
    with open(f"{build_dir}/windows/build_win32_portable.bat", "w", encoding='utf-8') as f:
        f.write(win32_portable_script)
    with open(f"{build_dir}/windows/build_installer.bat", "w", encoding='utf-8') as f:
        f.write(win_installer_script)

def create_unix_build_scripts(build_dir, system="linux"):
    """Create Unix build scripts for portable and installer"""
    
    # Portable build script
    portable_script = f'''#!/bin/bash
# Build TutorDraw {system.title()} Portable
echo "Building TutorDraw {system.title()} Portable..."

# Create working directory
BUILD_DIR="$(pwd)/temp_{system}_portable"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy source files
cp -r ./src "$BUILD_DIR/"
cp main.py "$BUILD_DIR/"
cp tutordraw_settings.json "$BUILD_DIR/" 2>/dev/null || true
cp tutordraw_config.json "$BUILD_DIR/" 2>/dev/null || true
cp README.md "$BUILD_DIR/" 2>/dev/null || true
cp LICENSE "$BUILD_DIR/" 2>/dev/null || true
cp -r ./icons "$BUILD_DIR/" 2>/dev/null || true

# Change to build directory
cd "$BUILD_DIR"

# Install required packages
pip install pyqt5 pyinstaller

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == *"64"* ]] || [[ "$ARCH" == *"x86_64"* ]] || [[ "$ARCH" == *"amd64"* ]]; then
    ARCH_NAME="{system}64"
else
    ARCH_NAME="{system}32"
fi

# Build portable executable
pyinstaller --onefile --windowed --clean --noconsole \\
    --icon="src/tutorDraw-logoX92.png" \\
    --add-data="src:src" \\
    --add-data="icons:icons" \\
    --name="TutorDraw-$ARCH_NAME-Portable" \\
    main.py

# Create final distribution
DIST_DIR="../../{build_dir}/{system}/portable/TutorDraw-$ARCH_NAME-Portable"
mkdir -p "$DIST_DIR"
cp "dist/TutorDraw-$ARCH_NAME-Portable" "$DIST_DIR/"
cp README.md "$DIST_DIR/" 2>/dev/null || true
cp tutordraw_settings.json "$DIST_DIR/" 2>/dev/null || true
cp LICENSE "$DIST_DIR/" 2>/dev/null || true

# Make executable
chmod +x "$DIST_DIR/TutorDraw-$ARCH_NAME-Portable"

# Cleanup
cd - > /dev/null
rm -rf "$BUILD_DIR"

echo "{system.title()} Portable build completed!"
'''

    # Installer build script
    installer_script = f'''#!/bin/bash
# Build TutorDraw {system.title()} Installer
echo "Building TutorDraw {system.title()} Installer..."

# Create working directory
BUILD_DIR="$(pwd)/temp_{system}_installer"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy source files
cp -r ./src "$BUILD_DIR/"
cp main.py "$BUILD_DIR/"
cp tutordraw_settings.json "$BUILD_DIR/" 2>/dev/null || true
cp tutordraw_config.json "$BUILD_DIR/" 2>/dev/null || true
cp README.md "$BUILD_DIR/" 2>/dev/null || true
cp LICENSE "$BUILD_DIR/" 2>/dev/null || true
cp -r ./icons "$BUILD_DIR/" 2>/dev/null || true

# Change to build directory
cd "$BUILD_DIR"

# Install required packages
pip install pyqt5 pyinstaller

# Build installer executable (one directory)
pyinstaller --onedir --windowed --clean --noconsole \\
    --icon="src/tutorDraw-logoX92.png" \\
    --add-data="src:src" \\
    --add-data="icons:icons" \\
    --name="TutorDraw-Installer" \\
    main.py

# Create installer distribution
DIST_DIR="../../{build_dir}/{system}/installer/TutorDraw-Installer"
mkdir -p "$(dirname "$DIST_DIR")"
rm -rf "$DIST_DIR"
cp -r "dist/TutorDraw-Installer" "$DIST_DIR"

# Cleanup
cd - > /dev/null
rm -rf "$BUILD_DIR"

echo "{system.title()} Installer build completed!"
echo "To create a real package, use appimagetool, dpkg, or rpm with the output folder."
'''

    # Write scripts
    script_suffix = "_macos" if system == "macos" else ""
    with open(f"{build_dir}/{system}/build_portable{script_suffix}.sh", "w", encoding='utf-8') as f:
        f.write(portable_script)
    with open(f"{build_dir}/{system}/build_installer{script_suffix}.sh", "w", encoding='utf-8') as f:
        f.write(installer_script)
    
    # Make scripts executable
    os.chmod(f"{build_dir}/{system}/build_portable{script_suffix}.sh", 0o755)
    os.chmod(f"{build_dir}/{system}/build_installer{script_suffix}.sh", 0o755)

def create_android_build_script(build_dir):
    """Create Android build script with full APK installer"""
    
    android_script = f'''#!/bin/bash
# Build TutorDraw Android Installer APK
echo "Setting up Android build environment for TutorDraw..."

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "Installing buildozer and cython..."
    pip install buildozer cython
fi

# Install Android SDK/NDK requirements
if [ "$(uname)" = "Linux" ]; then
    echo "Installing Android build requirements..."
    sudo apt update
    sudo apt install -y build-essential libffi-dev libssl-dev zlib1g-dev
    sudo apt install -y libncurses5-dev libncursesw5-dev libreadline-dev
    sudo apt install -y libdb5.3-dev libgdbm-dev libsqlite3-dev
    sudo apt install -y libbz2-dev libexpat1-dev liblzma-dev tk-dev
fi

# Create working directory
BUILD_DIR="$(pwd)/temp_android"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy source files
cp -r ./src "$BUILD_DIR/"
cp main.py "$BUILD_DIR/"
cp tutordraw_settings.json "$BUILD_DIR/" 2>/dev/null || true
cp README.md "$BUILD_DIR/" 2>/dev/null || true
cp LICENSE "$BUILD_DIR/" 2>/dev/null || true
cp -r ./icons "$BUILD_DIR/" 2>/dev/null || true

# Change to build directory
cd "$BUILD_DIR"

# Initialize buildozer if not already done
if [ ! -f buildozer.spec ]; then
    buildozer init
fi

# Create comprehensive Android buildozer.spec file
cat > buildozer.spec << EOF
[app]
title = TutorDraw
package.name = tutordraw
package.domain = com.tutordraw.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt,spec
source.exclude_dirs = tests, bin

version = 2.1.0
requirements = python3,kivy==2.1.0,pyjnius,android

[buildozer]
log_level = 2

[app]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,RECORD_AUDIO,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 30
android.ndk_api = 21

android.archs = arm64-v8a,armeabi-v7a

android.release_artifact = apk

android.add_compile_options = --pack-batch-size 0

[buildozer]
warn_on_root = 1
EOF

# Build for Android (release APK)
echo "Building Android release APK..."
buildozer android release

# Create installer distribution directory
APK_DIST_DIR="../../{build_dir}/android/installer"
mkdir -p "$APK_DIST_DIR"

# Find and copy the APK (both debug and release)
DEBUG_APK=$(find bin -name "*debug.apk" -type f | head -n 1)
RELEASE_APK=$(find bin -name "*release.apk" -type f | head -n 1)
if [ -n "$RELEASE_APK" ]; then
    cp "$RELEASE_APK" "$APK_DIST_DIR/TutorDraw-Android-Installer.apk"
    echo "Android Release APK built successfully: $APK_DIST_DIR/TutorDraw-Android-Installer.apk"
elif [ -n "$DEBUG_APK" ]; then
    cp "$DEBUG_APK" "$APK_DIST_DIR/TutorDraw-Android-Debug.apk"
    echo "Android Debug APK built: $APK_DIST_DIR/TutorDraw-Android-Debug.apk"
else
    echo "Warning: Could not find APK file. Build may have failed."
fi

# Cleanup
cd - > /dev/null
rm -rf "$BUILD_DIR"

echo "Android installer build completed!"'''
'''

    # Write script
    with open(f"{build_dir}/android/build_apk.sh", "w", encoding='utf-8') as f:
        f.write(android_script)
    
    # Make executable
    os.chmod(f"{build_dir}/android/build_apk.sh", 0o755)

def create_universal_build_script(build_dir):
    """Create a universal build script that can build for all platforms"""
    
    universal_script = '''#!/bin/bash
# Universal Build Script for TutorDraw
# Builds for all platforms: Windows, macOS, Linux, Android

echo "Universal Build Script for TutorDraw"
echo "===================================="

# Detect platform
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')

case $PLATFORM in
    *linux*)
        echo "Detected Linux platform"
        echo "Building for Linux..."
        bash "''' + f'{build_dir}' + '''/linux/build_portable.sh"
        bash "''' + f'{build_dir}' + '''/linux/build_installer.sh"
        ;;
    *darwin*|*macos*)
        echo "Detected macOS platform"
        echo "Building for macOS..."
        bash "''' + f'{build_dir}' + '''/macos/build_portable_macos.sh"
        bash "''' + f'{build_dir}' + '''/macos/build_installer_macos.sh"
        ;;
    *)
        echo "Run the appropriate platform-specific script manually:"
        echo "  Windows: Run the .bat files in ''' + f'{build_dir}' + '''/windows/"
        echo "  Linux: bash ''' + f'{build_dir}' + '''/linux/build_portable.sh"
        echo "  macOS: bash ''' + f'{build_dir}' + '''/macos/build_portable_macos.sh"
        echo "  Android: bash ''' + f'{build_dir}' + '''/android/build_apk.sh"
        ;;
esac

echo "Universal build process completed!"'''
'''

    # Write script
    with open(f"{build_dir}/build_all_platforms.sh", "w", encoding='utf-8') as f:
        f.write(universal_script)
    
    # Make executable
    os.chmod(f"{build_dir}/build_all_platforms.sh", 0o755)

def create_requirements_and_setup():
    """Create updated requirements and setup files"""
    
    # Enhanced requirements
    requirements = '''# Core requirements
PyQt5>=5.15.0
Pillow>=8.0.0
numpy>=1.20.0

# Build tools
pyinstaller>=5.0.0
cx-freeze>=6.0.0

# For Android builds (optional)
# Uncomment for Android development
# buildozer>=1.2.0
# cython>=0.29.0
# kivy>=2.1.0
'''
    
    with open("requirements_build.txt", "w", encoding='utf-8') as f:
        f.write(requirements)
    
    # Enhanced setup.py for distribution
    setup_py = '''"""
Setup configuration for TutorDraw
"""
from setuptools import setup, find_packages
import os

# Read README for long description
long_description = ""
readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="tutordraw",
    version="2.1.0",
    author="TutorDraw Team",
    author_email="contact@tutordraw.org",
    description="Professional screen annotation tool with smooth laser pointer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tutordraw/tutordraw",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "Pillow>=8.0.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "tutordraw=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
'''
    
    with open("setup_build.py", "w", encoding='utf-8') as f:
        f.write(setup_py)

def main():
    """Main function to create all build scripts"""
    print("Creating enhanced build system for TutorDraw...")
    print("Supporting: Windows (32/64-bit), macOS, Linux (32/64-bit), Android")
    
    # Create build directory structure
    build_dir = create_build_directory()
    print(f"Created build directory structure: {build_dir}")
    
    # Create platform-specific build scripts
    print("Creating Windows build scripts...")
    create_windows_build_scripts(build_dir)
    
    print("Creating Linux build scripts...")
    create_unix_build_scripts(build_dir, "linux")
    
    print("Creating macOS build scripts...")
    create_unix_build_scripts(build_dir, "macos")
    
    print("Creating Android build script...")
    create_android_build_script(build_dir)
    
    print("Creating universal build script...")
    create_universal_build_script(build_dir)
    
    print("Creating build requirements and setup files...")
    create_requirements_and_setup()
    
    # Create build documentation
    build_docs = f"""# TutorDraw Build System Documentation

## Directory Structure
```
build_dist/
├── windows/
│   ├── portable/
│   │   ├── TutorDraw-Win64-Portable/
│   │   └── TutorDraw-Win32-Portable/
│   └── installer/
│       └── TutorDraw-Installer/
├── linux/
│   ├── portable/
│   └── installer/
├── macos/
│   ├── portable/
│   └── installer/
└── android/
    └── portable/
        └── TutorDraw-Android-Portable.apk
```

## Build Scripts

### Windows
- `build_dist/windows/build_win64_portable.bat` - Build 64-bit portable version
- `build_dist/windows/build_win32_portable.bat` - Build 32-bit portable version  
- `build_dist/windows/build_installer.bat` - Build installer version

### Linux/macOS
- `build_dist/linux/build_portable.sh` - Build portable version
- `build_dist/linux/build_installer.sh` - Build installer version
- `build_dist/macos/build_portable_macos.sh` - Build macOS portable version
- `build_dist/macos/build_installer_macos.sh` - Build macOS installer version

### Android
- `build_dist/android/build_apk.sh` - Build Android APK

### Universal
- `build_dist/build_all_platforms.sh` - Build for all platforms (Linux/macOS)

## Prerequisites

### For all platforms:
- Python 3.8+
- pip
- pyinstaller
- PyQt5

### For Windows:
- Windows OS
- NSIS or Inno Setup (for installer creation)

### For Linux/macOS:
- Unix-like system
- AppImage tools (optional, for AppImage creation)

### For Android:
- Linux system
- buildozer and cython
- Android SDK/NDK

## Usage

1. Install prerequisites:
   ```bash
   pip install -r requirements_build.txt
   ```

2. Run the appropriate build script for your platform.

3. Find the built application in the corresponding output directory.

## Version Naming Convention

- `{build_dir}/windows/portable/TutorDraw-Win64-Portable/` - Windows 64-bit portable
- `{build_dir}/windows/portable/TutorDraw-Win32-Portable/` - Windows 32-bit portable
- `{build_dir}/linux/portable/TutorDraw-Linux64-Portable/` - Linux 64-bit portable
- `{build_dir}/linux/portable/TutorDraw-Linux32-Portable/` - Linux 32-bit portable
- `{build_dir}/macos/portable/TutorDraw-macOS-Portable/` - macOS portable
- `{build_dir}/android/portable/TutorDraw-Android-Portable.apk` - Android APK
"""

    with open(f"{build_dir}/BUILD_INSTRUCTIONS.md", "w", encoding='utf-8') as f:
        f.write(build_docs)
    
    print(f"\nEnhanced build system created successfully!")
    print(f"Build scripts are located in: {build_dir}")
    print(f"Run 'python build_enhanced.py' to create the build system")
    print(f"Then run platform-specific scripts in the {build_dir} directory")

if __name__ == "__main__":
    main()

