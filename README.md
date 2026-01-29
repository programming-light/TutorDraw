# TutorDraw

TutorDraw is a powerful annotation and drawing tool designed for educators, presenters, and content creators. It provides a seamless overlay canvas that allows you to draw, annotate, and highlight directly on your screen during presentations, tutorials, or demonstrations.

## Features

### Drawing Tools
- **Pencil**: Freehand drawing tool
- **Highlighter**: Text-aware highlighting that aligns with existing text
- **Shapes**: Rectangle, Circle, Diamond, and Arrow tools
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
- **Transparent Annotation**: Draw on top of existing content
- **Whiteboard Mode**: Solid background for clear presentations

## Keyboard Shortcuts

| Shortcut | Function |
|----------|----------|
| Ctrl+Shift+H | Toggle toolbar visibility |
| Ctrl+Shift+M | Mouse mode |
| Ctrl+V | Select mode |
| Ctrl+P | Pencil tool |
| Ctrl+R | Rectangle tool |
| Ctrl+D | Diamond tool |
| Ctrl+E | Ellipse/Circle tool |
| Ctrl+A | Arrow tool |
| Ctrl+T | Text tool |
| Ctrl+L | Laser pointer |
| Ctrl+X | Eraser |
| Ctrl+B | Toggle text bold |
| Ctrl+I | Toggle text italic |
| Ctrl+Shift+> | Increase text size |
| Ctrl+Shift+< | Decrease text size |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Esc | Exit application |

## Installation

### Prerequisites
- Python 3.7 or higher
- Virtual environment (recommended)

### Setup
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

## Contributing

We welcome contributions from the community! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, feature requests, or bug reports, please open an issue on our GitHub repository.

## Acknowledgments

- PyQt5 for the GUI framework
- All contributors who have helped make TutorDraw better