LIGHT_THEME = {
    "name": "light",
    "excali_purple": "rgb(105, 101, 219)",
    "excali_light": "rgb(236, 236, 253)",
    "button_stylesheet_template": """
        QPushButton {{ 
            background: transparent; 
            border: none; 
            border-radius: 12px; 
            color: rgb(30, 30, 30); 
            font-size: 18px; 
            padding: 6px 10px;
        }}
        QPushButton:hover {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(245, 245, 245, 0.9), stop:1 rgba(232, 232, 232, 0.8)); 
        }}
        QPushButton:checked {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, stop:0 rgba(105, 101, 219, 0.2), stop:1 rgba(105, 101, 219, 0.05)); 
            color: {excali_purple}; 
            border: 2px solid {excali_purple}; 
            border-radius: 12px;
            font-weight: 600;
        }}
        QPushButton:pressed {{ 
            background: {excali_purple}; 
            color: white; 
        }}
    """,
    "bg_frame_stylesheet": """
        QFrame {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.95), stop:1 rgba(245, 245, 245, 0.95));
            border: 1px solid rgba(200, 200, 200, 0.3);
            border-radius: 25px; 
        }}
    """,
    "slider_stylesheet": """
        QSlider::groove:horizontal {{ 
            height: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e0e0e0, stop:1 #d0d0d0); 
            border-radius: 4px; 
            border: 1px solid #c0c0c0;
        }} 
        QSlider::handle:horizontal {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: -6px 0; 
            border-radius: 10px; 
            border: 2px solid white;
            
        }} 
        QSlider::groove:vertical {{ 
            width: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0e0e0, stop:1 #d0d0d0); 
            border-radius: 4px; 
            border: 1px solid #c0c0c0;
        }} 
        QSlider::handle:vertical {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: 0 -6px; 
            border-radius: 10px; 
            border: 2px solid white;
            
        }}
    """,
    "menu_stylesheet": """
        QMenu {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 white, stop:1 #f8f8f8); 
            border: 1px solid rgba(0, 0, 0, 0.1); 
            border-radius: 12px; 
            padding: 8px; 
            
        }} 
        QMenu::item {{ 
            color: #333; 
            padding: 10px 24px; 
            border-radius: 8px; 
            font-family: 'Segoe UI';
            font-size: 14px;
        }} 
        QMenu::item:selected {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f0f0, stop:1 #e8e8e8); 
            color: {excali_purple};
        }}
        QMenu::separator {{
            height: 1px;
            background: rgba(0, 0, 0, 0.1);
            margin: 4px 0;
        }}
    """,
    "separator_stylesheet_horizontal": "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 transparent, stop:0.5 rgba(208, 208, 208, 0.6), stop:1 transparent);",
    "separator_stylesheet_vertical": "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.5 rgba(208, 208, 208, 0.6), stop:1 transparent);",
    "canvas_background_color": "white",
    "settings_dialog_stylesheet": """
        QFrame {{ 
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.95), stop:1 rgba(245, 245, 245, 0.95));
            border: 1px solid rgba(200, 200, 200, 0.3); 
            border-radius: 20px; 
            
        }}
        QLabel {{ 
            color: #1e1e1e; 
            font-family: 'Segoe UI'; 
            font-weight: 600; 
            border: none; 
            font-size: 13px; 
        }}
        QKeySequenceEdit, QSpinBox {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f9fa, stop:1 #f0f0f0);
            color: black; 
            padding: 10px 12px; 
            border-radius: 10px; 
            border: 1px solid #ddd; 
            font-family: 'Segoe UI';
            font-size: 13px;
        }}
        QKeySequenceEdit:focus, QSpinBox:focus {{
            border: 2px solid {excali_purple};
            background: white;
        }}
        QCheckBox {{ 
            color: #1e1e1e; 
            font-weight: 500; 
            background: transparent;
            font-family: 'Segoe UI';
            font-size: 13px;
        }}
        QSlider::groove:horizontal {{ 
            height: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e0e0e0, stop:1 #d0d0d0); 
            border-radius: 4px; 
            border: 1px solid #c0c0c0;
        }} 
        QSlider::handle:horizontal {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: -6px 0; 
            border-radius: 10px; 
            border: 2px solid white;
            
        }} 
        QSlider::groove:vertical {{ 
            width: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0e0e0, stop:1 #d0d0d0); 
            border-radius: 4px; 
            border: 1px solid #c0c0c0;
        }} 
        QSlider::handle:vertical {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: 0 -6px; 
            border-radius: 10px; 
            border: 2px solid white;
            
        }}
    """
}

DARK_THEME = {
    "name": "dark",
    "excali_purple": "rgb(105, 101, 219)",
    "excali_light": "rgb(45, 45, 45)",
    "button_stylesheet_template": """
        QPushButton {{ 
            background: transparent; 
            border: none; 
            border-radius: 12px; 
            color: rgb(220, 220, 220); 
            font-size: 18px; 
            padding: 6px 10px;
        }}
        QPushButton:hover {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(60, 60, 60, 0.9), stop:1 rgba(50, 50, 50, 0.8)); 
        }}
        QPushButton:checked {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, stop:0 rgba(105, 101, 219, 0.3), stop:1 rgba(105, 101, 219, 0.1)); 
            color: {excali_purple}; 
            border: 2px solid {excali_purple}; 
            border-radius: 12px;
            font-weight: 600;
        }}
        QPushButton:pressed {{ 
            background: {excali_purple}; 
            color: white; 
        }}
    """,
    "bg_frame_stylesheet": """
        QFrame {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(45, 45, 45, 0.95), stop:1 rgba(35, 35, 35, 0.95));
            border: 1px solid rgba(80, 80, 80, 0.4);
            border-radius: 25px; 
            
        }}
    """,
    "slider_stylesheet": """
        QSlider::groove:horizontal {{ 
            height: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #444); 
            border-radius: 4px; 
            border: 1px solid #666;
        }} 
        QSlider::handle:horizontal {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: -6px 0; 
            border-radius: 10px; 
            border: 2px solid #333;
            
        }} 
        QSlider::groove:vertical {{ 
            width: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #555, stop:1 #444); 
            border-radius: 4px; 
            border: 1px solid #666;
        }} 
        QSlider::handle:vertical {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: 0 -6px; 
            border-radius: 10px; 
            border: 2px solid #333;
            
        }}
    """,
    "menu_stylesheet": """
        QMenu {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #232323, stop:1 #1a1a1a); 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            border-radius: 12px; 
            padding: 8px; 
            
        }} 
        QMenu::item {{ 
            color: #f0f0f0; 
            padding: 10px 24px; 
            border-radius: 8px; 
            font-family: 'Segoe UI';
            font-size: 14px;
        }} 
        QMenu::item:selected {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #404040, stop:1 #383838); 
            color: {excali_purple};
        }}
        QMenu::separator {{
            height: 1px;
            background: rgba(255, 255, 255, 0.1);
            margin: 4px 0;
        }}
    """,
    "separator_stylesheet_horizontal": "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 transparent, stop:0.5 rgba(100, 100, 100, 0.6), stop:1 transparent);",
    "separator_stylesheet_vertical": "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.5 rgba(100, 100, 100, 0.6), stop:1 transparent);",
    "canvas_background_color": "rgb(30, 30, 30)",
    "settings_dialog_stylesheet": """
        QFrame {{ 
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(45, 45, 45, 0.95), stop:1 rgba(35, 35, 35, 0.95));
            border: 1px solid rgba(80, 80, 80, 0.4); 
            border-radius: 20px; 
            
        }}
        QLabel {{ 
            color: #f0f0f0; 
            font-family: 'Segoe UI'; 
            font-weight: 600; 
            border: none; 
            font-size: 13px; 
        }}
        QKeySequenceEdit, QSpinBox {{ 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2d2d2d, stop:1 #252525);
            color: white; 
            padding: 10px 12px; 
            border-radius: 10px; 
            border: 1px solid #555; 
            font-family: 'Segoe UI';
            font-size: 13px;
        }}
        QKeySequenceEdit:focus, QSpinBox:focus {{
            border: 2px solid {excali_purple};
            background: #333;
        }}
        QCheckBox {{ 
            color: #f0f0f0; 
            font-weight: 500; 
            background: transparent;
            font-family: 'Segoe UI';
            font-size: 13px;
        }}
        QSlider::groove:horizontal {{ 
            height: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #444); 
            border-radius: 4px; 
            border: 1px solid #666;
        }} 
        QSlider::handle:horizontal {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: -6px 0; 
            border-radius: 10px; 
            border: 2px solid #333;
            
        }} 
        QSlider::groove:vertical {{ 
            width: 8px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #555, stop:1 #444); 
            border-radius: 4px; 
            border: 1px solid #666;
        }} 
        QSlider::handle:vertical {{ 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {excali_purple}, stop:1 #5a55b0);
            width: 20px; 
            height: 20px; 
            margin: 0 -6px; 
            border-radius: 10px; 
            border: 2px solid #333;
            
        }}
    """
}

def get_theme(theme_name):
    if theme_name == "dark":
        return DARK_THEME
    return LIGHT_THEME


def get_theme_stylesheet_comprehensive(theme_name):
    """Comprehensive theme stylesheet function to match src/themes_system interface"""
    # Define comprehensive theme data similar to src/themes_system
    themes_data = {
        "Light": {
            "name": "light",
            "bg_color": "#ffffff",
            "text_color": "#333333",
            "accent_color": "#6965db",
            "secondary_color": "#f0f0f0",
            "border_color": "#e0e0e0",
            "highlight_color": "#e3f2fd",
            "button_hover": "#d1d0ff",
            "toolbar_bg": "#ffffff",
            "canvas_bg": "#ffffff",
            "icon_color": "#333333"
        },
        "Dark": {
            "name": "dark",
            "bg_color": "#01002c",
            "text_color": "#f0f0f0",
            "accent_color": "#8ab4f8",
            "secondary_color": "#404040",
            "border_color": "#555555",
            "highlight_color": "#3a3a3a",
            "button_hover": "#3e3e3e",
            "toolbar_bg": "#01002c",
            "canvas_bg": "#01002c",
            "icon_color": "#ffffff"
        },
        "Charcoal": {
            "name": "charcoal",
            "bg_color": "#2c2c2c",
            "text_color": "#f0f0f0",
            "accent_color": "#8ab4f8",
            "secondary_color": "#404040",
            "border_color": "#555555",
            "highlight_color": "#3a3a3a",
            "button_hover": "#3e3e3e",
            "toolbar_bg": "#2c2c2c",
            "canvas_bg": "#2c2c2c",
            "icon_color": "#ffffff"
        },
        "Deep Blue": {
            "name": "deep_blue",
            "bg_color": "#03005b",
            "text_color": "#e3f2fd",
            "accent_color": "#42a5f5",
            "secondary_color": "#1565c0",
            "border_color": "#555555",
            "highlight_color": "#3a3a3a",
            "button_hover": "#3e3e3e",
            "toolbar_bg": "#03005b",
            "canvas_bg": "#03005b",
            "icon_color": "#ffffff"
        },
        "Colorful": {
            "name": "colorful",
            "bg_color": "#f0f8ff",
            "text_color": "#333333",
            "accent_color": "#ff6b6b",
            "secondary_color": "#ffd93d",
            "border_color": "#cccccc",
            "highlight_color": "#e3f2fd",
            "button_hover": "#d1d0ff",
            "toolbar_bg": "#ffffff",
            "canvas_bg": "#f0f8ff",
            "icon_color": "#333333"
        },
        "Jellyfish": {
            "name": "jellyfish",
            "bg_color": "#1a1a2e",
            "text_color": "#e94560",
            "accent_color": "#0f3460",
            "secondary_color": "#16213e",
            "border_color": "#555555",
            "highlight_color": "#3a3a3a",
            "button_hover": "#3e3e3e",
            "toolbar_bg": "#1a1a2e",
            "canvas_bg": "#1a1a2e",
            "icon_color": "#e94560"
        },
        "Deep Green": {
            "name": "deep_green",
            "bg_color": "#1b2e00",
            "text_color": "#f0f0f0",
            "accent_color": "#4caf50",
            "secondary_color": "#388e3c",
            "border_color": "#555555",
            "highlight_color": "#3a3a3a",
            "button_hover": "#3e3e3e",
            "toolbar_bg": "#1b2e00",
            "canvas_bg": "#1b2e00",
            "icon_color": "#ffffff"
        }
    }
    
    # Return the theme data, defaulting to Light if not found
    return themes_data.get(theme_name, themes_data["Light"])
