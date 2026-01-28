"""
Theme system for TutorDraw application
Handles multiple UI themes with consistent color schemes
"""

class ThemeManager:
    def __init__(self):
        self.themes = {
            "Light": {
                "name": "light",
                "bg_color": "#ffffff",
                "text_color": "#333333",
                "accent_color": "#6965db",
                "secondary_color": "#f0f0f0",
                "border_color": "#e0e0e0",
                "highlight_color": "#e3f2fd",
                "button_hover": "#f5f5f5",
                "toolbar_bg": "#ffffff",
                "canvas_bg": "#ffffff",
                "icon_color": "#333333"
            },
            "Dark": {
                "name": "dark",
                "bg_color": "#2d2d2d",
                "text_color": "#f0f0f0",
                "accent_color": "#8ab4f8",
                "secondary_color": "#404040",
                "border_color": "#555555",
                "highlight_color": "#3a3a3a",
                "button_hover": "#3e3e3e",
                "toolbar_bg": "#3a3a3a",
                "canvas_bg": "#1e1e1e",
                "icon_color": "#ffffff"
            },
            "Charcoal": {
                "name": "charcoal",
                "bg_color": "#2a2a2a",
                "text_color": "#e0e0e0",
                "accent_color": "#a0a0a0",
                "secondary_color": "#3a3a3a",
                "border_color": "#4a4a4a",
                "highlight_color": "#353535",
                "button_hover": "#3f3f3f",
                "toolbar_bg": "#303030",
                "canvas_bg": "#252525",
                "icon_color": "#ffffff"
            },
            "Deep Blue": {
                "name": "deep_blue",
                "bg_color": "#0d47a1",
                "text_color": "#e3f2fd",
                "accent_color": "#42a5f5",
                "secondary_color": "#1565c0",
                "border_color": "#1976d2",
                "highlight_color": "#1e88e5",
                "button_hover": "#1976d2",
                "toolbar_bg": "#1565c0",
                "canvas_bg": "#0d47a1",
                "icon_color": "#ffffff"
            },
            "Colorful": {
                "name": "colorful",
                "bg_color": "#f5f5f5",
                "text_color": "#212121",
                "accent_color": "#e91e63",
                "secondary_color": "#ffcdd2",
                "border_color": "#e91e63",
                "highlight_color": "#ffecb3",
                "button_hover": "#f8bbd0",
                "toolbar_bg": "#ffffff",
                "canvas_bg": "#fafafa",
                "icon_color": "#212121"
            },
            "Jellyfish": {
                "name": "jellyfish",
                "bg_color": "#0a0f2c",
                "text_color": "#e0e0ff",
                "accent_color": "#00bcd4",  # Cyan
                "secondary_color": "#e040fb",  # Purple
                "border_color": "#ff4081",    # Pink
                "highlight_color": "#1a237e",
                "button_hover": "#0d47a1",
                "toolbar_bg": "#0c1125",
                "canvas_bg": "#080c20",
                "icon_color": "#ffffff"
            }
        }

    def get_theme(self, theme_name):
        """Get theme by name"""
        # Handle both capitalized and uncapitalized theme names
        if theme_name in self.themes:
            return self.themes[theme_name]
        theme_name_capitalized = theme_name.lower().capitalize()
        return self.themes.get(theme_name_capitalized, self.themes["Light"])

    def get_theme_stylesheet(self, theme_name):
        """Generate a comprehensive stylesheet for the theme"""
        theme = self.get_theme(theme_name)
        return {
            "bg_color": theme["bg_color"],
            "text_color": theme["text_color"],
            "accent_color": theme["accent_color"],
            "secondary_color": theme["secondary_color"],
            "border_color": theme["border_color"],
            "highlight_color": theme["highlight_color"],
            "button_hover": theme["button_hover"],
            "toolbar_bg": theme["toolbar_bg"],
            "canvas_bg": theme["canvas_bg"],
            "icon_color": theme["icon_color"]
        }

    def apply_theme_to_widget(self, widget, theme_name):
        """Apply theme to a specific widget"""
        theme = self.get_theme_stylesheet(theme_name)
        # This would be used to apply theme to individual widgets
        pass

# Global theme manager instance
theme_manager = ThemeManager()