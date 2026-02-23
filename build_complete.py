"""
Complete Automated Build System for TutorDraw
Creates ALL installer packages for all platforms in one command
Supports: Windows (MSI), Linux (DEB/RPM/AppImage), macOS (DMG/PKG), Android (APK)
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def detect_platform():
    """Detect current platform"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    arch = "64" if "64" in machine or "amd64" in machine or "x86_64" in machine else "32"
    
    return {
        "system": system,
        "architecture": arch,
        "is_detected": True
    }

def build_windows_complete():
    """Build complete Windows installer (MSI)"""
    print("Building Windows complete installer...")
    
    # Run the Windows installer build script
    installer_script = "build_dist\\installers\\build_windows_installer.bat"
    if os.path.exists(installer_script):
        try:
            result = subprocess.run(
                ["cmd", "/c", installer_script],
                cwd=os.getcwd(),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ Windows MSI installer created successfully!")
                return True
            else:
                print(f"✗ Windows installer failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error running Windows installer script: {e}")
            return False
    else:
        print("✗ Windows installer script not found")
        return False

def build_linux_complete():
    """Build complete Linux installers (DEB, RPM, AppImage)"""
    print("Building Linux complete installers...")
    
    # Run the Linux installer build script
    installer_script = "build_dist/installers/build_linux_installer.sh"
    if os.path.exists(installer_script):
        try:
            result = subprocess.run(
                ["bash", installer_script],
                cwd=os.getcwd(),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ Linux installers (DEB, RPM, AppImage) created successfully!")
                return True
            else:
                print(f"✗ Linux installers failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error running Linux installer script: {e}")
            return False
    else:
        print("✗ Linux installer script not found")
        return False

def build_macos_complete():
    """Build complete macOS installers (DMG, PKG)"""
    print("Building macOS complete installers...")
    
    # Run the macOS installer build script
    installer_script = "build_dist/installers/build_macos_installer.sh"
    if os.path.exists(installer_script):
        try:
            result = subprocess.run(
                ["bash", installer_script],
                cwd=os.getcwd(),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ macOS installers (DMG, PKG) created successfully!")
                return True
            else:
                print(f"✗ macOS installers failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error running macOS installer script: {e}")
            return False
    else:
        print("✗ macOS installer script not found")
        return False

def build_android_complete():
    """Build complete Android APK installer"""
    print("Building Android complete APK installer...")
    
    # Run the Android build script
    android_script = "build_dist/android/build_apk.sh"
    if os.path.exists(android_script):
        try:
            result = subprocess.run(
                ["bash", android_script],
                cwd=os.getcwd(),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ Android APK installer created successfully!")
                return True
            else:
                print(f"✗ Android APK failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error running Android build script: {e}")
            return False
    else:
        print("✗ Android build script not found")
        return False

def build_all_platforms():
    """Build installers for all platforms"""
    print("=" * 60)
    print("TUTORDRAW COMPLETE AUTOMATED BUILD SYSTEM")
    print("=" * 60)
    print("Creating complete installer packages for all platforms...")
    print()
    
    results = {}
    
    # Build for current platform
    current_platform = detect_platform()
    print(f"Detected platform: {current_platform['system']} {current_platform['architecture']}-bit")
    print()
    
    # Build Windows (if on Windows or cross-compiling)
    if current_platform['system'] == 'windows':
        results['windows'] = build_windows_complete()
    else:
        print("Skipping Windows build (not on Windows platform)")
        results['windows'] = False
    
    # Build Linux (if on Linux)
    if current_platform['system'] == 'linux':
        results['linux'] = build_linux_complete()
    else:
        print("Skipping Linux build (not on Linux platform)")
        results['linux'] = False
    
    # Build macOS (if on macOS)
    if current_platform['system'] == 'darwin':
        results['macos'] = build_macos_complete()
    else:
        print("Skipping macOS build (not on macOS platform)")
        results['macos'] = False
    
    # Always try to build Android (cross-platform)
    results['android'] = build_android_complete()
    
    # Summary
    print()
    print("=" * 60)
    print("BUILD SUMMARY")
    print("=" * 60)
    successful = 0
    total = len(results)
    
    for platform_name, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{platform_name.upper():10}: {status}")
        if success:
            successful += 1
    
    print()
    print(f"Successfully built: {successful}/{total} platforms")
    
    if successful > 0:
        print()
        print("INSTALLER LOCATIONS:")
        print("- Windows MSI: build_dist/windows/installer/")
        print("- Linux DEB/RPM/AppImage: build_dist/linux/installer/")
        print("- macOS DMG/PKG: build_dist/macos/installer/")
        print("- Android APK: build_dist/android/installer/")
        print()
        print("✓ Build process completed successfully!")
    else:
        print("✗ No installers were built successfully")
    
    return successful > 0

def build_specific_platform(platform_name):
    """Build installer for a specific platform"""
    platform_name = platform_name.lower()
    
    if platform_name == 'windows':
        return build_windows_complete()
    elif platform_name == 'linux':
        return build_linux_complete()
    elif platform_name == 'macos':
        return build_macos_complete()
    elif platform_name == 'android':
        return build_android_complete()
    else:
        print(f"Unknown platform: {platform_name}")
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TutorDraw Complete Build System')
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos', 'android', 'all'], 
                       default='all', help='Build for specific platform')
    parser.add_argument('--list', action='store_true', help='List available build scripts')
    
    args = parser.parse_args()
    
    if args.list:
        print("Available build scripts:")
        print("- build_dist/installers/build_windows_installer.bat")
        print("- build_dist/installers/build_linux_installer.sh")
        print("- build_dist/installers/build_macos_installer.sh")
        print("- build_dist/android/build_apk.sh")
        return
    
    if args.platform == 'all':
        success = build_all_platforms()
        sys.exit(0 if success else 1)
    else:
        success = build_specific_platform(args.platform)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()