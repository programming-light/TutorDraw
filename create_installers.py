"""
Enhanced Installer Creation System for TutorDraw
Creates complete installer packages for all platforms
"""
import os
import sys
import platform
from pathlib import Path

def create_windows_installer_script(build_dir):
    """Create comprehensive Windows installer with Inno Setup"""
    
    # Create Inno Setup script
    inno_script = f'''; TutorDraw Windows Installer Script
[Setup]
AppName=TutorDraw
AppVersion=2.1.0
AppPublisher=TutorDraw Team
AppPublisherURL=https://tutordraw.org
AppSupportURL=https://tutordraw.org/support
AppUpdatesURL=https://tutordraw.org/downloads

DefaultDirName={{autopf}}\\TutorDraw
DefaultGroupName=TutorDraw
AllowNoIcons=yes
LicenseFile=..\\..\\LICENSE
OutputDir=..\\..\\{build_dir}\\windows\\installer
OutputBaseFilename=TutorDraw-Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "dist\\TutorDraw-Win64-Installer\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\TutorDraw"; Filename: "{{app}}\\main.exe"
Name: "{{group}}\\{{cm:UninstallProgram,TutorDraw}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\TutorDraw"; Filename: "{{app}}\\main.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\main.exe"; Description: "{{cm:LaunchProgram,TutorDraw}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\\TutorDraw"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\\TutorDraw\\Settings"; ValueType: string; ValueName: "InstallPath"; ValueData: "{{app}}"

[INI]
Filename: "{{app}}\\settings.ini"; Section: "Settings"; Key: "InstallPath"; String: "{{app}}"
'''
    
    # Create Windows installer build script
    installer_script = f'''@echo off
REM Comprehensive Windows Installer Build Script
echo Building Comprehensive Windows Installer...

REM Create working directory
set BUILD_DIR=%~dp0\\temp_win_installer
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

REM Copy source files
xcopy /E /I /Y "..\\..\\src" "%BUILD_DIR%\\src"
copy "..\\..\\main.py" "%BUILD_DIR%\\" >nul
copy "..\\..\\tutordraw_settings.json" "%BUILD_DIR%\\" >nul 2>&1
copy "..\\..\\tutordraw_config.json" "%BUILD_DIR%\\" >nul 2>&1
copy "..\\..\\README.md" "%BUILD_DIR%\\" >nul 2>&1
copy "..\\..\\LICENSE" "%BUILD_DIR%\\" >nul 2>&1
copy "..\\..\\icons" "%BUILD_DIR%\\icons" /E >nul 2>&1

REM Change to build directory
cd /d "%BUILD_DIR%"

REM Install required packages
pip install pyqt5 pyinstaller cx_freeze

REM Build installer executable (one directory)
pyinstaller --onedir --windowed --clean --noconsole ^
    --icon="src\\\\tutorDraw-logoX92.png" ^
    --add-data="src;src" ^
    --add-data="icons;icons" ^
    --name="main" ^
    main.py

REM Create Inno Setup script
echo Creating Inno Setup script...
) > TutorDraw.iss

REM Check if Inno Setup is installed
where ISCC.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Compiling installer with Inno Setup...
    ISCC.exe TutorDraw.iss
) else (
    echo Inno Setup not found. Creating portable installer alternative...
    
    REM Create NSIS script as alternative
    echo !define PRODUCT_NAME "TutorDraw" > TutorDraw.nsi
    echo !define PRODUCT_VERSION "2.1.0" >> TutorDraw.nsi
    echo !define PRODUCT_PUBLISHER "TutorDraw Team" >> TutorDraw.nsi
    echo !define PRODUCT_WEB_SITE "https://tutordraw.org" >> TutorDraw.nsi
    echo !define PRODUCT_DIR_REGKEY "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\TutorDraw.exe" >> TutorDraw.nsi
    echo !define PRODUCT_UNINST_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}" >> TutorDraw.nsi
    echo !define PRODUCT_UNINST_ROOT_KEY "HKLM" >> TutorDraw.nsi
    echo !include "MUI2.nsh" >> TutorDraw.nsi
    echo !insertmacro MUI_PAGE_WELCOME >> TutorDraw.nsi
    echo !insertmacro MUI_PAGE_LICENSE "..\\..\\LICENSE" >> TutorDraw.nsi
    echo !insertmacro MUI_PAGE_DIRECTORY >> TutorDraw.nsi
    echo !insertmacro MUI_PAGE_INSTFILES >> TutorDraw.nsi
    echo !insertmacro MUI_PAGE_FINISH >> TutorDraw.nsi
    echo !insertmacro MUI_UNPAGE_INSTFILES >> TutorDraw.nsi
    echo !insertmacro MUI_LANGUAGE "English" >> TutorDraw.nsi
    echo Section "MainSection" SEC01 >> TutorDraw.nsi
    echo SetOutPath "$INSTDIR" >> TutorDraw.nsi
    echo File /r "dist\\main" >> TutorDraw.nsi
    echo CreateDirectory "$SMPROGRAMS\\TutorDraw" >> TutorDraw.nsi
    echo CreateShortCut "$SMPROGRAMS\\TutorDraw\\TutorDraw.lnk" "$INSTDIR\\main\\main.exe" >> TutorDraw.nsi
    echo CreateShortCut "$DESKTOP\\TutorDraw.lnk" "$INSTDIR\\main\\main.exe" >> TutorDraw.nsi
    echo SectionEnd >> TutorDraw.nsi
    echo Section -AdditionalIcons >> TutorDraw.nsi
    echo WriteIniStr "$INSTDIR\\${{PRODUCT_NAME}}.url" "InternetShortcut" "URL" "${{PRODUCT_WEB_SITE}}" >> TutorDraw.nsi
    echo CreateShortCut "$SMPROGRAMS\\TutorDraw\\Website.lnk" "$INSTDIR\\${{PRODUCT_NAME}}.url" >> TutorDraw.nsi
    echo SectionEnd >> TutorDraw.nsi
    echo Section -Post >> TutorDraw.nsi
    echo WriteUninstaller "$INSTDIR\\uninst.exe" >> TutorDraw.nsi
    echo WriteRegStr HKLM "${{PRODUCT_UNINST_ROOT_KEY}}\\${{PRODUCT_UNINST_KEY}}" "DisplayName" "$(^Name)" >> TutorDraw.nsi
    echo WriteRegStr HKLM "${{PRODUCT_UNINST_ROOT_KEY}}\\${{PRODUCT_UNINST_KEY}}" "UninstallString" "$INSTDIR\\uninst.exe" >> TutorDraw.nsi
    echo WriteRegStr HKLM "${{PRODUCT_UNINST_ROOT_KEY}}\\${{PRODUCT_UNINST_KEY}}" "DisplayIcon" "$INSTDIR\\main\\main.exe" >> TutorDraw.nsi
    echo WriteRegStr HKLM "${{PRODUCT_UNINST_ROOT_KEY}}\\${{PRODUCT_UNINST_KEY}}" "DisplayVersion" "${{PRODUCT_VERSION}}" >> TutorDraw.nsi
    echo WriteRegStr HKLM "${{PRODUCT_UNINST_ROOT_KEY}}\\${{PRODUCT_UNINST_KEY}}" "URLInfoAbout" "${{PRODUCT_WEB_SITE}}" >> TutorDraw.nsi
    echo SectionEnd >> TutorDraw.nsi
    echo Section Uninstall >> TutorDraw.nsi
    echo Delete "$INSTDIR\\${{PRODUCT_NAME}}.url" >> TutorDraw.nsi
    echo Delete "$INSTDIR\\uninst.exe" >> TutorDraw.nsi
    echo Delete "$SMPROGRAMS\\TutorDraw\\Uninstall.lnk" >> TutorDraw.nsi
    echo Delete "$SMPROGRAMS\\TutorDraw\\Website.lnk" >> TutorDraw.nsi
    echo Delete "$DESKTOP\\TutorDraw.lnk" >> TutorDraw.nsi
    echo Delete "$SMPROGRAMS\\TutorDraw\\TutorDraw.lnk" >> TutorDraw.nsi
    echo RMDir "$SMPROGRAMS\\TutorDraw" >> TutorDraw.nsi
    echo RMDir /r "$INSTDIR" >> TutorDraw.nsi
    echo SectionEnd >> TutorDraw.nsi
    
    REM Check if NSIS is available
    where makensis.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo Compiling installer with NSIS...
        makensis.exe TutorDraw.nsi
    ) else (
        echo Neither Inno Setup nor NSIS found.
        echo Creating self-extracting archive installer...
        
        REM Create 7-Zip SFX installer
        if exist "C:\\Program Files\\7-Zip\\7z.exe" (
            echo Creating 7-Zip self-extracting installer...
            "C:\\Program Files\\7-Zip\\7z.exe" a -t7z TutorDraw.7z "dist\\main\\*" -mx=9
            copy /b "C:\\Program Files\\7-Zip\\7z.sfx" + TutorDraw.7z TutorDraw-Installer.exe
            del TutorDraw.7z
        ) else (
            echo No installer creation tools found.
            echo Creating simple ZIP distribution...
            powershell Compress-Archive -Path "dist\\main\\*" -DestinationPath "TutorDraw-Windows-Installer.zip" -Force
        )
    )
)

REM Create final installer distribution
set INSTALLER_DIST_DIR=..\\..\\{build_dir}\\windows\\installer\\TutorDraw-Complete-Installer
if exist "%INSTALLER_DIST_DIR%" rd /s /q "%INSTALLER_DIST_DIR%"
mkdir "%INSTALLER_DIST_DIR%"

REM Copy installer files
if exist "Output\\TutorDraw-Installer.exe" (
    copy "Output\\TutorDraw-Installer.exe" "%INSTALLER_DIST_DIR%\\"
) else if exist "TutorDraw-Installer.exe" (
    copy "TutorDraw-Installer.exe" "%INSTALLER_DIST_DIR%\\"
) else if exist "TutorDraw-Windows-Installer.zip" (
    copy "TutorDraw-Windows-Installer.zip" "%INSTALLER_DIST_DIR%\\"
) else (
    xcopy /E /I /Y "dist\\main" "%INSTALLER_DIST_DIR%\\TutorDraw-Portable\\"
    copy "..\\..\\README.md" "%INSTALLER_DIST_DIR%\\TutorDraw-Portable\\" >nul 2>&1
    copy "..\\..\\LICENSE" "%INSTALLER_DIST_DIR%\\TutorDraw-Portable\\" >nul 2>&1
    echo Created portable distribution as fallback
)

REM Copy additional files
copy "..\\..\\README.md" "%INSTALLER_DIST_DIR%\\"
copy "..\\..\\LICENSE" "%INSTALLER_DIST_DIR%\\"

REM Cleanup
cd /d "%~dp0"
rd /s /q "%BUILD_DIR%"

echo Windows comprehensive installer build completed!
echo Installer location: %INSTALLER_DIST_DIR%
pause
'''

    return installer_script

def create_linux_installer_scripts(build_dir):
    """Create comprehensive Linux installer scripts"""
    
    # Debian/Ubuntu installer script
    deb_script = f'''#!/bin/bash
# Comprehensive Debian/Ubuntu Installer Build Script
echo "Building Debian/Ubuntu Installer..."

# Create working directory
BUILD_DIR="$(pwd)/temp_linux_deb"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy source files
cp -r ../../src "$BUILD_DIR/"
cp ../../main.py "$BUILD_DIR/"
cp ../../tutordraw_settings.json "$BUILD_DIR/" 2>/dev/null || true
cp ../../README.md "$BUILD_DIR/" 2>/dev/null || true
cp ../../LICENSE "$BUILD_DIR/" 2>/dev/null || true
cp -r ../../icons "$BUILD_DIR/" 2>/dev/null || true

# Change to build directory
cd "$BUILD_DIR"

# Install required packages
pip install pyqt5 pyinstaller

# Build application
pyinstaller --onedir --windowed --clean --noconsole \\
    --icon="src/tutorDraw-logoX92.png" \\
    --add-data="src:src" \\
    --add-data="icons:icons" \\
    --name="tutordraw" \\
    main.py

# Create Debian package structure
mkdir -p deb-package/usr/bin
mkdir -p deb-package/usr/share/applications
mkdir -p deb-package/usr/share/icons/hicolor/256x256/apps
mkdir -p deb-package/usr/share/doc/tutordraw
mkdir -p deb-package/DEBIAN

# Copy application files
cp -r dist/tutordraw/* deb-package/usr/bin/
cp ../../icons/tutorDraw-logoX92.png deb-package/usr/share/icons/hicolor/256x256/apps/tutordraw.png

# Create desktop entry
cat > deb-package/usr/share/applications/tutordraw.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=TutorDraw
Comment=Professional screen annotation tool
Exec=/usr/bin/tutordraw/main
Icon=tutordraw
Terminal=false
Categories=Education;Graphics;
EOF

# Create control file
cat > deb-package/DEBIAN/control << EOF
Package: tutordraw
Version: 2.1.0
Section: graphics
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt5
Maintainer: TutorDraw Team <contact@tutordraw.org>
Description: Professional screen annotation tool with smooth laser pointer
 TutorDraw is a powerful annotation and drawing tool designed for educators,
 presenters, and content creators. It provides a seamless overlay canvas that
 allows you to draw, annotate, and highlight directly on your screen.
Homepage: https://tutordraw.org
EOF

# Create post-install script
cat > deb-package/DEBIAN/postinst << EOF
#!/bin/bash
chmod +x /usr/bin/tutordraw/main
xdg-desktop-menu install /usr/share/applications/tutordraw.desktop
gtk-update-icon-cache /usr/share/icons/hicolor/ -f
EOF

chmod +x deb-package/DEBIAN/postinst

# Create pre-remove script
cat > deb-package/DEBIAN/prerm << EOF
#!/bin/bash
xdg-desktop-menu uninstall /usr/share/applications/tutordraw.desktop
gtk-update-icon-cache /usr/share/icons/hicolor/ -f
EOF

chmod +x deb-package/DEBIAN/prerm

# Set permissions
find deb-package -type d -exec chmod 755 {{}} \\;
find deb-package -type f -exec chmod 644 {{}} \\;
chmod 755 deb-package/usr/bin/main

# Build Debian package
dpkg-deb --build deb-package

# Create installer distribution
DEB_DIST_DIR="../../{build_dir}/linux/installer/TutorDraw-Debian-Installer"
mkdir -p "$DEB_DIST_DIR"
mv deb-package.deb "$DEB_DIST_DIR/TutorDraw-2.1.0-amd64.deb"

# Also create RPM package for Fedora/RHEL
echo "Building RPM package..."

# Create RPM structure
mkdir -p ~/rpmbuild/{{BUILD,RPMS,SOURCES,SPECS,SRPMS}}
mkdir -p rpm-package/{{BUILD,RPMS,SOURCES,SPECS,SRPMS}}

# Create RPM spec file
cat > rpm-package/SPECS/tutordraw.spec << EOF
Name: tutordraw
Version: 2.1.0
Release: 1
Summary: Professional screen annotation tool
License: MIT
Group: Applications/Graphics
URL: https://tutordraw.org
Source0: tutordraw-%{{version}}.tar.gz
BuildArch: x86_64

Requires: python3, python3-qt5

%description
TutorDraw is a powerful annotation and drawing tool designed for educators,
presenters, and content creators. It provides a seamless overlay canvas that
allows you to draw, annotate, and highlight directly on your screen.

%prep
%setup -q

%build
# No build required for Python application

%install
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/icons/hicolor/256x256/apps

cp -r dist/tutordraw/* %{{buildroot}}/usr/bin/
cp icons/tutorDraw-logoX92.png %{{buildroot}}/usr/share/icons/hicolor/256x256/apps/tutordraw.png

cat > %{{buildroot}}/usr/share/applications/tutordraw.desktop << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=TutorDraw
Comment=Professional screen annotation tool
Exec=/usr/bin/main
Icon=tutordraw
Terminal=false
Categories=Education;Graphics;
DESKTOP

%files
/usr/bin/*
/usr/share/applications/tutordraw.desktop
/usr/share/icons/hicolor/256x256/apps/tutordraw.png

%post
gtk-update-icon-cache /usr/share/icons/hicolor/ -f

%preun
gtk-update-icon-cache /usr/share/icons/hicolor/ -f
EOF

# Create RPM package
# rpmbuild -bb rpm-package/SPECS/tutordraw.spec

# Create RPM distribution
RPM_DIST_DIR="../../{build_dir}/linux/installer/TutorDraw-RPM-Installer"
mkdir -p "$RPM_DIST_DIR"
# mv ~/rpmbuild/RPMS/x86_64/tutordraw-2.1.0-1.x86_64.rpm "$RPM_DIST_DIR/"

# Create AppImage as universal Linux installer
echo "Creating AppImage installer..."

# Download linuxdeploy if not exists
if [ ! -f linuxdeploy-x86_64.AppImage ]; then
    wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x linuxdeploy-x86_64.AppImage
fi

# Create AppImage
./linuxdeploy-x86_64.AppImage \\
    --appdir AppDir \\
    --executable dist/tutordraw/main \\
    --icon-file icons/tutorDraw-logoX92.png \\
    --desktop-file usr/share/applications/tutordraw.desktop \\
    --output appimage

# Move AppImage to distribution
APPIMAGE_DIST_DIR="../../{build_dir}/linux/installer/TutorDraw-AppImage-Installer"
mkdir -p "$APPIMAGE_DIST_DIR"
mv TutorDraw-x86_64.AppImage "$APPIMAGE_DIST_DIR/TutorDraw-Linux-Installer.AppImage"

# Cleanup
cd - > /dev/null
rm -rf "$BUILD_DIR"

echo "Linux comprehensive installer build completed!"
echo "Installers created:"
echo "  - Debian: $DEB_DIST_DIR/TutorDraw-2.1.0-amd64.deb"
echo "  - AppImage: $APPIMAGE_DIST_DIR/TutorDraw-Linux-Installer.AppImage"
'''

    return deb_script

def create_macos_installer_script(build_dir):
    """Create comprehensive macOS installer"""
    
    macos_script = f'''#!/bin/bash
# Comprehensive macOS Installer Build Script
echo "Building macOS Installer..."

# Create working directory
BUILD_DIR="$(pwd)/temp_macos_installer"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy source files
cp -r ../../src "$BUILD_DIR/"
cp ../../main.py "$BUILD_DIR/"
cp ../../tutordraw_settings.json "$BUILD_DIR/" 2>/dev/null || true
cp ../../README.md "$BUILD_DIR/" 2>/dev/null || true
cp ../../LICENSE "$BUILD_DIR/" 2>/dev/null || true
cp -r ../../icons "$BUILD_DIR/" 2>/dev/null || true

# Change to build directory
cd "$BUILD_DIR"

# Install required packages
pip install pyqt5 pyinstaller

# Build application bundle
pyinstaller --windowed --clean --noconsole \\
    --icon="src/tutorDraw-logoX92.png" \\
    --add-data="src:src" \\
    --add-data="icons:icons" \\
    --name="TutorDraw" \\
    main.py

# Create disk image installer
echo "Creating DMG installer..."

# Create temporary directory for DMG
mkdir -p dmg_tmp
cp -r dist/TutorDraw.app dmg_tmp/
cp ../../README.md dmg_tmp/ 2>/dev/null || true
cp ../../LICENSE dmg_tmp/ 2>/dev/null || true

# Create symbolic link to Applications folder
ln -s /Applications dmg_tmp/Applications

# Create DMG
hdiutil create -volname "TutorDraw Installer" \\
    -srcfolder dmg_tmp \\
    -ov -format UDZO \\
    TutorDraw-Installer.dmg

# Create PKG installer
echo "Creating PKG installer..."

# Create component package
pkgbuild --root dist/TutorDraw.app \\
    --identifier org.tutordraw.tutordraw \\
    --version 2.1.0 \\
    --install-location /Applications \\
    tutordraw-component.pkg

# Create distribution package
productbuild --package tutordraw-component.pkg \\
    --resources pkg_resources \\
    TutorDraw-Installer.pkg

# Create installer distribution
MACOS_DIST_DIR="../../{build_dir}/macos/installer/TutorDraw-MacOS-Installer"
mkdir -p "$MACOS_DIST_DIR"
mv TutorDraw-Installer.dmg "$MACOS_DIST_DIR/"
mv TutorDraw-Installer.pkg "$MACOS_DIST_DIR/"

# Cleanup
cd - > /dev/null
rm -rf "$BUILD_DIR"

echo "macOS comprehensive installer build completed!"
echo "Installers created:"
echo "  - DMG: $MACOS_DIST_DIR/TutorDraw-Installer.dmg"
echo "  - PKG: $MACOS_DIST_DIR/TutorDraw-Installer.pkg"
'''

    return macos_script

def main():
    """Generate all installer creation scripts"""
    print("Creating comprehensive installer build system...")
    
    build_dir = "build_dist"
    
    # Create installer scripts directory
    installer_dir = Path(f"{build_dir}/installers")
    installer_dir.mkdir(exist_ok=True)
    
    # Create Windows installer script
    windows_installer = create_windows_installer_script(build_dir)
    with open(f"{installer_dir}/build_windows_installer.bat", "w") as f:
        f.write(windows_installer)
    
    # Create Linux installer script
    linux_installer = create_linux_installer_scripts(build_dir)
    with open(f"{installer_dir}/build_linux_installer.sh", "w") as f:
        f.write(linux_installer)
    os.chmod(f"{installer_dir}/build_linux_installer.sh", 0o755)
    
    # Create macOS installer script
    macos_installer = create_macos_installer_script(build_dir)
    with open(f"{installer_dir}/build_macos_installer.sh", "w") as f:
        f.write(macos_installer)
    os.chmod(f"{installer_dir}/build_macos_installer.sh", 0o755)
    
    # Create master installer script
    master_script = f'''#!/bin/bash
# Master Installer Build Script
echo "Building installers for all platforms..."

# Build Windows installer
if [ "$(uname)" = "Linux" ] || [ "$(uname)" = "Darwin" ]; then
    echo "Windows installer must be built on Windows"
else
    cmd /c "{installer_dir}/build_windows_installer.bat"
fi

# Build Linux installer
if [ "$(uname)" = "Linux" ]; then
    bash "{installer_dir}/build_linux_installer.sh"
fi

# Build macOS installer
if [ "$(uname)" = "Darwin" ]; then
    bash "{installer_dir}/build_macos_installer.sh"
fi

echo "Installer build process completed!"
'''
    
    with open(f"{installer_dir}/build_all_installers.sh", "w") as f:
        f.write(master_script)
    os.chmod(f"{installer_dir}/build_all_installers.sh", 0o755)
    
    print(f"Installer build scripts created in {installer_dir}/")
    print("Run 'bash build_dist/installers/build_all_installers.sh' to build all installers")

if __name__ == "__main__":
    main()