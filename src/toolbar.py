from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class IconButton(QPushButton):
    def __init__(self, icon, tooltip="", shortcut="", checkable=True):
        super().__init__()
        self.setFixedSize(32, 32)  # Standardized size for all icons
        self.update_theme_style()  # Apply theme-appropriate styling
        self.icon_name = icon
        self.setToolTip(f"{tooltip} ({shortcut})" if shortcut else tooltip)
        self.setCheckable(checkable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_icon()
        
    def showEvent(self, event):
        """Override showEvent to ensure icons are loaded when widget is shown"""
        super().showEvent(event)
        # Update icons when the widget is shown
        self.update_icon()
        
    def update_icon(self):
        """Update the icon based on the current theme"""
        # Check if parent is the canvas directly
        parent = self.parent()
        
        if parent and hasattr(parent, 'current_theme'):
            # Parent is the canvas
            self._do_update_icon_with_canvas(parent)
        elif parent and hasattr(parent, 'canvas') and hasattr(parent.canvas, 'current_theme'):
            # Parent has a canvas attribute (toolbar has canvas attribute)
            self._do_update_icon_with_canvas(parent.canvas)
        else:
            # Look up the hierarchy for canvas - check if parent's parent is the canvas
            grandparent = parent.parent() if parent else None
            if grandparent and hasattr(grandparent, 'current_theme'):
                self._do_update_icon_with_canvas(grandparent)
            else:
                # Schedule the update for later when the button is properly parented
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(100, self._do_update_icon)  # Increased delay to 100ms
    
    def _do_update_icon_with_canvas(self, canvas):
        """Actually update the icon with the given canvas"""
        try:
            # Use the new simple icon manager
            from src.modern_icons import icon_manager
            theme_name = canvas.current_theme
            
            # Update the icon manager theme
            icon_manager.set_theme(theme_name)
            
            # Create the icon with the simple icon manager
            icon = icon_manager.get_icon(self.icon_name, size=24)
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
            self.setText("")  # Clear any text
        except Exception as e:
            print(f"Error updating icon: {e}")
            import traceback
            traceback.print_exc()
            self.setText("?")  # Fallback to question mark
    
    def _do_update_icon(self):
        """Actually update the icon"""
        # Look up the hierarchy for the canvas
        current_parent = self.parent()
        canvas_found = False
        
        # Go up the hierarchy until we find the canvas or run out of parents
        while current_parent and not canvas_found:
            if hasattr(current_parent, 'canvas') and hasattr(current_parent.canvas, 'current_theme'):
                # Found canvas attribute
                self._do_update_icon_with_canvas(current_parent.canvas)
                canvas_found = True
            elif hasattr(current_parent, 'current_theme'):
                # Direct parent is canvas
                self._do_update_icon_with_canvas(current_parent)
                canvas_found = True
            else:
                # Move up to the next parent
                current_parent = current_parent.parent()
        
        if not canvas_found:
            # Final fallback to text
            self.setText("?")
        
    def _get_fallback_icon_text(self):
        """Get fallback text representation for icons"""
        fallback_map = {
            'board': '📊',
            'settings': '⚙️',
            'more': '⋮',
            # Add more as needed
        }
        return fallback_map.get(self.icon_name, "?")
        
    def update_theme_style(self):
        """Apply theme-appropriate styling"""
        # Check if parent canvas has theme information
        if hasattr(self.parent(), 'canvas') and hasattr(self.parent().canvas, 'current_theme'):
            from src.themes_system import theme_manager
            theme_name = self.parent().canvas.current_theme
            theme_data = theme_manager.get_theme_stylesheet(theme_name)
            
            # Determine if this is a dark theme
            dark_themes = ["dark", "deep blue", "jellyfish", "charcoal", "midnight", "night", "deep green"]
            is_dark_theme = theme_name.lower() in dark_themes
            
            # Choose appropriate background colors based on theme
            active_bg_color = "#403e6d" if is_dark_theme else "#e0dfff"
            
            # Style based on theme
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 7px; /* Rounded corners for buttons */
                    font-size: 16px; /* Smaller font size for modern look */
                    color: {theme_data['icon_color']};
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme_data['button_hover']};
                }}
                QPushButton:checked {{
                    background-color: {active_bg_color}; /* Appropriate background for theme */
                }}
                QPushButton:pressed {{
                    background-color: {active_bg_color};
                    border: 2px solid #817dff; /* Border color when pressed */
                }}
            """)
        else:
            # Default styling
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 7px; /* Rounded corners for buttons */
                    font-size: 16px; /* Smaller font size for modern look */
                    color: #ffffff; /* White icons for default dark-like appearance */
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
                QPushButton:checked {
                    background-color: #403E6a; /* Darker background for dark themes */
                }
                QPushButton:pressed {
                    background-color: #403E6a;
                    border: 2px solid #817dff; /* Border color when pressed */
                }
            """)

class TutorToolbar(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.orientation = getattr(canvas, 'toolbar_orientation', 'horizontal')
        # Change window flags to make toolbar stay on top and accept focus
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize oldPos to prevent errors
        self.oldPos = QPoint(0, 0)
        
        # Use appropriate layout based on orientation
        if self.orientation == "horizontal":
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)
            
        self.bg = QFrame()
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0,100))
        shadow.setOffset(0, 3)  # Reduced blur
        self.bg.setGraphicsEffect(shadow)

        # Use appropriate inner layout based on orientation
        if self.orientation == "horizontal":
            inner = QHBoxLayout(self.bg)
            inner.setContentsMargins(8, 4, 8, 4)  # More compact margins
        else:
            inner = QVBoxLayout(self.bg)
            inner.setContentsMargins(4, 8, 4, 8)  # More compact margins

        self.logo_lbl = QLabel()
        # Try to load logo from the icons folder
        logo_loaded = False
        
        # Try SVG version first
        try:
            from PyQt5.QtSvg import QSvgWidget
            import os
            svg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons', 'logo-01.svg')
            if os.path.exists(svg_path):
                # For SVG, we'll need to render it to pixmap
                from PyQt5.QtSvg import QSvgRenderer
                from PyQt5.QtGui import QPainter
                renderer = QSvgRenderer(svg_path)
                pixmap = QPixmap(24, 24)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                self.logo_lbl.setPixmap(pixmap)
                logo_loaded = True
        except Exception as e:
            print(f"Failed to load SVG logo: {e}")
        
        # Try PNG version if SVG failed
        if not logo_loaded:
            try:
                import os
                png_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons', 'tutorDraw-logoX92.png')
                pix = QPixmap(png_path)
                if not pix.isNull():
                    self.logo_lbl.setPixmap(pix.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    logo_loaded = True
            except Exception as e:
                print(f"Failed to load PNG logo: {e}")
        
        # If no logo is found, show a simple placeholder
        if not logo_loaded:
            self.logo_lbl.setText("TD")  # TutorDraw initials as fallback
            self.logo_lbl.setStyleSheet("font-size: 14px; font-weight: bold; border: none; background: transparent; color: #6965db;")
        else:
            self.logo_lbl.setStyleSheet("border: none; background: transparent;")
        inner.addWidget(self.logo_lbl)
        
        inner.addSpacing(3)
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setFixedHeight(20)
        sep.setStyleSheet("background: #eee;" if self.canvas.current_theme == "light" else "background: #555;")
        inner.addWidget(sep)
        inner.addSpacing(3)

        self.btns = {}
        # Create tool buttons with proper icon names - use empty shortcuts since they'll be updated
        tools = [("mouse", "mouse", "Mouse"),
                 ("select", "select", "Select"),
                 ("pencil", "pencil", "Pencil"),
                 ("highlighter", "highlighter", "Highlighter"),
                 ("rect", "rect", "Rectangle"),
                 ("ellipse", "ellipse", "Circle"),
                 ("diamond", "diamond", "Diamond"),
                 ("arrow", "arrow", "Arrow"),
                 ("laser", "laser", "Laser Pointer"),
                 ("zoom", "zoom", "Zoom Area"),
                 ("eraser", "eraser", "Eraser"),
                 ("text", "text", "Text")]
        
        for icon_name, mode, tip in tools:
            btn = IconButton(icon_name, tip, "")  # Pass empty shortcut, will be updated via tooltip
            btn.clicked.connect(lambda checked=False, m=mode: self.canvas.set_mode(m))
            inner.addWidget(btn)
            self.btns[mode] = btn
        
        # Update tooltips with current shortcuts from canvas
        self.update_tooltips()

        # Fill toggle button
        self.fill_btn = IconButton("fill", "Fill Mode", "")
        self.fill_btn.setCheckable(True)
        self.fill_btn.clicked.connect(self.toggle_fill_mode)
        inner.addWidget(self.fill_btn)
        self.btns['fill'] = self.fill_btn

        # Board toggle button
        board_btn = IconButton("board", "Toggle Board", "")
        board_btn.clicked.connect(self.canvas.toggle_board)
        inner.addWidget(board_btn)
        self.btns['board'] = board_btn

        # Color Palette Panel
        inner.addSpacing(6)
        self.pal_frame = QFrame()
        self.pal_frame.setStyleSheet(f"""
            background-color: {'#f8f9fa' if self.canvas.current_theme == 'light' else '#3a3a3a'}; 
            border-radius: 12px; /* Fully rounded corners */
            border: 1px solid {'#e0e0e0' if self.canvas.current_theme == 'light' else '#555'};
        """)
        if self.orientation == "horizontal":
            pal_lay = QHBoxLayout(self.pal_frame)
            pal_lay.setContentsMargins(2, 2, 2, 2)
        else:
            pal_lay = QVBoxLayout(self.pal_frame)
            pal_lay.setContentsMargins(2, 2, 2, 2)
        
        self.picker = QPushButton()
        self.picker.setFixedSize(24, 24)
        self.picker.setCursor(Qt.CursorShape.PointingHandCursor)
        # Show the actual selected color as a dot
        self.update_color_picker()
        self.picker.clicked.connect(self.canvas.open_color_picker)
        pal_lay.addWidget(self.picker)
        inner.addWidget(self.pal_frame)
        inner.addSpacing(6)

        # Width control buttons
        width_frame = QFrame()
        width_frame.setStyleSheet(f"""
            background-color: {'#f8f9fa' if self.canvas.current_theme == 'light' else '#3a3a3a'}; 
            border-radius: 8px; 
            border: 1px solid {'#e0e0e0' if self.canvas.current_theme == 'light' else '#555'};
        """)
        if self.orientation == "horizontal":
            width_lay = QHBoxLayout(width_frame)
            width_lay.setContentsMargins(2, 2, 2, 2)
        else:
            width_lay = QVBoxLayout(width_frame)
            width_lay.setContentsMargins(2, 2, 2, 2)
            
        # Decrease width button
        dec_width_btn = QPushButton("➖")
        dec_width_btn.setFixedSize(24, 24)
        dec_width_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dec_width_btn.setStyleSheet(f"""
            background: transparent; 
            border: none; 
            font-size: 16px;
            color: {'black' if self.canvas.current_theme == 'light' else 'white'};
        """)
        dec_width_btn.clicked.connect(self.decrease_width)
        width_lay.addWidget(dec_width_btn)
        
        # Width display
        self.width_label = QLabel("4")
        self.width_label.setFixedSize(24, 24)
        self.width_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.width_label.setStyleSheet(f"""
            color: {'black' if self.canvas.current_theme == 'light' else 'white'};
            font-weight: bold;
            font-size: 12px;
        """)
        width_lay.addWidget(self.width_label)
        
        # Increase width button
        inc_width_btn = QPushButton("➕")
        inc_width_btn.setFixedSize(24, 24)
        inc_width_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        inc_width_btn.setStyleSheet(f"""
            background: transparent; 
            border: none; 
            font-size: 16px;
            color: {'black' if self.canvas.current_theme == 'light' else 'white'};
        """)
        inc_width_btn.clicked.connect(self.increase_width)
        width_lay.addWidget(inc_width_btn)
        
        inner.addWidget(width_frame)
        inner.addSpacing(6)

        # More menu button
        self.more_btn = IconButton("more", "More", "", False)
        self.more_btn.clicked.connect(self.show_more_menu)
        inner.addWidget(self.more_btn)
        layout.addWidget(self.bg)

        # Update theme styling after all buttons are created
        self.update_theme_style()

    def mousePressEvent(self, event): 
        self.oldPos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def show_more_menu(self):
        menu = QMenu(self)
        # Apply theme to menu
        if self.canvas.current_theme == "dark":
            menu.setStyleSheet("""
                QMenu { 
                    background-color: #2d2d2d; 
                    color: white; 
                    border: 1px solid #555555;
                }
                QMenu::item { 
                    background-color: transparent; 
                    padding: 5px 20px; 
                    color: white;
                }
                QMenu::item:selected { 
                    background-color: #3e3e3e; 
                }
            """)
        else:  # light theme
            menu.setStyleSheet("""
                QMenu { 
                    background-color: white; 
                    color: black; 
                    border: 1px solid #d1d1d1;
                }
                QMenu::item { 
                    background-color: transparent; 
                    padding: 5px 20px; 
                    color: black;
                }
                QMenu::item:selected { 
                    background-color: #f0f0f0; 
                }
            """)
        
        menu.addAction("⚙️ Settings").triggered.connect(self.canvas.open_settings)
        menu.addAction("🗑️ Clear All").triggered.connect(self.canvas.clear_canvas)
        
        # Capture submenu
        capture_menu = QMenu("Capture", menu)
        capture_menu.addAction("📸 Full Screen Screenshot").triggered.connect(self.canvas.capture_full_screen_screenshot)
        capture_menu.addAction("✂️ Area Screenshot").triggered.connect(self.canvas.capture_area_screenshot)
        capture_menu.addAction("↕️ Scrolling Screenshot").triggered.connect(self.canvas.capture_scrolling_screenshot)
        menu.addMenu(capture_menu)
        
        # Recording submenu
        record_menu = QMenu("Record", menu)
        record_menu.addAction("🎥 Full Screen Record").triggered.connect(self.canvas.record_full_screen)
        record_menu.addAction("🎬 Area Record").triggered.connect(self.canvas.record_area)
        menu.addMenu(record_menu)
        
        menu.addSeparator()
        menu.addAction("🙈 Hide Toolbar").triggered.connect(self.canvas.hide_toolbar_permanent)
        menu.addSeparator()
        menu.addAction("❌ Exit").triggered.connect(QApplication.instance().quit)
        
        # Get the position of the more button to anchor the menu
        more_btn_global_pos = self.more_btn.mapToGlobal(QPoint(0, 0))
        
        # Position the menu directly below or beside the more button
        if self.orientation == "horizontal":
            # For horizontal toolbar, show menu below the more button
            menu_x = more_btn_global_pos.x()
            menu_y = more_btn_global_pos.y() + self.more_btn.height()
        else:
            # For vertical toolbar, show menu to the side of the more button
            if more_btn_global_pos.x() > self.canvas.width() // 2:
                # Toolbar is on the right side, show menu to the left of the button
                menu_x = more_btn_global_pos.x() - menu.sizeHint().width()
            else:
                # Toolbar is on the left side, show menu to the right of the button
                menu_x = more_btn_global_pos.x() + self.more_btn.width()
            menu_y = more_btn_global_pos.y()
        
        # Ensure menu stays within screen bounds
        screen_geometry = QApplication.desktop().screenGeometry()
        menu_x = max(0, min(menu_x, screen_geometry.width() - menu.sizeHint().width()))
        menu_y = max(0, min(menu_y, screen_geometry.height() - menu.sizeHint().height()))
        
        # Set menu to stay on top to ensure it appears above the toolbar
        menu.setWindowFlags(Qt.Popup | Qt.WindowStaysOnTopHint)
        menu.exec(QPoint(menu_x, menu_y))
        
    def decrease_width(self):
        """Decrease the current drawing width"""
        self.canvas.current_thickness = max(1, self.canvas.current_thickness - 1)
        self.width_label.setText(str(self.canvas.current_thickness))
        self.update_width_display()
        # Ensure toolbar remains responsive and on top
        self.raise_()
        self.activateWindow()
        
    def increase_width(self):
        """Increase the current drawing width"""
        self.canvas.current_thickness = min(12, self.canvas.current_thickness + 1)  # Reduced max to 12
        self.width_label.setText(str(self.canvas.current_thickness))
        self.update_width_display()
        # Ensure toolbar remains responsive and on top
        self.raise_()
        self.activateWindow()
        
    def update_width_display(self):
        """Update the width display with current theme colors"""
        color = 'black' if self.canvas.current_theme == 'light' else 'white'
        self.width_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 12px;
        """)

    def toggle_fill_mode(self):
        """Toggle fill mode for shapes"""
        self.canvas.fill_mode_enabled = not self.canvas.fill_mode_enabled
        # Update button appearance
        if self.canvas.fill_mode_enabled:
            self.fill_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a73e8;
                    color: white;
                    border: none;
                    font-size: 18px;
                    border-radius: 6px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #0d62d0;
                }
            """)
        else:
            self.fill_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 18px;
                    color: black;
                    border-radius: 6px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

    def update_theme_style(self):
        """Update toolbar styling based on current theme"""
        from src.themes_system import theme_manager
        theme_data = theme_manager.get_theme_stylesheet(self.canvas.current_theme)
        
        # Update toolbar background
        self.bg.setStyleSheet(f"""
            background-color: {theme_data['toolbar_bg']};
            border-radius: 12px;
            border: 1px solid {theme_data['border_color']};
        """)
        
        # Update all icon buttons
        for btn in self.btns.values():
            btn.update_theme_style()  # Use button's own theme method
            
        # Update the more button specifically
        self.more_btn.update_theme_style()  # Use button's own theme method
        
    def update_color_picker(self):
        """Update the color picker button to show the current selected color"""
        if hasattr(self.canvas, 'current_color'):
            color_hex = self.canvas.current_color.name()
            
            # Get theme-appropriate border color
            if hasattr(self.canvas, 'current_theme'):
                from src.themes_system import theme_manager
                theme_data = theme_manager.get_theme_stylesheet(self.canvas.current_theme)
                text_color = theme_data["text_color"]
                border_color = theme_data["border_color"]
            else:
                # Default to light theme colors if no theme is set
                text_color = "#333333"
                border_color = "#e0e0e0"
                
            self.picker.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_hex};
                    border: 2px solid {border_color};
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    border: 2px solid {text_color};
                }}
            """)
    
    def apply_theme(self, theme_name):
        """Apply theme to the entire toolbar"""
        self.canvas.current_theme = theme_name
        self.update_theme_style()
        self.update_color_picker()  # Also update color picker when theme changes
        
        # Refresh all button icons to reflect the new theme
        for child in self.findChildren(IconButton):
            child.update_icon()
    
    def update_tooltips(self):
        """Update tooltips for all buttons with current shortcuts from canvas"""
        # Define the mapping between button modes and their descriptions
        tooltip_descriptions = {
            "mouse": "Mouse - Select and move shapes",
            "select": "Select - Select and transform shapes",
            "pencil": "Pencil - Draw freehand lines",
            "highlighter": "Highlighter - Highlight text or areas",
            "rect": "Rectangle - Draw rectangles",
            "ellipse": "Circle - Draw circles and ellipses",
            "diamond": "Diamond - Draw diamond shapes",
            "arrow": "Arrow - Draw arrows",
            "laser": "Laser Pointer - Point and highlight",
            "zoom": "Zoom Area - Zoom in on specific area",
            "eraser": "Eraser - Erase drawn shapes",
            "text": "Text - Add text annotations",
            "fill": "Fill Mode - Toggle shape fill mode",
            "board": "Toggle Board - Switch between annotation and board modes"
        }
        
        # Update tooltips for all buttons
        for mode, btn in self.btns.items():
            if mode in tooltip_descriptions:
                description = tooltip_descriptions[mode]
                # Get the current shortcut for this mode from canvas
                current_shortcut = self.canvas.shortcuts.get(mode, "")
                if current_shortcut:
                    tooltip_text = f"{description}\nShortcut: {current_shortcut}"
                else:
                    tooltip_text = description
                btn.setToolTip(tooltip_text)
