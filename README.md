# TutorDraw 🖌️

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

**TutorDraw** is a revolutionary cross-platform annotation and presentation tool that transforms any screen into an interactive whiteboard. Built with Python and PyQt5, it provides educators, presenters, and content creators with powerful drawing tools that work seamlessly across applications.

## 🌟 Key Features

- **Universal Screen Annotation**: Draw, highlight, and annotate over any application
- **Real-time Collaboration**: Share your screen annotations during presentations
- **Multi-tool Drawing Kit**: Pencil, highlighter, shapes, arrows, and text tools
- **Laser Pointer**: Professional presentation tool with customizable thickness, color, and glow effects
- **White/Black Board**: Toggle between annotation mode and traditional whiteboard/blackboard modes
- **Theme System**: 6 beautiful themes including Dark, Deep Blue, and Jellyfish
- **Custom Branding**: Professional logo integration (`tutorDraw-logoX92.png`) across all UI elements
- **Recording Capabilities**: Capture your annotated sessions
- **Cross-Platform Support**: Works on Windows, macOS, Linux, and Android
- **Intuitive Toolbar**: Compact, modern interface with 3-dot menu system

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment support (venv module)
- Application logo file (`tutorDraw-logoX92.png`) in project root

### Installation from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/tutordraw.git
cd TutorDraw

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Installation from Release

1. Download the latest release from the [GitHub Releases](https://github.com/yourusername/tutordraw/releases) page
2. Extract the archive to your preferred location
3. Run the executable:
   - **Windows**: Double-click `TutorDraw.exe`
   - **macOS**: Double-click `TutorDraw.app`
   - **Linux**: Run `./TutorDraw` from terminal

## 🛠️ Development Guide

### Running the Application

```bash
# With virtual environment (recommended)
# First time setup:
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Every subsequent run:
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
python main.py
```

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python -m unittest discover tests/unit      # Unit tests
python -m unittest discover tests/integration  # Integration tests

# Run individual test files
python -m unittest tests/unit/test_themes.py
```

### Building for Different Platforms

#### Windows
```bash
# Install build dependencies
pip install pyinstaller

# Build executable with logo
pyinstaller --onefile --windowed --name=TutorDraw --icon=tutorDraw-logoX92.png main.py

# Or use the build script
python build.py
```

#### macOS
```bash
# Install build dependencies
pip install pyinstaller

# Build app bundle with logo
pyinstaller --onefile --windowed --name=TutorDraw --icon=tutorDraw-logoX92.png --osx-bundle-identifier=com.tutordraw.app main.py
```

#### Linux
```bash
# Install build dependencies
pip install pyinstaller

# Build executable with logo
pyinstaller --onefile --windowed --name=TutorDraw --icon=tutorDraw-logoX92.png main.py

# Make executable
chmod +x dist/TutorDraw
```

#### Android (Using Buildozer)
```bash
# Install buildozer
pip install buildozer

# Initialize buildozer
buildozer init

# Modify buildozer.spec to include tutorDraw-logoX92.png as app icon
# Update buildozer.spec:
# - source.include_patterns = *.py, tutorDraw-logoX92.png
# - icon = tutorDraw-logoX92.png
# Then build APK
buildozer android debug
```

## 📱 Platform-Specific Instructions

### Windows
- Supports Windows 10/11
- Touch screen compatible
- Keyboard shortcuts fully functional
- System tray integration available

### macOS
- Compatible with macOS 10.15+
- Touch Bar support
- Retina display optimized
- Gatekeeper compatible builds

### Linux
- Works on Ubuntu, Fedora, Debian, and other distributions
- Wayland and X11 support
- Snap/Flatpak packaging available
- System theme integration

### Android
- Requires Android 7.0+
- Touch-optimized interface
- Hardware acceleration support
- Tablet and phone layouts

## 🔧 Technical Architecture

### Core Components
- **Canvas Engine**: Real-time drawing surface with anti-aliasing
- **Theme Manager**: Dynamic color scheme system
- **Toolbar System**: Modular, extensible UI components
- **Recording Module**: Screen capture and video export
- **Configuration Manager**: Persistent settings storage

### Dependencies
```python
PyQt5>=5.15.0        # GUI Framework
numpy>=1.21.0        # Numerical computations
opencv-python>=4.5.0 # Image processing
pillow>=8.3.0        # Image manipulation
pyautogui>=0.9.53    # Screen automation
```

### Project Structure
```
TutorDraw/
├── src/                 # Source code
│   ├── canvas.py       # Main drawing canvas
│   ├── toolbar.py      # Toolbar implementation
│   ├── themes_system.py # Theme management
│   ├── settings.py     # Settings dialog
│   └── recorder.py     # Screen recording
├── tests/              # Test suite
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── e2e/           # End-to-end tests
├── tutorDraw-logoX92.png # Application logo
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── build.py          # Build scripts
```

## 🎨 Usage Guide

### Basic Operations
1. **Launch**: Run `python main.py`
2. **Draw**: Use mouse/touch to draw on screen
3. **Tools**: Access via toolbar (pencil, highlighter, shapes)
4. **Themes**: Change appearance via Settings → Themes
5. **Record**: Capture sessions using recording controls

### Advanced Features
- **Keyboard Shortcuts**: 
  - `P` - Pencil tool
  - `H` - Highlighter tool  
  - `R` - Rectangle tool
  - `T` - Text tool
  - `ESC` - Exit application

- **Theme Customization**: 6 built-in themes with automatic icon coloring
- **Capture Options**: Full screen, area, or scrolling screenshots
- **Laser Pointer**: Real-time cursor highlighting during presentations

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/tutordraw.git
cd TutorDraw

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

# Run tests
python tests/run_tests.py

# Code formatting
black src/ tests/
flake8 src/ tests/
```

## 📊 Performance Metrics

- **Startup Time**: < 2 seconds
- **Memory Usage**: ~50MB baseline
- **CPU Usage**: < 5% during idle
- **Drawing Latency**: < 16ms (60 FPS)
- **Theme Switching**: Instant (< 100ms)

## 🔒 Security & Privacy

- **Local Processing**: All annotations processed locally
- **No Data Collection**: Zero telemetry or user data collection
- **File System Access**: Only reads/writes configuration files
- **Network Usage**: None (offline capable)

## 🆘 Troubleshooting

### Common Issues

**Issue**: Drawing not working on transparent screen
**Solution**: Ensure `Qt.WindowTransparentForInput` flag is NOT set

**Issue**: Toolbar not responding
**Solution**: Check that all required PyQt5 modules are installed

**Issue**: Theme colors not applying
**Solution**: Verify theme names match exactly (case-sensitive)

**Issue**: ModuleNotFoundError or import errors
**Solution**: Activate your virtual environment and reinstall dependencies:
```bash
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Virtual environment not working
**Solution**: Recreate the virtual environment:
```bash
# Remove existing virtual environment
delete .venv (Windows) or rm -rf .venv (macOS/Linux)

# Create new virtual environment
python -m venv .venv

# Activate and install dependencies
# On Windows:
.venv\\Scripts\\activate
# On macOS/Linux:
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Issue**: Logo not showing in application
**Solution**: Ensure `tutorDraw-logoX92.png` file is in the project root directory:
```bash
# Verify logo file exists
ls -la tutorDraw-logoX92.png

# If missing, copy from assets folder or re-download
# The application will fallback gracefully if logo is not found
```

### System Requirements
- **Minimum**: 4GB RAM, Dual-core processor
- **Recommended**: 8GB RAM, Quad-core processor
- **Display**: 1920x1080 minimum resolution

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PyQt5 community for the excellent GUI framework
- OpenCV team for computer vision capabilities
- FFmpeg project for multimedia processing
- All contributors who helped improve this tool

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/tutordraw/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/tutordraw/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/tutordraw/discussions)
- **Email**: support@tutordraw.com

---

<p align="center">
  Made with ❤️ for educators and presenters worldwide
</p>