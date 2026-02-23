#!/usr/bin/env python3
"""
Simple Build Wrapper for TutorDraw
Easy single-command building for all platforms
"""
import sys
import os
import platform
import subprocess
import argparse
from pathlib import Path

def detect_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    arch = "64" if "64" in machine or "amd64" in machine or "x86_64" in machine else "32"
    
    return {
        "system": system,
        "architecture": arch,
        "is_detected": True
    }

def run_build_script(script_path, platform_name):
    """Run a build script"""
    if not os.path.exists(script_path):
        print(f"Error: Build script not found: {script_path}")
        return False
    
    print(f"Building for {platform_name}...")
    print(f"Running: {script_path}")
    
    try:
        if script_path.endswith('.bat'):
            # Windows batch file
            result = subprocess.run([script_path], shell=True, 
                                  capture_output=True, text=True)
        else:
            # Unix shell script
            result = subprocess.run(['bash', script_path], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ {platform_name} build completed successfully!")
            return True
        else:
            print(f"✗ {platform_name} build failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error running build script: {e}")
        return False

def build_windows(arch="64", build_type="portable"):
    """Build for Windows"""
    build_script = f"build_dist/windows/build_win{arch}_{build_type}.bat"
    platform_name = f"Windows {arch}-bit {build_type}"
    return run_build_script(build_script, platform_name)

def build_linux(arch="64", build_type="portable"):
    """Build for Linux"""
    build_script = f"build_dist/linux/build_{build_type}.sh"
    platform_name = f"Linux {arch}-bit {build_type}"
    return run_build_script(build_script, platform_name)

def build_macos(build_type="portable"):
    """Build for macOS"""
    build_script = f"build_dist/macos/build_{build_type}_macos.sh"
    platform_name = f"macOS {build_type}"
    return run_build_script(build_script, platform_name)

def build_android():
    """Build for Android"""
    build_script = "build_dist/android/build_apk.sh"
    platform_name = "Android APK"
    return run_build_script(build_script, platform_name)

def build_all_installers():
    """Build complete installer packages for all platforms"""
    print("Building complete installer packages for all platforms...")
    
    # Get current platform info
    plat_info = detect_platform()
    
    success_count = 0
    total_count = 0
    
    # Build installers for current platform
    if plat_info["system"] == "windows":
        total_count += 1
        installer_script = "build_dist/installers/build_windows_installer.bat"
        if run_build_script(installer_script, "Windows Complete Installer"):
            success_count += 1
            
    elif plat_info["system"] == "linux":
        total_count += 1
        installer_script = "build_dist/installers/build_linux_installer.sh"
        if run_build_script(installer_script, "Linux Complete Installers"):
            success_count += 1
            
    elif plat_info["system"] == "darwin":  # macOS
        total_count += 1
        installer_script = "build_dist/installers/build_macos_installer.sh"
        if run_build_script(installer_script, "macOS Complete Installers"):
            success_count += 1
    
    # Build Android installer (can be built on Linux/macOS)
    if plat_info["system"] in ["linux", "darwin"]:
        total_count += 1
        if build_android():  # This creates APK installer
            success_count += 1
    
    print(f"\nInstaller Build Summary: {success_count}/{total_count} installer builds successful")

def build_all():
    """Build for all platforms (both portable and installers)"""
    print("Building for all platforms (portable + installers)...")
    
    # Get current platform info
    plat_info = detect_platform()
    
    success_count = 0
    total_count = 0
    
    # Build portable versions
    if plat_info["system"] == "windows":
        total_count += 2
        if build_windows("64", "portable"):
            success_count += 1
        if build_windows("64", "installer"):
            success_count += 1
            
    elif plat_info["system"] == "linux":
        total_count += 2
        if build_linux(plat_info["architecture"], "portable"):
            success_count += 1
        if build_linux(plat_info["architecture"], "installer"):
            success_count += 1
            
    elif plat_info["system"] == "darwin":  # macOS
        total_count += 2
        if build_macos("portable"):
            success_count += 1
        if build_macos("installer"):
            success_count += 1
    
    # Build for Android (can be built on Linux/macOS)
    if plat_info["system"] in ["linux", "darwin"]:
        total_count += 1
        if build_android():
            success_count += 1
    
    print(f"\nBuild Summary: {success_count}/{total_count} builds successful")

def main():
    parser = argparse.ArgumentParser(description="TutorDraw Build Wrapper")
    parser.add_argument('--platform', '-p', 
                       choices=['windows', 'linux', 'macos', 'android', 'all', 'installers'],
                       help='Target platform to build for')
    parser.add_argument('--arch', '-a', 
                       choices=['32', '64'], 
                       default='64',
                       help='Architecture (32 or 64 bit)')
    parser.add_argument('--type', '-t', 
                       choices=['portable', 'installer'], 
                       default='portable',
                       help='Build type (portable or installer)')
    parser.add_argument('--list', '-l', 
                       action='store_true',
                       help='List available build scripts')
    parser.add_argument('--installers-only', '-i',
                       action='store_true',
                       help='Build only complete installer packages')
    
    args = parser.parse_args()
    
    # Ensure build system exists
    if not os.path.exists("build_dist"):
        print("Build system not found. Creating...")
        result = subprocess.run([sys.executable, "build_enhanced.py"])
        if result.returncode != 0:
            print("Failed to create build system!")
            return 1
    
    # Handle list option
    if args.list:
        print("Available build scripts:")
        for root, dirs, files in os.walk("build_dist"):
            for file in files:
                if file.endswith(('.bat', '.sh')):
                    rel_path = os.path.relpath(os.path.join(root, file))
                    print(f"  {rel_path}")
        return 0
    
    # Handle build commands
    if args.installers_only or args.platform == 'installers':
        build_all_installers()
    elif args.platform:
        if args.platform == 'all':
            build_all()
        elif args.platform == 'windows':
            build_windows(args.arch, args.type)
        elif args.platform == 'linux':
            build_linux(args.arch, args.type)
        elif args.platform == 'macos':
            build_macos(args.type)
        elif args.platform == 'android':
            build_android()
    else:
        # Auto-detect and build for current platform
        plat_info = detect_platform()
        print(f"Detected platform: {plat_info['system']} {plat_info['architecture']}-bit")
        
        if plat_info["system"] == "windows":
            build_windows(plat_info["architecture"], "portable")
        elif plat_info["system"] == "linux":
            build_linux(plat_info["architecture"], "portable")
        elif plat_info["system"] == "darwin":
            build_macos("portable")
        else:
            print("Unsupported platform for auto-build")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())