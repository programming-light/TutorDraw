# TutorDraw

TutorDraw is a powerful annotation and drawing tool designed for educators, presenters, and content creators. It provides a seamless overlay canvas that allows you to draw, annotate, and highlight directly on your screen during presentations, tutorials, or demonstrations.

## Features

### Drawing Tools
- **Pencil**: Freehand drawing tool
- **Highlighter**: Text-aware highlighting that aligns with existing text
- **Shapes**: Rectangle, Circle, Diamond, Arrow, Triangle, Hexagon, Pentagon, Octagon, Star, and more
- **Advanced Shapes**: Double Arrow, Curved Arrow, Cloud, Callout, Speech Bubble
- **Text**: Add text annotations with customizable font properties
- **Laser Pointer**: Smooth animated laser pointer for presentations
- **Eraser**: Remove annotations selectively
- **Zoom**: Magnify specific areas of the screen

### Smart Features
- **Text-Aware Highlighting**: Automatically detects and aligns with existing text for precise highlighting
- **Selection & Transformation**: Select, move, resize, and rotate drawn elements
- **Fill Mode**: Fill shapes with color
- **Undo/Redo**: Full editing history support
- **Theme Support**: Light and Dark themes with customizable colors

### Toolbar Management
- **Auto-Hide**: Toolbar automatically hides when not in use but stays accessible during interaction
- **Peek Functionality**: Hover over the hide icon to temporarily show the toolbar
- **Toggle Visibility**: Use Ctrl+Shift+H to show/hide the toolbar
- **Orientation**: Switch between horizontal and vertical toolbar layouts

### Board Modes
- **White Board (Default)**: Full white background to hide other applications
- **Black Board**: Full black background to hide other applications
- **Transparent Annotation**: Draw on top of existing content
- **Left Sidebar**: Excalidraw-like sidebar for changing canvas color and fill settings
- **Keyboard Shortcut**: Ctrl+Shift+B to toggle board on/off
- **No Fill Button in Toolbar**: Fill options moved to sidebar
- **Reset to Defaults**: One-click reset all settings to default values
- **Whiteboard Mode**: Solid background for clear presentations

## Global Keyboard Shortcuts

**These shortcuts work even when TutorDraw is running in the background!**

| Shortcut | Function |
|----------|----------|
| **Ctrl+Alt+P** | Pencil tool |
| **Ctrl+Alt+R** | Rectangle tool |
| **Ctrl+Alt+E** | Ellipse/Circle tool |
| **Ctrl+Alt+A** | Arrow tool |
| **Ctrl+Alt+T** | Text tool |
| **Ctrl+Alt+X** | Eraser |
| **Ctrl+Alt+V** | Select mode |
| **Ctrl+Alt+M** | Mouse mode |
| **Ctrl+Alt+H** | Toggle toolbar visibility |
| **Ctrl+Alt+B** | Toggle board mode on/off |
| **Ctrl+Alt+Z** | Undo |
| **Ctrl+Alt+Y** | Redo |
| **Ctrl+Alt+C** | Clear canvas |
| **Ctrl+Alt+S** | Full Screen Screenshot |
| **Ctrl+Alt+Shift+S** | Area Screenshot |
| **Ctrl+Alt+L** | Long Screenshot (Scrolling) |
| **Ctrl+Alt+Shift+L** | Scrolling Screenshot |
| **Ctrl+Alt+Rec** | Start/Stop Recording |
| **Ctrl+Alt+Shift+Rec** | Record Area |
| **Ctrl+Alt+F** | Toggle Fill Mode |

### Legacy Shortcuts (for reference)
| Shortcut | Function |
|----------|----------|
| Ctrl+Shift+H | Toggle toolbar visibility |
| Ctrl+V | Select mode |
| Ctrl+P | Pencil tool |
| Ctrl+R | Rectangle tool |
| Ctrl+D | Diamond tool |
| Ctrl+E | Ellipse/Circle tool |
| Ctrl+A | Arrow tool |
| Ctrl+T | Text tool |
| Ctrl+L | Laser pointer |
| Ctrl+X | Eraser |
| Ctrl+Shift+B | Toggle board mode on/off |
| Ctrl+I | Toggle text italic |
| Ctrl+Shift+> | Increase text size |
| Ctrl+Shift+< | Decrease text size |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Esc | Exit application |

## Installation

### Quick Start (Source Code)
1. Clone the repository:
```bash
git clone https://github.com/yourusername/TutorDraw.git
cd TutorDraw
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

### Pre-built Binaries
Download pre-built binaries from our releases page:
- **Windows**: Portable (.exe) and Installer (.msi) versions
- **macOS**: Portable (.app) and Installer (.dmg) versions
- **Linux**: Portable (AppImage) and Installer (.deb/.rpm) versions
- **Android**: APK for mobile devices

All binaries are available in 32-bit and 64-bit versions where applicable.

## Usage

### Getting Started
1. Launch TutorDraw using `python main.py`
2. The toolbar will appear at the top center of your screen
3. Select a drawing tool from the toolbar
4. Start drawing directly on your screen

### Drawing Techniques
- **Freehand Drawing**: Use the pencil tool for natural drawing
- **Precise Shapes**: Use shape tools for perfect geometric forms
- **Text Annotations**: Click the text tool and type your annotation
- **Smart Highlighting**: The highlighter automatically aligns with existing text

### Advanced Features
- **Element Selection**: Use the select tool to move, resize, or rotate drawn elements
- **Layer Management**: New drawings appear on top of existing ones
- **Theme Customization**: Switch between light and dark themes in settings

## Configuration

TutorDraw stores user preferences in `tutordraw_settings.json`:
- Custom keyboard shortcuts
- Laser pointer settings
- Default colors and thicknesses
- Toolbar orientation preferences

## Building from Source

### 🚀 Complete Automated Building (ONE COMMAND!)
Create ALL installer packages for ALL platforms with a single command:

```bash
# Build everything automatically - creates MSI, DEB, RPM, AppImage, DMG, PKG, APK
python build.py
```

This single command will:
- ✅ Create Windows MSI installer
- ✅ Create Linux DEB/RPM/AppImage installers
- ✅ Create macOS DMG/PKG installers
- ✅ Create Android APK installer
- ✅ Organize everything in proper directories

### 🔧 Platform-Specific Building
Build for specific platforms when needed:

```bash
# Build for specific platform only
python build_complete.py --platform windows    # Creates MSI installer
python build_complete.py --platform linux      # Creates DEB/RPM/AppImage
python build_complete.py --platform macos      # Creates DMG/PKG
python build_complete.py --platform android    # Creates APK

# List all available build scripts
python build_complete.py --list
```

### 📁 Build Output Structure
```
build_dist/
├── windows/
│   ├── portable/
│   │   └── TutorDraw-Win64-Portable.zip
│   └── installer/
│       └── TutorDraw-Installer.msi          ← COMPLETE MSI INSTALLER
├── linux/
│   ├── portable/
│   │   └── TutorDraw-Linux64-Portable.tar.gz
│   └── installer/
│       ├── TutorDraw-Ubuntu-Installer.deb   ← DEB for Ubuntu/Debian
│       ├── TutorDraw-Fedora-Installer.rpm   ← RPM for Fedora/RHEL
│       └── TutorDraw-Linux-Installer.AppImage ← Universal Linux
├── macos/
│   ├── portable/
│   │   └── TutorDraw-macOS-Portable.app.zip
│   └── installer/
│       ├── TutorDraw-Installer.dmg          ← DMG installer
│       └── TutorDraw-Installer.pkg          ← PKG installer
└── android/
    └── installer/
        └── TutorDraw-Android-Installer.apk    ← COMPLETE APK INSTALLER
```

### ⚙️ Advanced Manual Building
For developers who want granular control:

1. Generate all installer build scripts:
```bash
python create_installers.py
```

2. Run platform-specific installer scripts:
```bash
# Windows (MSI)
build_dist\installers\build_windows_installer.bat

# Linux (DEB/RPM/AppImage)
bash build_dist/installers/build_linux_installer.sh

# macOS (DMG/PKG)
bash build_dist/installers/build_macos_installer.sh

# Android (APK)
bash build_dist/android/build_apk.sh
```

### 📦 Complete Installer Features
- **Windows**: MSI installer with desktop shortcuts and registry entries
- **Linux**: DEB (Ubuntu/Debian), RPM (Fedora/RHEL), and AppImage (universal) packages
- **macOS**: DMG and PKG installers with proper application bundling
- **Android**: Signed APK installer ready for Google Play Store

### Git Repository Management
The project includes a comprehensive `.gitignore` file that excludes:
- Build artifacts and output directories
- Python cache files and virtual environments
- IDE configuration files
- OS-specific files
- Log files and temporary files

To maintain the `.gitignore` file:
```bash
python maintain_gitignore.py
```

This script will:
- Check currently ignored files
- Verify common patterns are included
- Add missing patterns if needed
- Provide maintenance tips

## Contributing

We welcome contributions from the community! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, feature requests, or bug reports, please open an issue on our GitHub repository.

## Acknowledgments

- PyQt5 for the GUI framework
- All contributors who have helped make TutorDraw better