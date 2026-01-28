"""
Icon management system for TutorDraw
Provides theme-aware icons with proper coloring and keyboard shortcuts
"""
from PySide6.QtWidgets import QPushButton, QApplication
from PySide6.QtCore import Qt, QFile
from PySide6.QtGui import QIcon, QColor, QPixmap, QPainter, QFont, QFontDatabase
import base64


# This is the legacy IconManager that was using Unicode characters directly.
# Since we're now using the FontAwesome system from fontawesome_icons.py,
# this class will be simplified to serve as a fallback only.

class IconManager:
    """Legacy icon manager using Unicode characters - kept for backward compatibility"""
    
    def __init__(self, theme):
        self.theme = theme
        self.icon_cache = {}
        
    def get_icon(self, icon_name, size=36):
        """Get a fallback icon using Unicode characters"""
        # This should only be used if FontAwesome is not available
        # In our updated system, this shouldn't be called
        return QIcon()


class ThemedIconButton(QPushButton):
    """A button with theme-aware icon and proper tooltip with shortcut"""
    
    def __init__(self, icon_name, tooltip, shortcut="", checkable=True, theme=None):
        super().__init__()
        self.icon_name = icon_name
        self.theme = theme
        self.is_selected = False
        
        # Try to initialize FontAwesome icons if available
        try:
            from .fontawesome_icons import initialize_icons
            theme_name = theme.get('name', 'light') if theme else 'light'
            self.fa_icon_manager = initialize_icons(theme_name)
            self.use_fa_icons = True
        except ImportError:
            # Fallback to original icon manager
            self.icon_manager = IconManager(theme) if theme else None
            self.use_fa_icons = False
        
        # Set up the button with Excalidraw-style sizing (24x24 pixels)
        self.setFixedSize(28, 28)
        self.setCheckable(checkable)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply Excalidraw-style styling
        self._setup_excalidraw_style()
        
        # Update icon and tooltip
        self.update_icon()
        self.update_tooltip(tooltip, shortcut)
    
    def _setup_excalidraw_style(self):
        """Setup Excalidraw-style button styling"""
        # Get theme colors
        if self.theme:
            bg_color = self.theme.get("bg_color", "#ffffff")
            text_color = self.theme.get("text_color", "#333333")
            accent_color = self.theme.get("excali_purple", "#6965db")
            hover_color = self.theme.get("hover_color", "#f0f0f0")
        else:
            bg_color = "#ffffff"
            text_color = "#333333"
            accent_color = "#6965db"
            hover_color = "#f0f0f0"
        
        # Create Excalidraw-style stylesheets
        self.normal_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 0px;
                color: {text_color};
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
            QPushButton:pressed {{
                background: {accent_color};
                color: white;
            }}
        """
        
        self.selected_style = f"""
            QPushButton {{
                background: {accent_color};
                border: none;
                border-radius: 6px;
                padding: 0px;
                color: white;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: {accent_color};
            }}
            QPushButton:pressed {{
                background: {accent_color};
            }}
        """
        
        self.setStyleSheet(self.normal_style)
    
    def set_selected(self, selected):
        """Set the selected state of the button."""
        self.is_selected = selected
        if selected:
            self.setStyleSheet(self.selected_style)
        else:
            self.setStyleSheet(self.normal_style)
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        if not self.is_selected:
            # Apply hover effect only if not selected
            if self.theme:
                hover_color = self.theme.get("hover_color", "#f0f0f0")
                text_color = self.theme.get("text_color", "#333333")
                hover_style = f"""
                    QPushButton {{
                        background: {hover_color};
                        border: none;
                        border-radius: 6px;
                        padding: 0px;
                        color: {text_color};
                        font-size: 20px;
                    }}
                """
                self.setStyleSheet(hover_style)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        if not self.is_selected:
            # Return to normal style when not selected
            self.setStyleSheet(self.normal_style)
        super().leaveEvent(event)
    
    def update_icon(self):
        """Update the button icon based on theme"""
        if self.use_fa_icons:
            # Use FontAwesome icons with Excalidraw sizing
            try:
                icon = self.fa_icon_manager.get_icon(self.icon_name, size=22)  # Slightly smaller than button for padding
                self.setIcon(icon)
                self.setIconSize(QSize(22, 22))  # Keep icon size consistent
            except:
                # Fallback to text if FontAwesome fails
                self.setText(self._get_fallback_char())
        else:
            # Even if use_fa_icons is False, try to initialize it
            # This ensures FontAwesome is used when available
            try:
                from .fontawesome_icons import initialize_icons
                theme_name = self.theme.get('name', 'light') if self.theme else 'light'
                self.fa_icon_manager = initialize_icons(theme_name)
                self.use_fa_icons = True
                icon = self.fa_icon_manager.get_icon(self.icon_name, size=22)
                self.setIcon(icon)
                self.setIconSize(QSize(22, 22))
            except ImportError:
                # If FontAwesome is not available, use text fallback
                self.setText(self._get_fallback_char())
    
    def update_tooltip(self, tooltip, shortcut):
        """Update the button tooltip with proper formatting"""
        if shortcut:
            self.setToolTip(f"{tooltip}\n[{shortcut}]")
        else:
            self.setToolTip(tooltip)
    
    def _get_fallback_char(self):
        """Get fallback character for icon name"""
        fallback_map = {
            "mouse": "\uf8cc",      # fa-computer-mouse
            "pencil": "\uf303",     # fa-pencil
            "select": "\uf0c5",     # fa-copy
            "shape_rect": "\uf0c8", # fa-square
            "shape_diamond": "\uf219", # fa-gem
            "shape_ellipse": "\uf111", # fa-circle
            "shape_arrow": "\uf061",   # fa-arrow-right
            "text": "\uf031",       # fa-font
            "laser": "\uf6ea",      # fa-wand-sparkles
            "eraser": "\uf12d",     # fa-eraser
            "undo": "\uf0e2",       # fa-undo
            "redo": "\uf01e",       # fa-redo
            "board": "\uf51b",      # fa-chalkboard
            "transparency": "\uf0c8", # fa-square
            "more": "\uf141",       # fa-ellipsis-vertical
            "capture": "\uf87c",    # fa-photo-film
            "settings": "\uf013",   # fa-gear
            "hide": "\uf070",       # fa-eye-slash
            "exit": "\uf00d",       # fa-xmark
            "about": "\uf05a",      # fa-circle-info
            "shapes": "\uf61f"      # fa-shapes
        }
        return fallback_map.get(self.icon_name, "?")
    
    def set_theme(self, theme):
        """Update theme for the button"""
        self.theme = theme
        if self.use_fa_icons:
            from .fontawesome_icons import switch_theme
            theme_name = theme.get('name', 'light')
            self.fa_icon_manager = switch_theme(theme_name)
        else:
            self.icon_manager = IconManager(theme)
        self.update_icon()
        
        # Apply new theme styles
        self._setup_excalidraw_style()
        # Reapply selected state if needed
        if self.is_selected:
            self.set_selected(True)


# Predefined shortcuts dictionary
SHORTCUTS = {
    "mouse": "Ctrl+M",
    "select": "Ctrl+A", 
    "pencil": "Ctrl+P",
    "shape_rect": "Ctrl+R",
    "shape_diamond": "Ctrl+D",
    "shape_ellipse": "Ctrl+E",
    "shape_arrow": "Ctrl+N",
    "text": "Ctrl+T",
    "laser": "Ctrl+L",
    "eraser": "Ctrl+X",
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Y",
    "board": "Ctrl+B",
    "transparency": "Ctrl+Shift+T",
    "capture": "Ctrl+Shift+C",
    "settings": "Ctrl+,",
    "hide": "Ctrl+H",
    "more": "Ctrl+Shift+M",
    "exit": "Ctrl+Q"
}


def get_shortcut(icon_name):
    """Get the keyboard shortcut for an icon"""
    return SHORTCUTS.get(icon_name, "")