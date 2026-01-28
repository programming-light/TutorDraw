"""
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
