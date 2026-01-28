from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class IconButton(QPushButton):
    def __init__(self, icon, tooltip="", shortcut="", checkable=True):
        super().__init__()
        self.setFixedSize(32, 32)  # Standardized size for all icons
        self.update_theme_style()  # Apply theme-appropriate styling
        self.setText(icon)
        self.setToolTip(f"{tooltip} ({shortcut})" if shortcut else tooltip)
        self.setCheckable(checkable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_theme_style(self):
        """Apply theme-appropriate styling"""
        # Check if parent canvas has theme information
        if hasattr(self.parent(), 'canvas') and hasattr(self.parent().canvas, 'current_theme'):
            from src.themes_system import theme_manager
            theme_name = self.parent().canvas.current_theme
            theme_data = theme_manager.get_theme_stylesheet(theme_name)
            
            # Style based on theme
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    font-size: 18px;
                    color: {theme_data['icon_color']};
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme_data['button_hover']};
                }}
                QPushButton:checked {{
                    background-color: {theme_data['highlight_color']};
                }}
                QPushButton:pressed {{
                    background-color: {theme_data['accent_color']};
                    color: white;
                }}
            """)
        else:
            # Default styling
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    font-size: 18px;
                    color: #333333;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
                QPushButton:checked {
                    background-color: #e3f2fd;
                }
                QPushButton:pressed {
                    background-color: #6965db;
                    color: white;
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
        # Try to load logo from different possible locations
        logo_paths = ["logo.png", "logo.jpg", "logo.ico", "icon.png", "assets/logo.png"]
        logo_loaded = False
        
        for logo_path in logo_paths:
            try:
                pix = QPixmap(logo_path)
                if not pix.isNull():
                    self.logo_lbl.setPixmap(pix.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    logo_loaded = True
                    break
            except:
                continue
        
        # If no logo is found, show a placeholder or just text
        if not logo_loaded:
            self.logo_lbl.setText("✏️")  # Drawing icon as placeholder
            self.logo_lbl.setStyleSheet("font-size: 18px; border: none; background: transparent;")
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
        # Complete toolset on the main toolbar - fixed icons and removed duplicates
        tools = [("🖱️", "mouse", "PC Interaction", "Ctrl+M"), ("↖", "select", "Move Object", "Ctrl+V"),
                 ("✎", "pencil", "Pencil", "Ctrl+P"), ("🖍️", "highlighter", "Highlighter", "Ctrl+H"),
                 ("⬜", "rectangle", "Rectangle", "Ctrl+R"), ("⭕", "circle", "Circle", "Ctrl+C"),
                 ("🔷", "diamond", "Diamond", "Ctrl+D"),
                 ("🪄", "laser", "Laser Pointer", "Ctrl+L"),
                 ("🔍", "zoom", "Zoom Area", "Ctrl+Z"),
                 ("🧽", "eraser", "Eraser", "Ctrl+X"), ("📝", "text", "Text", "Ctrl+T")]
        
        for icon, mode, tip, key in tools:
            btn = IconButton(icon, tip, key)
            btn.clicked.connect(lambda checked=False, m=mode: self.canvas.set_mode(m))
            inner.addWidget(btn)
            self.btns[mode] = btn

        # Fill toggle button
        self.fill_btn = IconButton("▧", "Fill Mode", "F")
        self.fill_btn.setCheckable(True)
        self.fill_btn.clicked.connect(self.toggle_fill_mode)
        inner.addWidget(self.fill_btn)
        self.btns['fill'] = self.fill_btn

        # Board toggle button
        board_btn = IconButton("📊", "Toggle Board", "")
        board_btn.clicked.connect(self.canvas.toggle_board)
        inner.addWidget(board_btn)

        # Color Palette Panel
        inner.addSpacing(6)
        self.pal_frame = QFrame()
        self.pal_frame.setStyleSheet(f"""
            background-color: {'#f8f9fa' if self.canvas.current_theme == 'light' else '#3a3a3a'}; 
            border-radius: 8px; 
            border: 1px solid {'#e0e0e0' if self.canvas.current_theme == 'light' else '#555'};
        """)
        if self.orientation == "horizontal":
            pal_lay = QHBoxLayout(self.pal_frame)
            pal_lay.setContentsMargins(2, 2, 2, 2)
        else:
            pal_lay = QVBoxLayout(self.pal_frame)
            pal_lay.setContentsMargins(2, 2, 2, 2)
        
        self.picker = QPushButton("🎨")
        self.picker.setFixedSize(24, 24)
        self.picker.setCursor(Qt.CursorShape.PointingHandCursor)
        self.picker.setStyleSheet(f"""
            background: transparent; 
            border: none; 
            font-size: 16px;
            color: {'black' if self.canvas.current_theme == 'light' else 'white'};
        """)
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
        self.more_btn = IconButton("⋮", "More", "", False)
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
        menu.exec(QCursor.pos())
        
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
        
    def apply_theme(self, theme_name):
        """Apply theme to the entire toolbar"""
        self.canvas.current_theme = theme_name
        self.update_theme_style()
