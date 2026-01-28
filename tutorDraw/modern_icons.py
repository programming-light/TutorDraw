"""
Simple Reliable SVG Icon Manager for TutorDraw
This provides guaranteed icon rendering using simple SVG paths.
"""

import sys
from PyQt5.QtGui import QIcon, QColor, QPixmap, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QApplication

class SimpleIconManager:
    """Simple and reliable icon manager using SVG paths"""
    
    def __init__(self, theme_name="light"):
        self.theme_name = theme_name
        self.icon_cache = {}
        self._setup_colors()
        
        # Modern rounded icons mapping
        self.icon_mapping = {
            # Tools
            'mouse': '🖱',           # Computer mouse
            'pencil': '✏',          # Pencil
            'eraser': '🧽',          # Sponge/Eraser
            'text': '📝',            # Memo/Text
            'laser': '💡',          # Light bulb/Laser
            'select': '↖',          # Up-left arrow/Select
            'highlighter': '🖍',     # Crayon/Highlighter
            'zoom': '🔍',            # Magnifying glass
            'fill': '油漆桶',        # Paint bucket (Chinese character as fallback)
            
            # Shapes
            'shapes': '🔷',          # Blue diamond/Shapes
            'rect': '⬜',            # White square
            'ellipse': '⭕',         # Heavy circle
            'diamond': '🔷',         # Blue diamond
            'arrow': '↗',           # Up-right arrow
            
            # Actions
            'undo': '↩',            # Left arrow with hook
            'redo': '↪',            # Right arrow with hook
            'clear': '🗑',           # Wastebasket
            
            # UI Elements
            'board': '📋',          # Clipboard/Board
            'capture': '📷',        # Camera
            'tools': '🧰',          # Toolbox
            'settings': '⚙',        # Gear
            'more': '⋮',            # Vertical ellipsis
            'hide': '👁',           # Eye
            'exit': '✖',            # Multiplication sign
            'about': 'ℹ',           # Information
            
            # View/UI
            'zoom_in': '🔍+',       # Magnifying glass with plus
            'zoom_out': '🔍-',      # Magnifying glass with minus
            'fullscreen': '⛶',      # Square with corners
            'grid': '⊞',            # Grid
            'transparency': '▢'     # Hollow square
        }

    def _setup_colors(self):
        """Setup colors based on theme"""
        if self.theme_name in ["Dark", "Deep Blue", "Deep Green", "Jellyfish", "Charcoal"]:
            self.primary_color = QColor(255, 255, 255)  # White for dark themes
        else:
            self.primary_color = QColor(30, 30, 30)     # Dark for light themes

    def set_theme(self, theme_name):
        """Set the theme and update colors"""
        self.theme_name = theme_name
        self._setup_colors()
        self.icon_cache.clear()

    def _get_svg_template(self, icon_name, color, size=24):
        """Get SVG template for icons that don't have external files"""
        svg_templates = {
            'mouse': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M13 1.07V9h7c0-4.08-3.06-7.44-7-7.93zM4 15c0 4.42 3.58 8 8 8s8-3.58 8-8v-4H4v4zm7-13.93C7.05 1.55 4 4.91 4 9h7V1.07z"/>
                </svg>
            ''',
            'pencil': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
            ''',
            'eraser': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M16.24 3.56l4.95 4.94c.78.79.78 2.05 0 2.84L12 20.53a4.008 4.008 0 0 1-5.66 0L2.81 17c-.78-.79-.78-2.05 0-2.84l10.6-10.6c.79-.78 2.05-.78 2.83 0zM4.22 15.58l3.54 3.53c.78.79 2.04.79 2.83 0l3.53-3.53-6.36-6.36-3.54 3.54c-.78.78-.78 2.04 0 2.82z"/>
                </svg>
            ''',
            'text': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M5 4v3h5.5v12h3V7H19V4z"/>
                </svg>
            ''',
            'laser': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm7-7H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1.75 9c0 .23-.02.46-.05.68l-3.69 3.69c-.15.15-.35.22-.55.22s-.4-.07-.55-.22l-1.42-1.42 4.24-4.24c.23-.03.46-.05.69-.05.23 0 .46.02.68.05l3.69 3.69c-.03.15-.05.29-.05.44 0 .55.45 1 1 1s1-.45 1-1-.45-1-1-1z"/>
                </svg>
            ''',
            'select': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
            ''',
            'highlighter': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M6 14l3 3v5h6v-5l3-3V9H6v5zm5-12h2v3h-2V2zM3.5 5.88l1.41-1.41 2.12 2.12L5.62 8 3.5 5.88zm13.46.71l2.12-2.12 1.41 1.41L18.38 8l-1.42-1.41z"/>
                </svg>
            ''',
            'zoom': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
            ''',
            'fill': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M18 4V3c0-.55-.45-1-1-1H5c-.55 0-1 .45-1 1v4c0 .55.45 1 1 1h12c.55 0 1-.45 1-1V6h1v4H9v11c0 .55.45 1 1 1h2c.55 0 1-.45 1-1v-9h8V4h-3z"/>
                </svg>
            ''',
            'rect': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M3 3v18h18V3H3zm16 16H5V5h14v14z"/>
                </svg>
            ''',
            'ellipse': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <circle fill="{color}" cx="12" cy="12" r="10"/>
                </svg>
            ''',
            'diamond': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 2L2 12l10 10 10-10L12 2zm0 18l-8-8 8-8 8 8-8 8z"/>
                </svg>
            ''',
            'arrow': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/>
                </svg>
            ''',
            'undo': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/>
                </svg>
            ''',
            'redo': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.95 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"/>
                </svg>
            ''',
            'clear': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
            ''',
            'board': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
                </svg>
            ''',
            'capture': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                </svg>
            ''',
            'tools': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
                </svg>
            ''',
            'settings': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.82,11.69,4.82,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
                </svg>
            ''',
            'more': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                </svg>
            ''',
            'hide': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                </svg>
            ''',
            'exit': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            ''',
            'about': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm0-8h-2V7h2v2z"/>
                </svg>
            ''',
            'shapes': '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
            '''
        }
        
        # Get the SVG template for this icon
        if icon_name not in svg_templates:
            # Fallback to a simple question mark
            svg_content = '''
                <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
                    <path fill="{color}" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
                </svg>
            '''
        else:
            svg_content = svg_templates[icon_name]
        
        # Format the SVG with color and size
        formatted_svg = svg_content.format(color=color.name(), size=size)
        return formatted_svg

    def _create_svg_icon(self, icon_name, color, size=24):
        """Create SVG-based icons with guaranteed rendering"""
        import os
        
        # Map icon names to their corresponding SVG files
        svg_file_map = {
            'laser': 'icons/laser_pointer-01.svg',
            'board': 'icons/bord_svg.svg',
            'select': 'icons/selector.svg',
            'more': 'icons/3_dot_options.svg'
        }
        
        # Check if we have a specific SVG file for this icon
        if icon_name in svg_file_map:
            svg_file_path = svg_file_map[icon_name]
            if os.path.exists(svg_file_path):
                try:
                    # Read the SVG file
                    with open(svg_file_path, 'r', encoding='utf-8') as f:
                        svg_content = f.read()
                    
                    # Update the color in the SVG content
                    # Replace fill color with the desired color
                    svg_content = svg_content.replace('fill="currentColor"', f'fill="{color.name()}"')
                    svg_content = svg_content.replace('fill="#000000"', f'fill="{color.name()}"')
                    svg_content = svg_content.replace('fill="black"', f'fill="{color.name()}"')
                    svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color.name()}"')
                    svg_content = svg_content.replace('stroke="#000000"', f'stroke="{color.name()}"')
                    
                    # For the laser icon specifically, add fill to paths that don't have explicit fill
                    if icon_name == 'laser':
                        # Add fill attribute to path elements that don't have one
                        import re
                        svg_content = re.sub(r'(<path\s+(?:[^>]*?\s+)?)([^>]*?>)', 
                                           lambda m: f'{m.group(1)}fill="{color.name()}" {m.group(2)}' if 'fill=' not in m.group(0) else m.group(0), 
                                           svg_content)
                        
                        # Also handle paths that have fill="none" - replace with the desired color
                        svg_content = svg_content.replace('fill="none"', f'fill="{color.name()}"')
                        svg_content = re.sub(r'fill:\s*none', f'fill:{color.name()}', svg_content)
                    
                    # Ensure the SVG has the correct size
                    if 'width="' not in svg_content:
                        svg_content = svg_content.replace('<svg ', f'<svg width="{size}" height="{size}" ')
                    else:
                        # Replace width and height attributes with the desired size
                        import re
                        svg_content = re.sub(r'width="[^"]*"', f'width="{size}"', svg_content)
                        svg_content = re.sub(r'height="[^"]*"', f'height="{size}"', svg_content)
                    
                    formatted_svg = svg_content
                except Exception as e:
                    print(f"Error loading SVG file {svg_file_path}: {e}")
                    # Fallback to template
                    formatted_svg = self._get_svg_template(icon_name, color, size)
            else:
                # Fallback to template if file doesn't exist
                formatted_svg = self._get_svg_template(icon_name, color, size)
        else:
            # Use template for other icons
            formatted_svg = self._get_svg_template(icon_name, color, size)
        
        # Create QPixmap from SVG
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer = QSvgRenderer(formatted_svg.encode('utf-8'))
        renderer.render(painter)
        painter.end()
        
        # Create and return QIcon
        icon = QIcon(pixmap)
        return icon

    def get_icon(self, icon_name, color='primary', size=24):
        """Get an icon with caching"""
        cache_key = f"{icon_name}_{color}_{size}_{self.theme_name}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Use primary color by default
        icon_color = self.primary_color
        
        # For dark themes, enforce white color for laser pointer and more icons
        dark_themes = ["Dark", "Deep Blue", "Deep Green", "Jellyfish", "Charcoal"]
        
        if self.theme_name in dark_themes and icon_name in ['laser', 'more']:
            icon_color = QColor(255, 255, 255)  # Force white for these icons in dark themes
        
        icon = self._create_svg_icon(icon_name, icon_color, size)
        self.icon_cache[cache_key] = icon
        return icon

# Global instance
icon_manager = SimpleIconManager()

def initialize_icons(theme_name="light"):
    """Initialize the global icon manager"""
    global icon_manager
    icon_manager = SimpleIconManager(theme_name)
    return icon_manager

def switch_theme(theme_name):
    """Switch theme for all icons"""
    global icon_manager
    icon_manager.set_theme(theme_name)
    return icon_manager

# Test function
if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = SimpleIconManager()
    
    # Test a few icons
    icons_to_test = ['mouse', 'pencil', 'eraser', 'text', 'laser']
    for icon_name in icons_to_test:
        icon = manager.get_icon(icon_name, size=32)
        print(f"Icon '{icon_name}': {'Success' if not icon.isNull() else 'Failed'}")
    
    app.quit()