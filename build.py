"""
Build configuration for TutorDraw application
Supports Windows, macOS, Linux, and Android builds
"""
import sys
import os
from pathlib import Path

def create_build_scripts():
    """Create build scripts for different platforms"""
    
    # Create dist directory if it doesn't exist
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Windows build script
    windows_build_script = '''@echo off
REM Build script for Windows
echo Building TutorDraw for Windows...

REM Install required packages
pip install pyinstaller pyside6

REM Build executable
pyinstaller --onefile --windowed --icon=src/tutorDraw-logoX92.png --add-data "src;tutorDraw/src" --name "TutorDraw" main.py

echo Windows build completed!
pause
'''
    
    # Linux/macOS build script
    unix_build_script = '''#!/bin/bash
# Build script for Linux/macOS
echo "Building TutorDraw for Linux/macOS..."

# Install required packages
pip install pyinstaller pyside6

# Build executable
pyinstaller --onefile --windowed --icon=src/tutorDraw-logoX92.png --add-data "src:tutorDraw/src" --name "TutorDraw" main.py

echo "Linux/macOS build completed!"
'''
    
    # Android build script (using buildozer with Kivy)
    android_build_script = '''#!/bin/bash
# Build script for Android using Buildozer
echo "Setting up Android build environment..."

# Install buildozer if not already installed
pip install buildozer cython

# Initialize buildozer if not already done
if [ ! -f buildozer.spec ]; then
    buildozer init
fi

# Modify buildozer.spec for our app
cat > buildozer.spec << EOF
[app]
title = TutorDraw
package.name = tutordraw
package.domain = org.tutordraw

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt

version = 1.0
requirements = python3,pyjnius,pyside6

[buildozer]
log_level = 2

[app]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,CAMERA
EOF

# Build for Android
buildozer android debug

echo "Android build completed!"
'''

    # Write build scripts
    with open(dist_dir / "build_windows.bat", "w") as f:
        f.write(windows_build_script)
        
    with open(dist_dir / "build_unix.sh", "w") as f:
        f.write(unix_build_script)
        
    with open(dist_dir / "build_android.sh", "w") as f:
        f.write(android_build_script)

    # Make Unix script executable
    os.chmod(dist_dir / "build_unix.sh", 0o755)
    os.chmod(dist_dir / "build_android.sh", 0o755)

    print("Build scripts created in dist/ directory:")
    print("- build_windows.bat")
    print("- build_unix.sh")
    print("- build_android.sh")


def optimize_code_structure():
    """Optimize the code structure for better maintainability"""
    
    # Create a main application module
    main_module = '''"""
Main application entry point for TutorDraw
Handles platform-specific initialization
"""
import sys
import os
from pathlib import Path

def get_platform():
    """Detect the current platform"""
    import platform
    system = platform.system().lower()
    if "windows" in system:
        return "windows"
    elif "darwin" in system or "macos" in system:
        return "macos"
    elif "linux" in system:
        return "linux"
    elif "android" in system:
        return "android"
    else:
        return "unknown"

def main():
    """Main application entry point"""
    platform = get_platform()
    
    # Import and run platform-specific main
    if platform == "android":
        # Android-specific initialization
        from tutorDraw.android_main import run_android_app
        run_android_app()
    else:
        # Desktop initialization
        from tutorDraw.main_desktop import run_desktop_app
        run_desktop_app()

if __name__ == "__main__":
    main()
'''

    # Create desktop main module
    desktop_main = '''"""
Desktop main application module
"""
import sys
from PySide6.QtWidgets import QApplication
from tutorDraw.canvas import TutorCanvas
from tutorDraw.themes import get_theme

def run_desktop_app():
    """Run the desktop version of the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("TutorDraw")
    app.setApplicationVersion("2.0")
    
    # Load theme
    theme = get_theme("light")  # Could be configurable
    
    # Create main window
    canvas = TutorCanvas(theme)
    
    sys.exit(app.exec())
'''

    # Create Android main module
    android_main = '''"""
Android main application module
"""
def run_android_app():
    """Run the Android version of the application"""
    # For Android, we might use a different UI framework
    # or adapt the existing PySide6 code
    print("Running TutorDraw on Android")
    
    # Placeholder for Android-specific code
    # In a real implementation, you'd likely use Kivy
    # or another mobile-friendly framework
    pass
'''

    # Create organized package structure
    tutor_draw_dir = Path("tutorDraw")
    tutor_draw_dir.mkdir(exist_ok=True)
    
    with open(tutor_draw_dir / "__init__.py", "w") as f:
        f.write('"""TutorDraw package"""')
    
    with open(tutor_draw_dir / "main.py", "w") as f:
        f.write(main_module)
    
    desktop_dir = tutor_draw_dir / "desktop"
    desktop_dir.mkdir(exist_ok=True)
    with open(desktop_dir / "__init__.py", "w") as f:
        f.write('"""TutorDraw desktop package"""')
    
    with open(desktop_dir / "main_desktop.py", "w") as f:
        f.write(desktop_main)
    
    android_dir = tutor_draw_dir / "android"
    android_dir.mkdir(exist_ok=True)
    with open(android_dir / "__init__.py", "w") as f:
        f.write('"""TutorDraw Android package"""')
    
    with open(android_dir / "main_android.py", "w") as f:
        f.write(android_main)
    
    # Move existing modules to the new structure
    modules = ["canvas", "toolbar", "shapes", "themes", "laser", "recorder", "recording_controls", "selection_window", "settings"]
    for module in modules:
        src = Path(f"src/{module}.py")
        if src.exists():
            dest = tutor_draw_dir / f"{module}.py"
            if not dest.exists():  # Don't overwrite if already exists
                with open(src, 'r') as s:
                    content = s.read()
                
                # Update imports in the content to reflect new structure
                content = content.replace('from .', 'from tutorDraw.')
                content = content.replace('from src.', 'from tutorDraw.')
                
                with open(dest, 'w') as d:
                    d.write(content)

    print("Code structure optimized for cross-platform deployment")


def create_deployment_configs():
    """Create configuration files for different deployment scenarios"""
    
    # Create setup.py for pip installation
    setup_py = '''"""
Setup configuration for TutorDraw
"""
from setuptools import setup, find_packages

setup(
    name="tutordraw",
    version="2.0.0",
    description="Professional screen annotation tool with smooth laser pointer",
    author="TutorDraw Team",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.5.0",
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tutordraw=tutorDraw.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
    
    # Create requirements.txt
    requirements = '''PySide6>=6.5.0
Pillow>=9.0.0
'''

    # Create Dockerfile for containerized builds
    dockerfile = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
'''

    # Write configuration files
    with open("setup.py", "w") as f:
        f.write(setup_py)
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)

    print("Deployment configurations created:")
    print("- setup.py")
    print("- requirements.txt")
    print("- Dockerfile")


def main():
    """Run the optimization process"""
    print("Optimizing TutorDraw for cross-platform deployment...")
    
    create_build_scripts()
    optimize_code_structure()
    create_deployment_configs()
    
    print("\nOptimization complete!")
    print("Next steps:")
    print("1. Review the new code structure in the tutorDraw/ directory")
    print("2. Run the appropriate build script from dist/")
    print("3. Test the application on your target platforms")


if __name__ == "__main__":
    main()