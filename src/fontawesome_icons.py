"""
Professional FontAwesome icon manager for TutorDraw
Uses qtawesome for proper icon rendering with theme support
"""
import qtawesome as qta
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt


class FontAwesomeIconManager:
    """Professional icon manager using qtawesome with theme support"""
    
    def __init__(self, theme_name="light"):
        self.theme_name = theme_name
        self.icon_cache = {}
        self._setup_theme_colors()
    
    def _setup_theme_colors(self):
        """Setup color schemes for different themes"""
        if self.theme_name == "dark":
            self.colors = {
                'primary': QColor(220, 220, 220),    # Light text for dark background
                'secondary': QColor(180, 180, 180),  # Secondary text
                'accent': QColor(105, 101, 219),     # Purple accent
                'success': QColor(46, 204, 113),     # Green
                'warning': QColor(241, 196, 15),     # Yellow
                'error': QColor(231, 76, 60),        # Red
                'disabled': QColor(100, 100, 100)    # Disabled state
            }
        else:  # light theme
            self.colors = {
                'primary': QColor(30, 30, 30),       # Dark text for light background
                'secondary': QColor(80, 80, 80),     # Secondary text
                'accent': QColor(105, 101, 219),     # Purple accent
                'success': QColor(46, 204, 113),     # Green
                'warning': QColor(241, 196, 15),     # Yellow
                'error': QColor(231, 76, 60),        # Red
                'disabled': QColor(180, 180, 180)    # Disabled state
            }
    
    def set_theme(self, theme_name):
        """Switch theme and update colors"""
        self.theme_name = theme_name
        self._setup_theme_colors()
        # Clear cache to regenerate icons with new theme
        self.icon_cache.clear()
    
    def get_icon(self, icon_name, color='primary', size=24, **kwargs):
        """Get a FontAwesome icon with theme-aware coloring"""
        # Create cache key
        cache_key = f"{icon_name}_{color}_{size}_{self.theme_name}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Get color from theme
        icon_color = self.colors.get(color, self.colors['primary'])
        
        # Map simple names to FontAwesome icon names (exact qtawesome equivalents for your requested icons)
        icon_mapping = {
            # Tools - using exact equivalents to your requested icons
            'mouse': 'fa5s.mouse',           # fa-solid fa-computer-mouse -> fa5s.mouse
            'pencil': 'fa5s.pencil-alt',   # fa-solid fa-pencil -> fa5s.pencil-alt
            'eraser': 'fa5s.eraser',       # fa-solid fa-eraser -> fa5s.eraser
            'text': 'fa5s.font',           # fa-solid fa-font -> fa5s.font
            'laser': 'fa5s.magic',         # fa-solid fa-wand-sparkles -> fa5s.magic
            'select': 'fa5s.object-group', # fa-solid fa-object-group -> fa5s.object-group
            
            # Shapes
            'shapes': 'fa5s.shapes',       # fa-solid fa-shapes -> fa5s.shapes
            'shape_rect': 'fa5s.square',
            'shape_circle': 'fa5s.circle',
            'shape_ellipse': 'fa5s.ellipsis-h',
            'shape_diamond': 'fa5s.gem',
            'shape_arrow': 'fa5s.arrow-right',
            
            # Actions
            'undo': 'fa5s.undo',
            'redo': 'fa5s.redo',
            'clear': 'fa5s.trash',
            
            # UI Elements
            'board': 'fa5s.chalkboard',    # fa-solid fa-chalkboard -> fa5s.chalkboard
            'capture': 'fa5s.camera',      # fa-solid fa-photo-film -> fa5s.camera
            'tools': 'fa5s.toolbox',       # fa-solid fa-toolbox -> fa5s.toolbox
            'settings': 'fa5s.cog',
            'more': 'fa5s.ellipsis-v',
            'hide': 'fa5s.eye-slash',
            'exit': 'fa5s.times',
            'about': 'fa5s.info-circle',
            
            # View/UI
            'zoom_in': 'fa5s.search-plus',
            'zoom_out': 'fa5s.search-minus',
            'fullscreen': 'fa5s.expand',
            'grid': 'fa5s.th',
            'transparency': 'fa5s.border-all'
        }
        
        # Get FontAwesome icon name
        fa_icon_name = icon_mapping.get(icon_name, 'fa5s.question-circle')
        
        try:
            # Create icon with qtawesome
            icon = qta.icon(fa_icon_name, 
                          color=icon_color, 
                          scale_factor=size/24.0,  # Scale relative to base size
                          **kwargs)
            self.icon_cache[cache_key] = icon
            return icon
        except Exception as e:
            print(f"Warning: Could not create icon '{icon_name}': {e}")
            # Return fallback icon
            return QIcon()
    
    def get_colored_icon(self, icon_name, color_name, size=24):
        """Convenience method to get colored icons"""
        return self.get_icon(icon_name, color_name, size)
    
    def get_disabled_icon(self, icon_name, size=24):
        """Get disabled state icon"""
        return self.get_icon(icon_name, 'disabled', size)
    
    def get_accent_icon(self, icon_name, size=24):
        """Get accent-colored icon"""
        return self.get_icon(icon_name, 'accent', size)


class ThemedToolButton:
    """Professional tool button with FontAwesome icons and theme support"""
    
    def __init__(self, icon_manager, icon_name, tooltip="", shortcut="", parent=None):
        from PySide6.QtWidgets import QPushButton
        
        self.button = QPushButton(parent)
        self.icon_manager = icon_manager
        self.icon_name = icon_name
        self.tooltip = tooltip
        self.shortcut = shortcut
        
        self.setup_button()
    
    def setup_button(self):
        """Setup button with icon and styling"""
        # Set icon
        icon = self.icon_manager.get_icon(self.icon_name)
        self.button.setIcon(icon)
        self.button.setIconSize(self.button.size())
        
        # Set tooltip
        if self.shortcut:
            self.button.setToolTip(f"{self.tooltip} [{self.shortcut}]")
        else:
            self.button.setToolTip(self.tooltip)
        
        # Set styling
        self.button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background: rgba(105, 101, 219, 0.1);
            }
            QPushButton:pressed {
                background: rgba(105, 101, 219, 0.2);
            }
            QPushButton:checked {
                background: rgba(105, 101, 219, 0.3);
                border: 2px solid #6965db;
            }
        """)
        
        # Set cursor
        self.button.setCursor(Qt.PointingHandCursor)
    
    def update_theme(self):
        """Update button icon when theme changes"""
        icon = self.icon_manager.get_icon(self.icon_name)
        self.button.setIcon(icon)
    
    def setChecked(self, checked):
        """Set button checked state"""
        self.button.setChecked(checked)
    
    def isChecked(self):
        """Get button checked state"""
        return self.button.isChecked()


# Global icon manager instance
icon_manager = FontAwesomeIconManager()


def initialize_icons(theme_name="light"):
    """Initialize the global icon manager"""
    global icon_manager
    icon_manager = FontAwesomeIconManager(theme_name)
    return icon_manager


def switch_theme(theme_name):
    """Switch theme for all icons"""
    global icon_manager
    icon_manager.set_theme(theme_name)
    return icon_manager