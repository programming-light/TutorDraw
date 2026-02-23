import time
import math
import os
import json
import tempfile

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QMessageBox, QColorDialog, QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QShortcut, QSlider
)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QRect, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QPainterPath, QFont, QRadialGradient, QBrush, QFontMetrics, QIcon, QKeySequence, QPolygonF
)

CONFIG_FILE = "tutordraw_settings.json"

class TutorShape:
    def __init__(self, mode, start, color, thickness=4, text="", fill_color=None, font_size=22, font_bold=False, font_italic=False):
        self.mode = mode
        self.points = [start]
        self.color = QColor(color) if isinstance(color, str) else color
        self.thickness = thickness
        self.text = text
        self.fill_color = QColor(fill_color) if fill_color else None
        self.end_pos = start
        self.is_selected = False
        # Transformation properties
        self.rotation = 0  # Rotation angle in degrees
        self.scale_x = 1.0  # Horizontal scale factor
        self.scale_y = 1.0  # Vertical scale factor
        self.original_bounding_rect = None  # Store original bounding rect for transformations
        # Font properties for text elements
        self.font_size = font_size
        self.font_bold = font_bold
        self.font_italic = font_italic

class LaserTrail:
    def __init__(self, start_pos, color, thickness, duration, smoothness):
        self.points = [start_pos]
        self.timestamps = [time.monotonic()]
        self.color = QColor(color) if isinstance(color, str) else color
        self.thickness = thickness
        self.duration = duration
        self.smoothness = smoothness
    
    def add_point(self, pos):
        self.points.append(pos)
        self.timestamps.append(time.monotonic())
    
    def cleanup_old_points(self, current_time):
        while self.timestamps and current_time - self.timestamps[0] > self.duration:
            self.points.pop(0)
            self.timestamps.pop(0)
    
    def is_empty(self):
        return len(self.points) == 0
    
    def get_interpolated_points(self, smoothness):
        if len(self.points) < 2:
            return self.points
        
        interpolated = []
        for i in range(len(self.points) - 1):
            p1, p2 = self.points[i], self.points[i + 1]
            interpolated.append(p1)
            # Add smooth intermediate points
            for j in range(1, smoothness):
                t = j / smoothness
                x = p1.x() * (1 - t) + p2.x() * t
                y = p1.y() * (1 - t) + p2.y() * t
                interpolated.append(QPointF(x, y))
        interpolated.append(self.points[-1])
        return interpolated

class HideHandle(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedSize(40, 40)
        # Position with maximum z-index above all annotations
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Ensure it can receive mouse events even with annotations
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setFocusPolicy(Qt.NoFocus)
        # Maximum priority to stay above all drawing
        self.setWindowOpacity(1.0)
        self.raise_()
        self.activateWindow()
        print("🔺 Hide handle initialized with maximum z-index")
        
        # Create layout for logo with white background
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # Small margins for border
        
        # Create logo label with white background and rounded border
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(36, 36)
        self.logo_label.setStyleSheet("""
            background-color: white;
            border-radius: 7px;
            border: none;
        """)
        self.load_hide_handle_logo()
        layout.addWidget(self.logo_label)
        
        # Import theme manager inside the method to avoid circular imports
        from src.themes_system import theme_manager
        self.apply_theme(getattr(self.canvas, 'current_theme', 'Light'))
        self.hide()
        
        # Animation for toolbar peek
        self.animation = None
        
        # State tracking
        self.is_hovered = False

    def load_hide_handle_logo(self):
        """Load the PNG logo with white background and rounded border"""
        logo_loaded = False
        
        # Use the PNG logo as requested since SVG isn't showing correctly
        try:
            from PyQt5.QtGui import QPixmap
            import os
            
            # Use the PNG file you specified
            png_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons', 'tutorDraw-logoX92.png')
            print(f"Loading PNG logo from: {png_path}")
            
            if os.path.exists(png_path):
                pix = QPixmap(png_path)
                if not pix.isNull():
                    # Scale the logo to fit properly
                    scaled_pixmap = pix.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.logo_label.setPixmap(scaled_pixmap)
                    logo_loaded = True
                    print("✅ PNG logo loaded successfully for hide handle")
                else:
                    print("❌ PNG file is invalid or corrupted")
            else:
                print(f"❌ PNG file not found at: {png_path}")
        except Exception as e:
            print(f"❌ Failed to load PNG logo: {e}")
        
        # Fallback if PNG also fails
        if not logo_loaded:
            print("⚠️ Using text fallback - please check PNG file in icons/ folder")
            self.logo_label.setText("📘")
            self.logo_label.setAlignment(Qt.AlignCenter)
            self.logo_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #6965db;")
    
    def apply_theme(self, theme_name):
        """Apply theme to the hide handle"""
        # Import theme manager inside the method to avoid circular imports
        from src.themes_system import theme_manager
        theme_data = theme_manager.get_theme_stylesheet(theme_name)
        accent_color = theme_data['accent_color']
        icon_color = theme_data['icon_color']
        
        self.setStyleSheet(f"""
            background: {accent_color};
            border-radius: 20px;
            border: 2px solid {icon_color};
            transition: all 0.3s ease;
        """)
    
    def mousePressEvent(self, event):
        # Toggle toolbar visibility on click
        self.canvas.toggle_toolbar_visibility()
    
    def enterEvent(self, event):
        # Show toolbar immediately on hover
        self.is_hovered = True
        
        # Always show toolbar when hovering - no conditions
        self.canvas.peek_toolbar_modern()
        
        # Enhanced hover styling with white background
        self.setStyleSheet("""
            background: white;
            border-radius: 20px;
            border: 2px solid #6965db;
        """)
        
        # Ensure toolbar visibility and focus
        if self.canvas.toolbar:
            self.canvas.toolbar.raise_()
            self.canvas.toolbar.activateWindow()
            self.canvas.toolbar.show()
            self.canvas.toolbar.setWindowOpacity(1.0)
        
        # Ensure hide handle stays on top of ALL annotations with maximum z-index
        self.raise_()
        self.activateWindow()
        self.setWindowOpacity(1.0)
        # Force to front
        self.setParent(None)
        self.show()
        
        # Debug: Print when hover is detected
        print("🔍 Hide handle hover detected - showing toolbar")
    
    def leaveEvent(self, event):
        # Hide toolbar when leaving if it was peeking
        self.is_hovered = False
        if self.canvas.is_hidden:
            # Delay hiding to allow for toolbar interaction
            QTimer.singleShot(1500, self.maybe_hide_toolbar_modern)
        
        # Return to normal styling
        self.setStyleSheet("""
            background: rgba(105, 101, 219, 0.9);
            border-radius: 20px;
            border: 2px solid white;
        """)
    
    def maybe_hide_toolbar_modern(self):
        # Only hide the toolbar if neither the toolbar nor the handle is being hovered
        if (self.canvas.is_hidden and 
            self.canvas.toolbar and 
            not self.canvas.toolbar.underMouse() and 
            not self.underMouse() and
            not self.is_hovered):
            self.canvas.complete_toolbar_hide_modern()
    
    def update_hover_state(self, is_hovered):
        """Update the hover state of the hide handle"""
        self.is_hovered = is_hovered
        if is_hovered:
            self.setStyleSheet("""
                background: rgba(105, 101, 219, 1.0);
                border-radius: 20px;
                border: 2px solid white;
                transform: scale(1.1);
            """)
        else:
            self.setStyleSheet("""
                background: rgba(105, 101, 219, 0.9);
                border-radius: 20px;
                border: 2px solid white;
            """)

class TutorToolbar(QWidget):
    def __init__(self, canvas, orientation="horizontal"):
        super().__init__()
        self.canvas = canvas
        self.orientation = orientation
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.btns = {}
        self.setup_ui()
    
    def setup_ui(self):
        from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QFrame
        from PyQt5.QtGui import QFont
        
        # Main layout
        if self.orientation == "horizontal":
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)
        
        # Background frame
        self.bg = QFrame()
        self.bg.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        """)
        
        if self.orientation == "horizontal":
            inner = QHBoxLayout(self.bg)
        else:
            inner = QVBoxLayout(self.bg)
        
        # Logo
        logo = QLabel("✏️")
        logo.setStyleSheet("font-size: 18px; border: none;")
        inner.addWidget(logo)
        
        inner.addSpacing(5)
        
        # Separator
        sep = QFrame()
        if self.orientation == "horizontal":
            sep.setFixedWidth(1)
            sep.setFixedHeight(20)
        else:
            sep.setFixedWidth(20)
            sep.setFixedHeight(1)
        sep.setStyleSheet("background: #ccc;")
        inner.addWidget(sep)
        
        inner.addSpacing(5)
        
        # Tools
        tools = [
            ("🖱️", "mouse", "Mouse"),
            ("↖", "select", "Select"), 
            ("✎", "pencil", "Pencil"),
            ("🖍️", "highlighter", "Highlighter"),
            ("⬜", "rect", "Rectangle"),
            ("🔷", "diamond", "Diamond"),
            ("⭕", "circle", "Circle"),
            ("🪄", "laser", "Laser"),
            ("🔍", "zoom", "Zoom"),
            ("📝", "text", "Text"),
            ("🧽", "eraser", "Eraser")
        ]
        
        for icon, mode, tooltip in tools:
            btn = QPushButton(icon)
            btn.setFixedSize(30, 30)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setFocusPolicy(Qt.StrongFocus)  # Ensure button can receive focus
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                    border-radius: 6px;
                }
                QPushButton:checked {
                    background: #e0e0e0;
                    border-radius: 6px;
                }
                QPushButton:focus {
                    border: 2px solid #6965db;
                    border-radius: 6px;
                }
            """)
            btn.clicked.connect(lambda checked, m=mode: self.canvas.set_mode(m))
            inner.addWidget(btn)
            self.btns[mode] = btn
        
        # Color button
        self.color_btn = QPushButton("🎨")
        self.color_btn.setFixedSize(30, 30)
        self.color_btn.setStyleSheet("""
            QPushButton {
                background: #90EE90;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #70EE70;
            }
        """)
        self.color_btn.clicked.connect(self.canvas.open_color_picker)
        inner.addWidget(self.color_btn)
        
        # Fill mode button
        fill_btn = QPushButton("▧")
        fill_btn.setFixedSize(30, 30)
        fill_btn.setCheckable(True)
        fill_btn.setToolTip("Fill Mode")
        fill_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
            QPushButton:checked {
                background: #e0e0e0;
                border-radius: 6px;
            }
        """)
        fill_btn.clicked.connect(self.toggle_fill_mode)
        inner.addWidget(fill_btn)
        self.btns['fill'] = fill_btn
        
        # Board toggle button
        board_btn = QPushButton("📊")
        board_btn.setFixedSize(30, 30)
        board_btn.setToolTip("Toggle Board")
        board_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
        """)
        board_btn.clicked.connect(self.canvas.toggle_board)
        inner.addWidget(board_btn)
        
        # Width controls
        dec_width_btn = QPushButton("➖")
        dec_width_btn.setFixedSize(30, 30)
        dec_width_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
        """)
        dec_width_btn.clicked.connect(self.decrease_width)
        inner.addWidget(dec_width_btn)
        
        self.width_label = QLabel(str(self.canvas.current_thickness))
        self.width_label.setFixedSize(30, 30)
        self.width_label.setAlignment(Qt.AlignCenter)
        self.width_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        inner.addWidget(self.width_label)
        
        inc_width_btn = QPushButton("➕")
        inc_width_btn.setFixedSize(30, 30)
        inc_width_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
        """)
        inc_width_btn.clicked.connect(self.increase_width)
        inner.addWidget(inc_width_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️")
        clear_btn.setFixedSize(30, 30)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
        """)
        clear_btn.clicked.connect(self.canvas.confirm_clear)
        inner.addWidget(clear_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(30, 30)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
        """)
        settings_btn.clicked.connect(self.canvas.open_settings)
        inner.addWidget(settings_btn)
        
        # Hide button
        hide_btn = QPushButton("🙈")
        hide_btn.setFixedSize(30, 30)
        hide_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
        """)
        hide_btn.clicked.connect(self.canvas.hide_toolbar_permanent)
        inner.addWidget(hide_btn)
        
        layout.addWidget(self.bg)
    
    def update_color_button(self, color):
        color_name = color.name() if hasattr(color, 'name') else color
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background: {color_name};
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: {color_name};
                opacity: 0.8;
            }}
        """)
    
    def toggle_fill_mode(self):
        self.canvas.enable_fill = not self.canvas.enable_fill
        self.btns['fill'].setChecked(self.canvas.enable_fill)
    
    def decrease_width(self):
        self.canvas.current_thickness = max(1, self.canvas.current_thickness - 1)
        self.width_label.setText(str(self.canvas.current_thickness))
        self.canvas.default_thickness = self.canvas.current_thickness
    
    def increase_width(self):
        self.canvas.current_thickness = min(20, self.canvas.current_thickness + 1)
        self.width_label.setText(str(self.canvas.current_thickness))
        self.canvas.default_thickness = self.canvas.current_thickness

class SettingsDialog(QDialog):
    def __init__(self, parent, canvas):
        super().__init__(parent)
        self.canvas = canvas
        self.setWindowTitle("Settings")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Laser settings
        laser_label = QLabel("Laser Settings:")
        layout.addWidget(laser_label)
        
        # Laser color
        color_layout = QVBoxLayout()
        color_label = QLabel("Laser Color:")
        self.color_combo = QComboBox()
        self.color_combo.addItems(["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"])
        self.color_combo.setCurrentText(canvas.laser_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)
        
        # Toolbar orientation
        orientation_label = QLabel("Toolbar Orientation:")
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["horizontal", "vertical"])
        self.orientation_combo.setCurrentText(canvas.toolbar_orientation)
        layout.addWidget(orientation_label)
        layout.addWidget(self.orientation_combo)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def accept(self):
        # Update canvas settings
        self.canvas.laser_color = self.color_combo.currentText()
        self.canvas.toolbar_orientation = self.orientation_combo.currentText()
        
        # Recreate toolbar if orientation changed
        if self.canvas.toolbar_orientation != self.canvas.toolbar.orientation:
            self.canvas.toolbar.close()
            self.canvas.toolbar.deleteLater()
            self.canvas.toolbar = TutorToolbar(self.canvas, self.canvas.toolbar_orientation)
            self.canvas.toolbar.show()
            if self.canvas.toolbar_orientation == "horizontal":
                self.canvas.toolbar.move((self.canvas.width() - self.canvas.toolbar.width()) // 2, 60)
            else:
                self.canvas.toolbar.move(60, (self.canvas.height() - self.canvas.toolbar.height()) // 2)
        
        super().accept()

class TutorCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        # Ensure canvas doesn't interfere with hide handle mouse events
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setGeometry(QApplication.primaryScreen().geometry())
        # Ensure canvas can receive keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
        # Set window icon with fallback
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons', 'tutorDraw-logoX92.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Initialize attributes needed by original toolbar first
        self.current_theme = "Light"  # Default theme
        self.toolbar_orientation = "horizontal"
        self.current_color = QColor(255, 0, 0)  # Red default for visibility
        self.current_thickness = 4
        self.default_thickness = 4
        self.enable_fill = False
        self.board_transparent = True  # Start in annotation mode (transparent)
        self.board_mode = "transparent"  # Start with transparent mode
        self.preferred_board_color = "white"  # Default board color when enabled
        self.current_text_size = 22
        self.current_text_bold = False
        self.current_text_italic = False
        
        # Selection and transformation attributes
        self.active_handle = None  # Which handle is currently being manipulated
        self.drag_start_pos = None  # Starting position for dragging/resizing
        self.original_shape_points = None  # Original points before transformation
        self.original_shape_end_pos = None  # Original end_pos before transformation
        self.original_bounding_rect = None  # Original bounding rect for transformations
        self.last_pos = None  # Last mouse position for shape movement
        
        # Add missing attributes for original toolbar compatibility
        self.fill_mode_enabled = False
        self.capture_full_screen_screenshot = lambda: print("Full screen capture")
        self.capture_area_screenshot = lambda: print("Area capture")
        self.capture_scrolling_screenshot = lambda: print("Scrolling capture")
        self.record_full_screen = lambda: print("Full screen record")
        self.record_area = lambda: print("Area record")
        self.hide_toolbar_permanent = self.hide_toolbar_permanent_func
        self.clear_canvas = self.clear_canvas_func
        
        self.laser_color = "#FF1E1E"
        self.laser_thickness = 14
        self.laser_duration = 1.5
        self.laser_smoothness = 5
        self.laser_glow = True
        
        self.shapes = []
        self.undo_stack = []
        self.redo_stack = []
        self.current_shape = None
        self.selected_shape = None
        self.input_box = None
        self.is_hidden = False
        self.laser_trails = []
        self.current_laser = None
        self.toolbar_last_pos = None
        
        # Zoom functionality
        self.zoom_factor = 1.0
        self.zoom_center = QPointF()
        self.zoom_start_pos = None
        self.zoom_end_pos = None
        self.is_zoom_active = False
        
        # Initialize with clean global shortcuts - Updated for modern capture
        self.shortcuts = {
            "mouse": "Ctrl+Alt+M", "select": "Ctrl+Alt+V", "pencil": "Ctrl+Alt+P", 
            "rect": "Ctrl+Alt+R", "ellipse": "Ctrl+Alt+E", "arrow": "Ctrl+Alt+A", 
            "text": "Ctrl+Alt+T", "eraser": "Ctrl+Alt+X", "clear": "Ctrl+Alt+C",
            "hide_show": "Ctrl+Alt+H", "toggle_board": "Ctrl+Alt+B", "undo": "Ctrl+Alt+Z", 
            "redo": "Ctrl+Alt+Y", "full_screenshot": "Ctrl+Shift+S", "area_screenshot": "Ctrl+Shift+A",
            "long_screenshot": "Ctrl+Shift+L", "scrolling_screenshot": "Ctrl+Shift+W",
            "toggle_recording": "Ctrl+Shift+R", "record_area": "Ctrl+Shift+E",
            "toggle_fill": "Ctrl+Alt+F"
        }
        
        # Initialize default save paths
        home_dir = os.path.expanduser("~")
        
        # Use a simple approach with Documents as base
        documents_dir = os.path.join(home_dir, "Documents")
        self.screenshots_path = os.path.join(documents_dir, "TutorDraw_Screenshots")
        self.videos_path = os.path.join(documents_dir, "TutorDraw_Videos")
        
        # Defer directory creation until needed to avoid startup issues
        
        # Force reset to ensure clean state
        self.force_reset_shortcuts()
        self.load_config()
        
        # Setup global keyboard shortcuts
        self.setup_global_shortcuts()

        # Add keyboard shortcuts for text formatting
        self.bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        self.bold_shortcut.activated.connect(self.toggle_text_bold)
        
        self.italic_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        self.italic_shortcut.activated.connect(self.toggle_text_italic)
        
        self.increase_font_shortcut = QShortcut(QKeySequence("Ctrl+Shift+>"), self)
        self.increase_font_shortcut.activated.connect(self.increase_text_size)
        
        self.decrease_font_shortcut = QShortcut(QKeySequence("Ctrl+Shift+<"), self)
        self.decrease_font_shortcut.activated.connect(self.decrease_text_size)

        # Use original toolbar design with 3-dot menu
        from src.toolbar import TutorToolbar
        from src.themes_system import theme_manager
        self.toolbar = TutorToolbar(self)
        # Set up system tray instead of hide handle
        self.setup_system_tray()
        
        # Position toolbar initially at top center
        screen_center = QApplication.primaryScreen().geometry().center()
        self.toolbar.move(screen_center.x() - self.toolbar.width() // 2, 50)
        self.toolbar.show()
        self.toolbar.raise_()
        
        # Initialize toolbar state tracking
        self.toolbar_last_pos = self.toolbar.pos()
        self.is_hidden = False
        # System tray starts active
        
        # System tray is positioned by the OS
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_canvas)
        self.timer.start(16)
        
        self.set_mode("pencil")
        self.show()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    d = json.load(f)
                    # Load only compatible shortcuts, ignore legacy ones
                    loaded_shortcuts = d.get("shortcuts", {})
                    # Only update shortcuts that exist in our new system
                    for action, key in loaded_shortcuts.items():
                        if action in self.shortcuts:
                            self.shortcuts[action] = key
                    self.laser_color = d.get("laser_color", self.laser_color)
                    self.laser_thickness = d.get("laser_thickness", self.laser_thickness)
                    self.laser_duration = d.get("laser_duration", self.laser_duration)
                    self.laser_smoothness = d.get("laser_smoothness", self.laser_smoothness)
                    self.laser_glow = d.get("laser_glow", self.laser_glow)
                    self.default_thickness = d.get("default_thickness", self.default_thickness)
                    self.enable_fill = d.get("enable_fill", self.enable_fill)
                    self.toolbar_orientation = d.get("toolbar_orientation", self.toolbar_orientation)
                    self.current_theme = d.get("current_theme", self.current_theme)
                    
                    # Load save paths
                    self.screenshots_path = d.get("screenshots_path", self.screenshots_path)
                    self.videos_path = d.get("videos_path", self.videos_path)
                    
                    # Ensure directories exist
                    os.makedirs(self.screenshots_path, exist_ok=True)
                    os.makedirs(self.videos_path, exist_ok=True)
            except:
                pass
        else:
            # If no config file exists, ensure we have the latest defaults
            self.ensure_latest_shortcuts()
    
    def force_reset_shortcuts(self):
        """Force reset all shortcuts to latest format - called during initialization"""
        self.shortcuts = {
            "mouse": "Ctrl+Alt+M", "select": "Ctrl+Alt+V", "pencil": "Ctrl+Alt+P", 
            "rect": "Ctrl+Alt+R", "ellipse": "Ctrl+Alt+E", "arrow": "Ctrl+Alt+A", 
            "text": "Ctrl+Alt+T", "eraser": "Ctrl+Alt+X", "clear": "Ctrl+Alt+C",
            "hide_show": "Ctrl+Alt+H", "toggle_board": "Ctrl+Alt+B", "undo": "Ctrl+Alt+Z", 
            "redo": "Ctrl+Alt+Y", "full_screenshot": "Ctrl+Alt+S", "area_screenshot": "Ctrl+Alt+Shift+S",
            "long_screenshot": "Ctrl+Alt+L", "scrolling_screenshot": "Ctrl+Alt+Shift+L",
            "toggle_recording": "Ctrl+Alt+Rec", "record_area": "Ctrl+Alt+Shift+Rec",
            "toggle_fill": "Ctrl+Alt+F"
        }
    
    def ensure_latest_shortcuts(self):
        """Ensure shortcuts are updated to the latest format"""
        latest_shortcuts = {
            "mouse": "Ctrl+Alt+M", "select": "Ctrl+Alt+V", "pencil": "Ctrl+Alt+P", 
            "rect": "Ctrl+Alt+R", "ellipse": "Ctrl+Alt+E", "arrow": "Ctrl+Alt+A", 
            "text": "Ctrl+Alt+T", "eraser": "Ctrl+Alt+X", "clear": "Ctrl+Alt+C",
            "hide_show": "Ctrl+Alt+H", "toggle_board": "Ctrl+Alt+B", "undo": "Ctrl+Alt+Z", 
            "redo": "Ctrl+Alt+Y", "full_screenshot": "Ctrl+Alt+S", "area_screenshot": "Ctrl+Alt+Shift+S",
            "long_screenshot": "Ctrl+Alt+L", "scrolling_screenshot": "Ctrl+Alt+Shift+L",
            "toggle_recording": "Ctrl+Alt+Rec", "record_area": "Ctrl+Alt+Shift+Rec",
            "toggle_fill": "Ctrl+Alt+F"
        }
        
        # Update any missing or outdated shortcuts
        for action, key in latest_shortcuts.items():
            if action not in self.shortcuts or not self.shortcuts[action].startswith("Ctrl+Alt+"):
                self.shortcuts[action] = key

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"shortcuts": self.shortcuts, "laser_color": self.laser_color, "laser_thickness": self.laser_thickness, "laser_duration": self.laser_duration, "laser_smoothness": self.laser_smoothness, "laser_glow": self.laser_glow, "default_thickness": self.default_thickness, "enable_fill": self.enable_fill, "toolbar_orientation": self.toolbar_orientation, "current_theme": self.current_theme, "screenshots_path": self.screenshots_path, "videos_path": self.videos_path}, f, indent=2)

    def hide_toolbar_permanent(self):
        self.is_hidden = True
        self.toolbar_last_pos = self.toolbar.pos()
        self.toolbar.hide()
        self.hide_handle.move(10, 10)
        self.hide_handle.show()
        
    def peek_toolbar(self):
        if self.is_hidden:
            # Position the toolbar next to the hide handle
            if self.toolbar_orientation == "horizontal":
                self.toolbar.move(self.hide_handle.x(), self.hide_handle.y() + self.hide_handle.height())
            else:
                self.toolbar.move(self.hide_handle.x() + self.hide_handle.width(), self.hide_handle.y())
            
            # Show the toolbar
            self.toolbar.show()
            self.toolbar.raise_()
            
    def restore_toolbar(self):
        self.is_hidden = False
        self.hide_handle.hide()
        if self.toolbar_last_pos:
            self.toolbar.move(self.toolbar_last_pos)
        self.toolbar.show()

    def toggle_toolbar_visibility(self):
        """Toggle toolbar between hidden and visible states with modern animation"""
        if self.is_hidden:
            # Toolbar is hidden, show it with modern expansion
            self.restore_toolbar_modern()
        else:
            # Toolbar is visible, hide it with smooth animation
            self.hide_toolbar_modern()
    
    def peek_toolbar_modern(self):
        """Show toolbar with zero gap from hide handle - attached directly"""
        # Always show toolbar when hovering, regardless of state
        if self.toolbar:
            # Position toolbar exactly at hide handle position (zero gap)
            handle_pos = self.hide_handle.pos()
            
            # Start with toolbar at exact same position as hide handle
            self.toolbar.move(handle_pos)  # Zero gap positioning
            self.toolbar.resize(40, 40)  # Start small
            self.toolbar.setWindowOpacity(0.0)
            self.toolbar.show()
            self.toolbar.raise_()
            self.toolbar.activateWindow()
            
            # Animate expansion from exact logo position
            self.animate_toolbar_expansion_from_logo_position()
            
            # Set up auto-hide behavior
            self.setup_toolbar_auto_hide()
    
    def restore_toolbar_modern(self):
        """Restore toolbar with modern animation and update system tray"""
        self.is_hidden = False
        
        if self.toolbar_last_pos:
            # Animate from system tray context to last position
            self.animate_toolbar_restore()
        else:
            # Default position
            screen_center = QApplication.primaryScreen().geometry().center()
            self.toolbar.move(screen_center.x() - self.toolbar.width() // 2, 50)
            self.toolbar.show()
        
        # Update system tray menu
        self.update_tray_menu()
        print("📤 Toolbar restored - system tray updated")
    
    def hide_toolbar_modern(self):
        """Hide toolbar with modern animation and update system tray"""
        self.is_hidden = True
        self.toolbar_last_pos = self.toolbar.pos()
        
        # Animate toolbar hide
        self.animate_toolbar_hide()
        
        # Update system tray after animation
        QTimer.singleShot(300, self.show_hide_handle_modern)
    
    def show_hide_handle_modern(self):
        """Update system tray after hiding animation"""
        # Update system tray menu to reflect hidden state
        self.update_tray_menu()
        print("📌 System tray updated for hidden toolbar")
    
    def setup_system_tray(self):
        """Set up system tray icon for hide/show functionality"""
        try:
            from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
            from PyQt5.QtGui import QIcon
            import os
            
            # Create system tray icon
            self.tray_icon = QSystemTrayIcon(self)
            
            # Load the application icon
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icons', 'tutorDraw-logoX92.png')
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
                print("✅ System tray icon loaded from PNG")
            else:
                # Fallback icon
                self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
                print("⚠️ Using fallback system tray icon")
            
            # Create context menu
            tray_menu = QMenu()
            
            # Show/Hide action
            self.toggle_action = tray_menu.addAction("Show Toolbar" if self.is_hidden else "Hide Toolbar")
            self.toggle_action.triggered.connect(self.toggle_toolbar_from_tray)
            
            # Separator
            tray_menu.addSeparator()
            
            # Capture submenu
            capture_menu = tray_menu.addMenu("📸 Capture")
            capture_menu.addAction("🖼️ Full Screen").triggered.connect(self.capture_full_screen_screenshot)
            capture_menu.addAction("✂️ Area Selection").triggered.connect(self.capture_area_screenshot)
            capture_menu.addAction("🔄 Smart Scrolling").triggered.connect(self.capture_scrolling_screenshot)
            capture_menu.addAction("💻 Code Editor").triggered.connect(self.capture_code_editor_screenshot)
            capture_menu.addAction("🖥️ Window Capture").triggered.connect(self.capture_window_screenshot)
            
            # Separator
            tray_menu.addSeparator()
            
            # Other actions
            clear_action = tray_menu.addAction("Clear Canvas")
            clear_action.triggered.connect(self.clear_canvas)
            
            settings_action = tray_menu.addAction("Settings")
            settings_action.triggered.connect(self.open_settings)
            
            tray_menu.addSeparator()
            
            exit_action = tray_menu.addAction("Exit")
            exit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            
            # Connect tray icon activation (double-click)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            # Show the tray icon
            self.tray_icon.show()
            print("✅ System tray icon created and shown")
            
        except Exception as e:
            print(f"❌ Failed to create system tray: {e}")
            self.tray_icon = None
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        from PyQt5.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.Trigger:  # Single click
            self.show_toolbar_dropdown()
        elif reason == QSystemTrayIcon.DoubleClick:
            self.toggle_toolbar_from_tray()
    
    def show_toolbar_dropdown(self):
        """Show toolbar as dropdown from system tray position"""
        if self.is_hidden:
            # Show toolbar near system tray
            self.restore_toolbar_modern()
            # Position toolbar near system tray area
            self.position_toolbar_near_tray()
            self.toggle_action.setText("Hide Toolbar")
            print("📤 Toolbar shown as dropdown from system tray")
        else:
            # Hide toolbar
            self.hide_toolbar_modern()
            self.toggle_action.setText("Show Toolbar")
            print("📥 Toolbar hidden from system tray")
    
    def position_toolbar_near_tray(self):
        """Position toolbar near system tray area"""
        try:
            # Get system tray geometry if available
            if hasattr(self, 'tray_icon') and self.tray_icon:
                # Try to get tray icon position
                tray_geometry = self.tray_icon.geometry()
                if not tray_geometry.isNull():
                    # Position toolbar below or near the tray icon
                    x = tray_geometry.x()
                    y = tray_geometry.y() + tray_geometry.height() + 10
                    self.toolbar.move(x, y)
                    print(f"📍 Toolbar positioned near tray at ({x}, {y})")
                    return
        except Exception as e:
            print(f"⚠️ Could not get tray position: {e}")
        
        # Fallback: position at top center
        screen_center = QApplication.primaryScreen().geometry().center()
        self.toolbar.move(screen_center.x() - self.toolbar.width() // 2, 50)
        print("📍 Toolbar positioned at screen center (fallback)")
    
    def toggle_toolbar_from_tray(self):
        """Toggle toolbar visibility from system tray"""
        if self.is_hidden:
            # Show toolbar
            self.restore_toolbar_modern()
            self.toggle_action.setText("Hide Toolbar")
            print("📤 Toolbar shown from system tray")
        else:
            # Hide toolbar
            self.hide_toolbar_modern()
            self.toggle_action.setText("Show Toolbar")
            print("📥 Toolbar hidden from system tray")
    
    def update_tray_menu(self):
        """Update tray menu text based on toolbar state"""
        if hasattr(self, 'toggle_action'):
            self.toggle_action.setText("Show Toolbar" if self.is_hidden else "Hide Toolbar")
    
    def position_hide_handle_at_screen_corner(self):
        """Position hide handle at screen corner based on OS"""
        # Get primary screen geometry
        screen = QApplication.primaryScreen().geometry()
        
        # Position at screen corner (top-left for Windows/Linux, top-right for Mac)
        import platform
        if platform.system() == "Darwin":  # macOS
            # Top-right corner
            x = screen.width() - self.hide_handle.width() - 20
            y = 20
        else:  # Windows/Linux
            # Top-left corner
            x = 20
            y = 20
            
        self.hide_handle.move(x, y)
        # Ensure hide handle is visible and on top
        self.hide_handle.show()
        self.hide_handle.raise_()
        self.hide_handle.activateWindow()
        print(f"📍 Hide handle positioned at: ({x}, {y})")
    
    def setup_toolbar_auto_hide(self):
        """Set up auto-hide behavior - hide when mouse leaves or tool is selected"""
        # Cancel any existing hide timer
        if hasattr(self, 'toolbar_hide_timer') and self.toolbar_hide_timer:
            self.toolbar_hide_timer.stop()
        
        # Create new timer for auto-hide
        self.toolbar_hide_timer = QTimer(self)
        self.toolbar_hide_timer.timeout.connect(self.check_toolbar_auto_hide)
        self.toolbar_hide_timer.start(100)  # Check every 100ms
    
    def check_toolbar_auto_hide(self):
        """Check if toolbar should auto-hide (system tray version)"""
        # Hide if mouse is not over toolbar (no hide handle in system tray mode)
        if (self.toolbar and not self.toolbar.underMouse() and self.is_hidden):
            self.toolbar_hide_timer.stop()
            self.toolbar.hide()
        
        # Also hide if a tool has been selected
        if (self.toolbar and not self.is_hidden and 
            hasattr(self, 'previous_mode') and self.previous_mode != self.mode):
            self.toolbar_hide_timer.stop()
            self.hide_toolbar_modern()
    
    def complete_toolbar_hide_modern(self):
        """Complete the toolbar hiding process"""
        if self.is_hidden and self.toolbar:
            self.toolbar.hide()
    
    def animate_toolbar_expansion_from_logo_position(self):
        """Animate toolbar expanding from exact logo position to full toolbar"""
        if not self.toolbar:
            return
            
        # Get target position (toolbar's last known position)
        target_pos = self.toolbar_last_pos if self.toolbar_last_pos else QPoint(100, 100)
        target_width = self.toolbar.sizeHint().width()
        target_height = self.toolbar.sizeHint().height()
        
        # Current position and size (starting from exact logo position)
        start_pos = self.toolbar.pos()  # Exact same as hide handle position
        start_width = 40
        start_height = 40
        
        # Calculate the offset to align the toolbar logo with the hide handle logo
        # The toolbar logo is typically at a specific offset within the toolbar
        logo_offset_x = 8  # Approximate offset of logo within toolbar (adjust as needed)
        logo_offset_y = 4  # Approximate offset of logo within toolbar (adjust as needed)
        
        # Adjust target position so that toolbar logo aligns with hide handle logo
        adjusted_target_pos = QPoint(
            target_pos.x() - logo_offset_x,
            target_pos.y() - logo_offset_y
        )
        
        # Animate over 25 steps for smoother transition
        steps = 25
        duration = 350  # 350ms for smoother animation
        
        for i in range(steps + 1):
            QTimer.singleShot(int(i * duration / steps), 
                            lambda step=i: self.animate_logo_expansion_step(
                                start_pos, adjusted_target_pos, 
                                start_width, target_width,
                                start_height, target_height,
                                step, steps
                            ))
    
    def animate_logo_expansion_step(self, start_pos, target_pos, start_width, target_width, 
                                   start_height, target_height, step, total_steps):
        """Single step of logo-to-toolbar expansion animation"""
        if step <= total_steps and self.toolbar:
            ratio = step / total_steps
            
            # Calculate intermediate position
            x = start_pos.x() + (target_pos.x() - start_pos.x()) * ratio
            y = start_pos.y() + (target_pos.y() - start_pos.y()) * ratio
            
            # Calculate intermediate size (non-linear for more natural feel)
            # Start slow, accelerate in middle, slow down at end
            if ratio < 0.5:
                size_progress = 0.5 * (ratio * 2) ** 2  # Quadratic easing in
            else:
                size_progress = 0.5 + 0.5 * (1 - (1 - (ratio - 0.5) * 2) ** 2)  # Quadratic easing out
            
            width = int(start_width + (target_width - start_width) * size_progress)
            height = int(start_height + (target_height - start_height) * size_progress)
            
            # Apply transformations
            self.toolbar.move(int(x), int(y))
            self.toolbar.resize(width, height)
            
            # Opacity animation with easing
            opacity = min(1.0, ratio * 1.5)  # Slightly faster fade in
            self.toolbar.setWindowOpacity(opacity)
            
            # Update toolbar content
            self.toolbar.update()
        elif step > total_steps:
            # Animation complete - ensure final state
            self.toolbar.resize(target_width, target_height)
            self.toolbar.move(target_pos)
            self.toolbar.setWindowOpacity(1.0)
            self.toolbar.update()
    
    def animate_expansion_step(self, start_pos, target_pos, start_width, target_width, 
                              start_height, target_height, step, total_steps):
        """Single step of the expansion animation (legacy method)"""
        if step <= total_steps and self.toolbar:
            ratio = step / total_steps
            
            # Calculate intermediate position
            x = start_pos.x() + (target_pos.x() - start_pos.x()) * ratio
            y = start_pos.y() + (target_pos.y() - start_pos.y()) * ratio
            
            # Calculate intermediate size
            width = int(start_width + (target_width - start_width) * ratio)
            height = int(start_height + (target_height - start_height) * ratio)
            
            # Apply transformations
            self.toolbar.move(int(x), int(y))
            self.toolbar.resize(width, height)
            
            # Opacity animation
            opacity = min(1.0, ratio * 2)  # Fade in faster
            self.toolbar.setWindowOpacity(opacity)
            
            # Update toolbar content
            self.toolbar.update()
        elif step > total_steps:
            # Animation complete - ensure final state
            self.toolbar.resize(target_width, target_height)
            self.toolbar.move(target_pos)
            self.toolbar.setWindowOpacity(1.0)
            self.toolbar.update()
    
    def animate_toolbar_expansion(self):
        """Animate toolbar expansion when peeking (legacy method)"""
        # Simple opacity animation for now
        self.toolbar.setWindowOpacity(0.0)
        self.toolbar.show()
        
        # Fade in animation
        for i in range(11):
            QTimer.singleShot(i * 20, lambda opacity=i/10.0: self.toolbar.setWindowOpacity(opacity))
    
    def animate_toolbar_hide(self):
        """Animate toolbar hiding (system tray version)"""
        # Simple fade out animation for system tray
        if self.toolbar:
            # Fade out animation
            self.toolbar.setWindowOpacity(0.0)
            self.toolbar.hide()
            
            # Complete the hiding process
            self.complete_toolbar_hide_modern()
    
    def animate_step_hide_with_shrink(self, start_pos, end_pos, start_size, end_size, step, total_steps):
        """Single step of hide animation with size reduction"""
        if step <= total_steps and self.toolbar:
            ratio = step / total_steps
            
            # Calculate intermediate position
            x = start_pos.x() + (end_pos.x() - start_pos.x()) * ratio
            y = start_pos.y() + (end_pos.y() - start_pos.y()) * ratio
            
            # Calculate intermediate size
            width = int(start_size.width() + (end_size.width() - start_size.width()) * ratio)
            height = int(start_size.height() + (end_size.height() - start_size.height()) * ratio)
            
            # Apply transformations
            self.toolbar.move(int(x), int(y))
            self.toolbar.resize(width, height)
            
            # Opacity animation
            opacity = 1.0 - (ratio * 0.8)  # Don't fade out completely until end
            self.toolbar.setWindowOpacity(opacity)
            
            # Update toolbar content
            self.toolbar.update()
        elif step > total_steps:
            # Final hide
            self.toolbar.hide()
    
    def animate_step_hide(self, start_pos, end_pos, step, total_steps):
        """Single step of hide animation (legacy method)"""
        if step <= total_steps and self.toolbar:
            # Calculate intermediate position
            ratio = step / total_steps
            x = start_pos.x() + (end_pos.x() - start_pos.x()) * ratio
            y = start_pos.y() + (end_pos.y() - start_pos.y()) * ratio
            self.toolbar.move(int(x), int(y))
            
            # Fade out
            opacity = 1.0 - ratio
            self.toolbar.setWindowOpacity(opacity)
        elif step > total_steps:
            self.toolbar.hide()
    
    def animate_toolbar_restore(self):
        """Animate toolbar restoration (system tray version)"""
        if self.toolbar and self.toolbar_last_pos:
            # Position at last position
            self.toolbar.move(self.toolbar_last_pos)
            self.toolbar.setWindowOpacity(0.0)
            self.toolbar.show()
            
            # Simple fade in animation
            for i in range(11):
                QTimer.singleShot(i * 30, lambda opacity=i/10.0: self.toolbar.setWindowOpacity(opacity))
    
    def animate_step_restore(self, start_pos, end_pos, step, total_steps):
        """Single step of restore animation"""
        if step <= total_steps and self.toolbar:
            # Calculate intermediate position
            ratio = step / total_steps
            x = start_pos.x() + (end_pos.x() - start_pos.x()) * ratio
            y = start_pos.y() + (end_pos.y() - start_pos.y()) * ratio
            self.toolbar.move(int(x), int(y))
            
            # Fade in
            opacity = ratio
            self.toolbar.setWindowOpacity(opacity)

    def set_mode(self, mode):
        # Track previous mode for auto-hide detection
        self.previous_mode = getattr(self, 'mode', None)
        self.mode = mode
        
        if mode != "text" and self.input_box:
            self.finish_text(self.input_box_pos)
        self.setWindowFlag(Qt.WindowTransparentForInput, mode == "mouse")
        self.setCursor(Qt.ArrowCursor if mode in ["mouse", "select"] else Qt.CrossCursor)
        if mode == "laser":
            self.setCursor(Qt.BlankCursor)
        self.hide()
        self.show()
        for m, btn in self.toolbar.btns.items():
            if btn.isCheckable() and m != 'fill':
                btn.setChecked(m == mode)
        # Ensure toolbar stays accessible after mode change
        self.toolbar.raise_()
        self.toolbar.activateWindow()
        
        # If toolbar was hidden and a tool was selected, hide it automatically
        if self.is_hidden and self.previous_mode != self.mode:
            QTimer.singleShot(300, self.hide_toolbar_modern)

    def open_color_picker(self):
        d = QColorDialog(self.current_color, self)
        d.setWindowFlags(Qt.WindowStaysOnTopHint)
        if d.exec_() == QColorDialog.Accepted:
            self.current_color = d.selectedColor()
            # Update the color picker button to reflect the new color
            if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'update_color_picker'):
                self.toolbar.update_color_picker()
            # Just update the color and refresh the display
            self.update()
    
    def toggle_board(self):
        """Toggle between transparent annotation and board mode (with configurable color)"""
        # Toggle between transparent and current board color
        if self.board_mode == "transparent":
            # Switch to preferred board color
            self.board_mode = getattr(self, 'preferred_board_color', 'white')
            # Set the background to the preferred board color
            if self.board_mode == "white":
                self.setStyleSheet("background-color: white;")
            elif self.board_mode == "black":
                self.setStyleSheet("background-color: black;")
            else:  # default to white
                self.board_mode = "white"
                self.setStyleSheet("background-color: white;")
            # Remove translucent background for solid color
            self.setAttribute(Qt.WA_TranslucentBackground, False)
        else:
            # Switch back to transparent annotation mode
            self.board_mode = "transparent"
            # Transparent annotation mode
            self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            # Restore translucent background for transparency
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Keep the board button icon constant (don't change when clicked)
        if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'btns') and 'board' in self.toolbar.btns:
            board_btn = self.toolbar.btns['board']
            # Do not change the icon - let the icon manager handle the SVG icon consistently
        
        self.hide()
        self.show()
    
    def quick_toggle_board(self):
        """Quick toggle board without showing options (for keyboard shortcut)"""
        # If no preferred color is set, default to white
        if not hasattr(self, 'preferred_board_color'):
            self.preferred_board_color = 'white'
        self.toggle_board()
    
    def set_board_color(self, color):
        """Set the preferred board color (white or black)"""
        self.preferred_board_color = color
        # If currently in board mode, update the background color
        if self.board_mode != "transparent":
            if color == "white":
                self.setStyleSheet("background-color: white;")
            elif color == "black":
                self.setStyleSheet("background-color: black;")
            self.board_mode = color
            self.hide()
            self.show()
    
    def set_line_style(self, style):
        """Set the current line drawing style (solid, dashed, hand_drawn)"""
        self.current_line_style = style
        # Update current tool to use new line style
        # This will affect the next shape drawn
        
    def setup_global_shortcuts(self):
        """Setup global keyboard shortcuts that work even when app is in background"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Create global shortcuts with Ctrl+Alt combinations to avoid conflicts
        # Tool switching shortcuts
        self.shortcut_pencil = QShortcut(QKeySequence("Ctrl+Alt+P"), self)
        self.shortcut_pencil.activated.connect(lambda: self.set_mode("pencil"))
        
        self.shortcut_rect = QShortcut(QKeySequence("Ctrl+Alt+R"), self)
        self.shortcut_rect.activated.connect(lambda: self.set_mode("rect"))
        
        self.shortcut_ellipse = QShortcut(QKeySequence("Ctrl+Alt+E"), self)
        self.shortcut_ellipse.activated.connect(lambda: self.set_mode("ellipse"))
        
        self.shortcut_arrow = QShortcut(QKeySequence("Ctrl+Alt+A"), self)
        self.shortcut_arrow.activated.connect(lambda: self.set_mode("arrow"))
        
        self.shortcut_text = QShortcut(QKeySequence("Ctrl+Alt+T"), self)
        self.shortcut_text.activated.connect(lambda: self.set_mode("text"))
        
        self.shortcut_eraser = QShortcut(QKeySequence("Ctrl+Alt+X"), self)
        self.shortcut_eraser.activated.connect(lambda: self.set_mode("eraser"))
        
        self.shortcut_select = QShortcut(QKeySequence("Ctrl+Alt+V"), self)
        self.shortcut_select.activated.connect(lambda: self.set_mode("select"))
        
        self.shortcut_mouse = QShortcut(QKeySequence("Ctrl+Alt+M"), self)
        self.shortcut_mouse.activated.connect(lambda: self.set_mode("mouse"))
        
        # Hide/Unhide shortcut
        self.shortcut_toggle_visibility = QShortcut(QKeySequence("Ctrl+Alt+H"), self)
        self.shortcut_toggle_visibility.activated.connect(self.toggle_toolbar_visibility)
        
        # Board toggle shortcut
        self.shortcut_toggle_board = QShortcut(QKeySequence("Ctrl+Alt+B"), self)
        self.shortcut_toggle_board.activated.connect(self.quick_toggle_board)
        
        # Undo/Redo shortcuts
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Alt+Z"), self)
        self.shortcut_undo.activated.connect(self.undo)
        
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+Alt+Y"), self)
        self.shortcut_redo.activated.connect(self.redo)
        
        # Clear canvas shortcut
        self.shortcut_clear = QShortcut(QKeySequence("Ctrl+Alt+C"), self)
        self.shortcut_clear.activated.connect(self.clear_canvas)
        
        # Screenshot shortcuts
        self.shortcut_full_screenshot = QShortcut(QKeySequence("Ctrl+Alt+S"), self)
        self.shortcut_full_screenshot.activated.connect(self.capture_full_screen_screenshot)
        
        self.shortcut_area_screenshot = QShortcut(QKeySequence("Ctrl+Alt+Shift+S"), self)
        self.shortcut_area_screenshot.activated.connect(self.capture_area_screenshot)
        
        self.shortcut_long_screenshot = QShortcut(QKeySequence("Ctrl+Alt+L"), self)
        self.shortcut_long_screenshot.activated.connect(self.capture_scrolling_screenshot)
        
        self.shortcut_scrolling_screenshot = QShortcut(QKeySequence("Ctrl+Alt+Shift+L"), self)
        self.shortcut_scrolling_screenshot.activated.connect(self.capture_scrolling_screenshot)
        
        # Recording shortcuts
        self.shortcut_record_toggle = QShortcut(QKeySequence("Ctrl+Alt+Rec"), self)
        self.shortcut_record_toggle.activated.connect(self.toggle_recording)
        
        self.shortcut_record_area = QShortcut(QKeySequence("Ctrl+Alt+Shift+Rec"), self)
        self.shortcut_record_area.activated.connect(self.record_area)
        
        # Fill mode toggle
        self.shortcut_toggle_fill = QShortcut(QKeySequence("Ctrl+Alt+F"), self)
        self.shortcut_toggle_fill.activated.connect(self.toggle_fill_color)
        
        # Make shortcuts work even when window is not focused
        self.setAttribute(Qt.WA_KeyCompression, False)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        
        # Ensure the window can receive keyboard events
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Set focus policy to ensure keyboard events are received
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
        # Ensure window stays responsive
        self.raise_()
        self.activateWindow()
        
        # Timer to periodically ensure window focus
        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.ensure_window_focus)
        self.focus_timer.start(1000)  # Check every second
    
    def ensure_window_focus(self):
        """Ensure the window can receive keyboard shortcuts"""
        if not self.isActiveWindow():
            self.raise_()
            self.activateWindow()
    
    def set_text_size(self, size):
        """Set the current text size"""
        self.current_text_size = size
        self.size_value_label.setText(str(size))
        # Update the input box if it exists
        if self.input_box:
            self.input_box.setStyleSheet(f"border: 1px dashed #6965db; background: white; color: {self.current_color.name()}; font-size: {size}px; padding: 5px;")
    
    def toggle_text_bold(self):
        """Toggle bold text formatting"""
        self.current_text_bold = self.bold_btn.isChecked()
        # Update the input box if it exists
        if self.input_box:
            font_weight = "bold" if self.current_text_bold else "normal"
            font_style = "italic" if self.current_text_italic else "normal"
            self.input_box.setStyleSheet(f"border: 1px dashed #6965db; background: white; color: {self.current_color.name()}; font-size: {self.current_text_size}px; font-weight: {font_weight}; font-style: {font_style}; padding: 5px;")
    
    def toggle_text_italic(self):
        """Toggle italic text formatting"""
        self.current_text_italic = self.italic_btn.isChecked()
        # Update the input box if it exists
        if self.input_box:
            font_weight = "bold" if self.current_text_bold else "normal"
            font_style = "italic" if self.current_text_italic else "normal"
            self.input_box.setStyleSheet(f"border: 1px dashed #6965db; background: white; color: {self.current_color.name()}; font-size: {self.current_text_size}px; font-weight: {font_weight}; font-style: {font_style}; padding: 5px;")
    
    def toggle_fill_color(self):
        """Toggle fill color for shapes"""
        self.enable_fill = not self.enable_fill
        # Update the fill button appearance if it exists
        if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'btns') and 'fill' in self.toolbar.btns:
            fill_btn = self.toolbar.btns['fill']
            if self.enable_fill:
                fill_btn.setStyleSheet(fill_btn.styleSheet() + " background-color: lightblue;")
            else:
                # Reset to default style
                fill_btn.setStyleSheet("")
    
    def capture_full_screen_screenshot(self):
        """Capture full screen screenshot with enhanced controls"""
        try:
            from src.smart_capture import SmartScrollCapture
            
            # Initialize smart capture
            self.smart_capture = SmartScrollCapture(self)
            
            # Create capture controls if not exists
            if not hasattr(self, 'capture_controls') or self.capture_controls is None:
                from src.capture_controls import CaptureControlsWindow
                self.capture_controls = CaptureControlsWindow(self)
                self.capture_controls.show()
                self.capture_controls.raise_()
                self.capture_controls.activateWindow()
            
            # Start capture
            self.capture_controls.start_capture("fullscreen")
            
            # Perform capture
            filepath = self.smart_capture.capture_full_screenshot()
            
            # Update controls
            self.capture_controls.add_captured_section({"type": "full", "path": filepath})
            
            print(f"✅ Full screen screenshot saved: {filepath}")
            self.capture_controls.status_indicator.setText("✓ COMPLETE")
            
        except Exception as e:
            error_msg = f"Full screen capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            if hasattr(self, 'capture_controls'):
                self.capture_controls.update_status("✗ ERROR", "#ff6b6b")
            QMessageBox.critical(self, "Capture Error", error_msg)
        
    def capture_area_screenshot(self):
        """Capture area screenshot with selection"""
        try:
            from src.smart_capture import SmartScrollCapture
            
            # Initialize smart capture
            self.smart_capture = SmartScrollCapture(self)
            
            # Create capture controls
            if not hasattr(self, 'capture_controls') or self.capture_controls is None:
                from src.capture_controls import CaptureControlsWindow
                self.capture_controls = CaptureControlsWindow(self)
                self.capture_controls.show()
                self.capture_controls.raise_()
                self.capture_controls.activateWindow()
            
            # Start capture
            self.capture_controls.start_capture("area")
            
            # For area capture, we'd need area selection logic
            # This is a simplified version
            filepath = self.smart_capture.capture_area_screenshot()
            
            # Update controls
            self.capture_controls.add_captured_section({"type": "area", "path": filepath})
            
            print(f"✅ Area screenshot saved: {filepath}")
            self.capture_controls.status_indicator.setText("✓ COMPLETE")
            
        except Exception as e:
            error_msg = f"Area capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            if hasattr(self, 'capture_controls'):
                self.capture_controls.update_status("✗ ERROR", "#ff6b6b")
            QMessageBox.critical(self, "Capture Error", error_msg)
        
    def capture_scrolling_screenshot(self):
        """Enhanced scrolling screenshot with interactive controls"""
        try:
            # Import enhanced components
            from src.window_selector import WindowSelector
            from src.interactive_capture import InteractiveCaptureControls
            from src.auto_scroller import EnhancedAutoScroller
            
            # Create window selector
            self.window_selector = WindowSelector()
            self.window_selector.window_selected.connect(self.on_window_selected_for_scrolling)
            self.window_selector.selection_cancelled.connect(self.on_selection_cancelled)
            self.window_selector.show()
            self.window_selector.raise_()
            self.window_selector.activateWindow()
            
            print("🎯 Window selection mode activated for scrolling capture")
            
        except Exception as e:
            error_msg = f"Scrolling capture setup failed: {str(e)}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Capture Error", error_msg)
            
    def on_window_selected_for_scrolling(self, area):
        """Handle window selection for scrolling capture"""
        try:
            from src.interactive_capture import InteractiveCaptureControls
            from src.auto_scroller import EnhancedAutoScroller
            
            # Create interactive capture controls
            self.interactive_controls = InteractiveCaptureControls()
            self.interactive_controls.show()
            self.interactive_controls.raise_()
            self.interactive_controls.activateWindow()
            
            # Create auto scroller
            self.auto_scroller = EnhancedAutoScroller()
            
            # Connect signals
            self.interactive_controls.start_capture.connect(self.start_interactive_scrolling)
            self.interactive_controls.pause_capture.connect(self.auto_scroller.pause_capture)
            self.interactive_controls.resume_capture.connect(self.auto_scroller.resume_capture)
            self.interactive_controls.stop_capture.connect(self.auto_scroller.stop_capture)
            self.interactive_controls.save_capture.connect(self.save_current_capture)
            self.interactive_controls.cancel_capture.connect(self.cancel_interactive_capture)
            self.interactive_controls.scroll_speed_changed.connect(self.auto_scroller.set_scroll_speed)
            
            self.auto_scroller.scroll_progress.connect(
                lambda current, total: self.interactive_controls.update_progress(current)
            )
            self.auto_scroller.capture_completed.connect(self.on_capture_completed)
            self.auto_scroller.capture_error.connect(self.on_capture_error)
            
            # Set the capture area
            self.auto_scroller.set_capture_area(area)
            
            print(f"✅ Interactive scrolling capture ready for area: {area}")
            
        except Exception as e:
            error_msg = f"Interactive capture setup failed: {str(e)}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Capture Error", error_msg)
            
    def start_interactive_scrolling(self, mode, area):
        """Start the interactive scrolling capture"""
        try:
            if hasattr(self, 'auto_scroller'):
                self.auto_scroller.start_capture(area)
                print("🔄 Interactive scrolling capture started")
        except Exception as e:
            error_msg = f"Failed to start scrolling capture: {str(e)}"
            print(f"❌ {error_msg}")
            self.on_capture_error(error_msg)
            
    def save_current_capture(self):
        """Save the current capture state"""
        try:
            if hasattr(self, 'auto_scroller'):
                info = self.auto_scroller.get_capture_info()
                print(f"💾 Capture saved - Sections: {info['sections_captured']}, Position: {info['scroll_position']}")
                # The auto scroller handles the actual saving
        except Exception as e:
            print(f"Save error: {e}")
            
    def cancel_interactive_capture(self):
        """Cancel the interactive capture"""
        try:
            if hasattr(self, 'auto_scroller'):
                self.auto_scroller.stop_capture()
            if hasattr(self, 'interactive_controls'):
                self.interactive_controls.reset_controls()
                self.interactive_controls.close()
            print("⏹ Interactive capture cancelled")
        except Exception as e:
            print(f"Cancel error: {e}")
            
    def on_selection_cancelled(self):
        """Handle window selection cancellation"""
        print("❌ Window selection cancelled")
            
    def capture_code_editor_screenshot(self):
        """Capture code editor with smart scrolling"""
        try:
            # Use the enhanced scrolling capture for code editors
            self.capture_scrolling_screenshot()
            print("💻 Code editor capture mode activated")
            
        except Exception as e:
            error_msg = f"Code editor capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Capture Error", error_msg)
            
    def capture_window_screenshot(self):
        """Capture specific window with selection"""
        try:
            from src.window_selector import WindowSelector
            
            # Create window selector
            self.window_selector = WindowSelector()
            self.window_selector.window_selected.connect(self.on_window_selected_for_capture)
            self.window_selector.selection_cancelled.connect(self.on_selection_cancelled)
            self.window_selector.show()
            self.window_selector.raise_()
            self.window_selector.activateWindow()
            
            print("🎯 Window selection mode activated")
            
        except Exception as e:
            error_msg = f"Window capture setup failed: {str(e)}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Capture Error", error_msg)
            
    def on_window_selected_for_capture(self, area):
        """Handle window selection for regular capture"""
        try:
            from src.smart_capture import SmartScrollCapture
            
            # Initialize smart capture
            self.smart_capture = SmartScrollCapture(self)
            
            # Create capture controls
            if not hasattr(self, 'capture_controls') or self.capture_controls is None:
                from src.capture_controls import CaptureControlsWindow
                self.capture_controls = CaptureControlsWindow(self)
                self.capture_controls.show()
                self.capture_controls.raise_()
                self.capture_controls.activateWindow()
            
            # Start capture
            self.capture_controls.start_capture("window")
            
            # Capture the selected window area
            filepath = self.smart_capture.capture_area_screenshot(area)
            
            # Update controls
            self.capture_controls.add_captured_section({"type": "window", "path": filepath})
            
            print(f"✅ Window screenshot saved: {filepath}")
            self.capture_controls.status_indicator.setText("✓ COMPLETE")
            
        except Exception as e:
            error_msg = f"Window capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            if hasattr(self, 'capture_controls'):
                self.capture_controls.update_status("✗ ERROR", "#ff6b6b")
            QMessageBox.critical(self, "Capture Error", error_msg)
            
    def on_capture_completed(self, filepaths):
        """Handle capture completion"""
        if hasattr(self, 'capture_controls'):
            self.capture_controls.update_status("✓ COMPLETE", "#6bff8c")
            self.capture_controls.capture_timer.stop()
            
        # Show completion message
        files_text = "\n".join(filepaths)
        QMessageBox.information(self, "Capture Complete", 
                              f"Capture completed successfully!\n\nFiles saved:\n{files_text}")
        
        print(f"✅ Capture completed. Files: {filepaths}")
        
    def on_capture_error(self, error_msg):
        """Handle capture error"""
        if hasattr(self, 'capture_controls'):
            self.capture_controls.update_status("✗ ERROR", "#ff6b6b")
            self.capture_controls.capture_timer.stop()
            
        QMessageBox.critical(self, "Capture Error", error_msg)
        print(f"❌ Capture error: {error_msg}")
        
    def toggle_recording(self):
        """Toggle screen recording on/off"""
        print("Recording toggled")
        # Implementation would go here
        
    def record_area(self):
        """Record specific area"""
        print("Area recording started")
        # Implementation would go here
    
    def create_sidebar(self):
        """Create left sidebar for board options like Excalidraw"""
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
        from PyQt5.QtCore import Qt
        
        # Create sidebar widget
        self.sidebar = QWidget(self)
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                              stop: 0 #ffffff, 
                                              stop: 1 #f8f9fa);
                border-radius: 16px;
                margin: 8px 8px 8px 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Board Settings")
        header.setStyleSheet("font-size: 18px; font-weight: 600; color: #2d2d2d; padding-bottom: 8px;")
        layout.addWidget(header)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color: #e9ecef; margin: 10px 0px;")
        layout.addWidget(sep1)
        
        # Canvas color options
        color_label = QLabel("Canvas Color:")
        color_label.setStyleSheet("font-weight: 600; margin-top: 10px; font-size: 14px; color: #3a3a3a;")
        layout.addWidget(color_label)
        
        white_btn = QPushButton("⬜ White")
        white_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #e0e0e0;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
            }
        """)
        white_btn.clicked.connect(lambda: self.set_board_color("white"))
        layout.addWidget(white_btn)
        
        black_btn = QPushButton("⬛ Black")
        black_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #404040;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #505050;
            }
        """)
        black_btn.clicked.connect(lambda: self.set_board_color("black"))
        layout.addWidget(black_btn)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #e9ecef; margin: 10px 0px;")
        layout.addWidget(sep2)
        
        # Fill options
        fill_label = QLabel("Shape Fill:")
        fill_label.setStyleSheet("font-weight: 600; margin-top: 10px; font-size: 14px; color: #3a3a3a;")
        layout.addWidget(fill_label)
        
        self.fill_toggle_btn = QPushButton("☐ Enable Fill" if not self.enable_fill else "☑ Disable Fill")
        self.fill_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
            }
        """)
        
        def toggle_fill():
            self.toggle_fill_color()
            self.fill_toggle_btn.setText("☐ Enable Fill" if not self.enable_fill else "☑ Disable Fill")
        
        self.fill_toggle_btn.clicked.connect(toggle_fill)
        layout.addWidget(self.fill_toggle_btn)
        
        # Separator
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("color: #e9ecef; margin: 10px 0px;")
        layout.addWidget(sep3)
        
        # Line style options
        line_style_label = QLabel("Line Style:")
        line_style_label.setStyleSheet("font-weight: 600; margin-top: 10px; font-size: 14px; color: #3a3a3a;")
        layout.addWidget(line_style_label)
        
        # Line style buttons
        solid_line_btn = QPushButton("— Solid")
        solid_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
            }
        """)
        solid_line_btn.clicked.connect(lambda: self.set_line_style("solid"))
        layout.addWidget(solid_line_btn)
        
        dashed_line_btn = QPushButton("- - Dashed")
        dashed_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
            }
        """)
        dashed_line_btn.clicked.connect(lambda: self.set_line_style("dashed"))
        layout.addWidget(dashed_line_btn)
        
        hand_drawn_line_btn = QPushButton("~ ~ Hand-drawn")
        hand_drawn_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
            }
        """)
        hand_drawn_line_btn.clicked.connect(lambda: self.set_line_style("hand_drawn"))
        layout.addWidget(hand_drawn_line_btn)
        
        # Separator
        sep4 = QFrame()
        sep4.setFrameShape(QFrame.HLine)
        sep4.setStyleSheet("color: #e9ecef; margin: 10px 0px;")
        layout.addWidget(sep4)
        
        # Additional drawing options
        drawing_options_label = QLabel("Drawing Options:")
        drawing_options_label.setStyleSheet("font-weight: 600; margin-top: 10px; font-size: 14px; color: #3a3a3a;")
        layout.addWidget(drawing_options_label)
        
        # Board toggle button
        board_toggle_btn = QPushButton("📊 Toggle Board")
        board_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
            }
        """)
        board_toggle_btn.clicked.connect(self.toggle_board)
        layout.addWidget(board_toggle_btn)
        
        # Separator
        sep5 = QFrame()
        sep5.setFrameShape(QFrame.HLine)
        sep5.setStyleSheet("color: #e9ecef; margin: 10px 0px;")
        layout.addWidget(sep5)
        
        # Text formatting options
        text_label = QLabel("Text Options:")
        text_label.setStyleSheet("font-weight: 600; margin-top: 10px; font-size: 14px; color: #3a3a3a;")
        layout.addWidget(text_label)
        
        # Text size slider
        size_layout = QHBoxLayout()
        size_label = QLabel("Size:")
        size_label.setStyleSheet("font-size: 12px; color: #555;")
        size_layout.addWidget(size_label)
        
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 72)
        self.size_slider.setValue(22)
        self.size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6965db;
                border: 1px solid #5c58c8;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
        """)
        self.size_slider.valueChanged.connect(self.set_text_size)
        size_layout.addWidget(self.size_slider)
        
        self.size_value_label = QLabel("22")
        self.size_value_label.setStyleSheet("font-size: 12px; color: #555; min-width: 30px;")
        size_layout.addWidget(self.size_value_label)
        
        layout.addLayout(size_layout)
        
        # Text style buttons
        style_layout = QHBoxLayout()
        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 5px 10px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #6965db;
                color: white;
                border: 1px solid #5c58c8;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.bold_btn.clicked.connect(self.toggle_text_bold)
        style_layout.addWidget(self.bold_btn)
        
        self.italic_btn = QPushButton("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 5px 10px;
                font-style: italic;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #6965db;
                color: white;
                border: 1px solid #5c58c8;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.italic_btn.clicked.connect(self.toggle_text_italic)
        style_layout.addWidget(self.italic_btn)
        
        layout.addLayout(style_layout)
        
        # Separator
        sep6 = QFrame()
        sep6.setFrameShape(QFrame.HLine)
        sep6.setStyleSheet("color: #e9ecef; margin: 10px 0px;")
        layout.addWidget(sep6)
        
        # Keyboard Shortcuts
        shortcuts_label = QLabel("Global Keyboard Shortcuts:")
        shortcuts_label.setStyleSheet("font-weight: 600; margin-top: 10px; font-size: 14px; color: #3a3a3a;")
        layout.addWidget(shortcuts_label)
        
        # Create shortcut info labels
        shortcuts_info = [
            ("Ctrl+Alt+P", "Pencil Tool"),
            ("Ctrl+Alt+R", "Rectangle Tool"),
            ("Ctrl+Alt+E", "Ellipse Tool"),
            ("Ctrl+Alt+A", "Arrow Tool"),
            ("Ctrl+Alt+T", "Text Tool"),
            ("Ctrl+Alt+X", "Eraser Tool"),
            ("Ctrl+Alt+V", "Select Tool"),
            ("Ctrl+Alt+M", "Mouse Tool"),
            ("Ctrl+Alt+H", "Hide/Show Toolbar"),
            ("Ctrl+Alt+B", "Toggle Board"),
            ("Ctrl+Alt+Z", "Undo"),
            ("Ctrl+Alt+Y", "Redo"),
            ("Ctrl+Alt+C", "Clear Canvas"),
            ("Ctrl+Alt+S", "Full Screen Screenshot"),
            ("Ctrl+Alt+Shift+S", "Area Screenshot"),
            ("Ctrl+Alt+L", "Long Screenshot"),
            ("Ctrl+Alt+Shift+L", "Scrolling Screenshot"),
            ("Ctrl+Alt+Rec", "Start/Stop Recording"),
            ("Ctrl+Alt+Shift+Rec", "Record Area"),
            ("Ctrl+Alt+F", "Toggle Fill Mode")
        ]
        
        for key, action in shortcuts_info:
            shortcut_layout = QHBoxLayout()
            key_label = QLabel(key)
            key_label.setStyleSheet("font-weight: bold; color: #6965db; min-width: 80px;")
            shortcut_layout.addWidget(key_label)
            
            action_label = QLabel(f"→ {action}")
            action_label.setStyleSheet("font-size: 12px; color: #555;")
            shortcut_layout.addWidget(action_label)
            
            layout.addLayout(shortcut_layout)
        
        # Separator
        sep7 = QFrame()
        sep7.setFrameShape(QFrame.HLine)
        sep7.setStyleSheet("color: #e9ecef; margin: 10px 0px;")
        layout.addWidget(sep7)
        
        # Reset button
        reset_btn = QPushButton("↺ Reset to Defaults")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: 1px solid #c82323;
                padding: 12px 16px;
                font-weight: bold;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
                border: 1px solid #b21f2d;
            }
        """)
        
        def reset_defaults():
            # Reset board to white (don't make it transparent)
            self.board_mode = "white"
            self.preferred_board_color = "white"
            self.setStyleSheet("background-color: white;")
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            # Reset fill mode
            self.enable_fill = False
            # Update UI
            if hasattr(self, 'fill_toggle_btn'):
                self.fill_toggle_btn.setText("☐ Enable Fill")
            if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'btns') and 'board' in self.toolbar.btns:
                self.toolbar.btns['board'].setText("⬜")
            self.hide()
            self.show()
        
        reset_btn.clicked.connect(reset_defaults)
        layout.addWidget(reset_btn)
        
        # Spacer
        layout.addStretch()
        
        self.sidebar.setLayout(layout)
        
        # Position sidebar on left side with padding for rounded corners
        self.sidebar.move(8, 8)
        self.sidebar.resize(280, self.height() - 16)
        self.sidebar.show()
        
        return self.sidebar
    
    def toggle_sidebar(self):
        """Toggle the sidebar visibility"""
        if not hasattr(self, 'sidebar'):
            self.create_sidebar()
            self.sidebar.show()
        elif self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
    
    def show_board_options(self):
        """Show board options sidebar"""
        if not hasattr(self, 'sidebar'):
            self.create_sidebar()
        self.sidebar.show()
    
    def create_shapes_submenu(self):
        """Create shapes submenu for the more menu"""
        from PyQt5.QtWidgets import QMenu
        
        shapes_menu = QMenu("_shapes", self)
        
        # Add various shape options
        shapes_menu.addAction("🔺 Triangle").triggered.connect(lambda: self.set_mode("triangle"))
        shapes_menu.addAction("🔷 Hexagon").triggered.connect(lambda: self.set_mode("hexagon"))
        shapes_menu.addAction("🔶 Pentagon").triggered.connect(lambda: self.set_mode("pentagon"))
        shapes_menu.addAction("🔷 Octagon").triggered.connect(lambda: self.set_mode("octagon"))
        shapes_menu.addAction("🔷 Star").triggered.connect(lambda: self.set_mode("star"))
        shapes_menu.addAction("🔷 Arrow (Double)").triggered.connect(lambda: self.set_mode("double_arrow"))
        shapes_menu.addAction("🔷 Curved Arrow").triggered.connect(lambda: self.set_mode("curved_arrow"))
        shapes_menu.addAction("🔷 Cloud").triggered.connect(lambda: self.set_mode("cloud"))
        shapes_menu.addAction("🔷 Callout").triggered.connect(lambda: self.set_mode("callout"))
        shapes_menu.addAction("🔷 Speech Bubble").triggered.connect(lambda: self.set_mode("speech_bubble"))
        
        # Add new diagram and database shapes
        shapes_menu.addSeparator()
        shapes_menu.addAction("🔷 Database Table").triggered.connect(lambda: self.set_mode("db_table"))
        shapes_menu.addAction("🔷 Entity").triggered.connect(lambda: self.set_mode("entity"))
        shapes_menu.addAction("🔷 Relationship").triggered.connect(lambda: self.set_mode("relationship"))
        shapes_menu.addAction("🔷 Note").triggered.connect(lambda: self.set_mode("note"))
        shapes_menu.addAction("🔷 Component").triggered.connect(lambda: self.set_mode("component"))
        shapes_menu.addAction("🔷 Class").triggered.connect(lambda: self.set_mode("class"))
        shapes_menu.addAction("🔷 Use Case").triggered.connect(lambda: self.set_mode("use_case"))
        
        # Add connection lines
        shapes_menu.addSeparator()
        shapes_menu.addAction("🔗 Orthogonal Line").triggered.connect(lambda: self.set_mode("orthogonal_line"))
        shapes_menu.addAction("🔗 Curved Connection").triggered.connect(lambda: self.set_mode("curved_connection"))
        shapes_menu.addAction("🔗 Dashed Line").triggered.connect(lambda: self.set_mode("dashed_line"))
        shapes_menu.addAction("🔗 Elbow Connector").triggered.connect(lambda: self.set_mode("elbow_connector"))
        
        return shapes_menu
    
    # Methods for original toolbar compatibility
    def hide_toolbar_permanent_func(self):
        """Hide toolbar permanently and update system tray"""
        self.is_hidden = True
        self.toolbar_last_pos = self.toolbar.pos()
        self.toolbar.hide()
        # Update system tray menu
        self.update_tray_menu()
        print("📌 Toolbar hidden - system tray updated")
        
    def clear_canvas_func(self):
        """Clear all canvas drawings"""
        self.shapes = []
        self.laser_trails = []
        self.undo_stack = []
        self.redo_stack = []
        if self.input_box:
            self.input_box.deleteLater()
            self.input_box = None
        self.update()
    
    def toggle_text_bold(self):
        """Toggle bold formatting for selected text"""
        if self.selected_shape and self.selected_shape.mode == "text":
            self.selected_shape.font_bold = not self.selected_shape.font_bold
            self.save_state()
            self.update()
    
    def toggle_text_italic(self):
        """Toggle italic formatting for selected text"""
        if self.selected_shape and self.selected_shape.mode == "text":
            self.selected_shape.font_italic = not self.selected_shape.font_italic
            self.save_state()
            self.update()
    
    def increase_text_size(self):
        """Increase font size for selected text"""
        if self.selected_shape and self.selected_shape.mode == "text":
            self.selected_shape.font_size = min(100, self.selected_shape.font_size + 2)
            self.save_state()
            self.update()
    
    def decrease_text_size(self):
        """Decrease font size for selected text"""
        if self.selected_shape and self.selected_shape.mode == "text":
            self.selected_shape.font_size = max(8, self.selected_shape.font_size - 2)
            self.save_state()
            self.update()

    def open_text_input(self, pos):
        if self.input_box:
            self.finish_text(self.input_box_pos)
        self.input_box_pos = pos
        self.input_box = QLineEdit(self)
        font_weight = "bold" if self.current_text_bold else "normal"
        font_style = "italic" if self.current_text_italic else "normal"
        self.input_box.setStyleSheet(f"border: 1px dashed #6965db; background: white; color: {self.current_color.name()}; font-size: {self.current_text_size}px; font-weight: {font_weight}; font-style: {font_style}; padding: 5px;")
        self.input_box.move(int(pos.x()), int(pos.y()))
        self.input_box.show()
        self.input_box.setFocus()
        self.input_box.editingFinished.connect(lambda: self.finish_text(pos))

    def finish_text(self, pos):
        if self.input_box:
            txt = self.input_box.text()
            if txt.strip():
                # Create text shape with current font properties
                shape = TutorShape("text", pos, self.current_color, self.current_thickness, txt,
                                 font_size=self.current_text_size, font_bold=self.current_text_bold, font_italic=self.current_text_italic)
                self.shapes.append(shape)
                self.save_state()
            self.input_box.deleteLater()
            self.input_box = None
            self.update()
    
    def edit_text_shape(self, shape, pos):
        """Edit an existing text shape"""
        if self.input_box:
            self.input_box.deleteLater()
        
        self.input_box_pos = pos
        self.input_box = QLineEdit(self)
        self.input_box.setText(shape.text)
        self.input_box.setStyleSheet(f"border: 1px dashed #6965db; background: white; color: {self.current_color.name()}; font-size: {shape.font_size}px; padding: 5px;")
        self.input_box.move(int(pos.x()), int(pos.y()))
        self.input_box.show()
        self.input_box.selectAll()
        self.input_box.setFocus()
        
        def finish_editing():
            if self.input_box:
                new_text = self.input_box.text()
                if new_text.strip():
                    shape.text = new_text
                    self.save_state()
                self.input_box.deleteLater()
                self.input_box = None
                self.update()
        
        self.input_box.editingFinished.connect(finish_editing)

    def clear_canvas(self):
        self.shapes = []
        self.laser_trails = []
        self.undo_stack = []
        self.redo_stack = []
        if self.input_box:
            self.input_box.deleteLater()
            self.input_box = None
        self.update()

    def confirm_clear(self):
        reply = QMessageBox.question(self, 'Clear Canvas', 'Clear all drawings?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clear_canvas()

    def open_settings(self):
        """Open the settings dialog"""
        from src.settings import SettingsDialog
        dialog = SettingsDialog(self, self)
        if dialog.exec_():
            self.save_config()
            # Update UI if needed based on settings changes
            if hasattr(self, 'toolbar'):
                # Apply theme to refresh all icons
                self.toolbar.apply_theme(self.current_theme)
                # Update tooltips to reflect new shortcuts
                self.toolbar.update_tooltips()

    def save_state(self):
        self.undo_stack.append([TutorShape(s.mode, s.points[0], s.color.name(), s.thickness, s.text, 
                                         s.fill_color.name() if s.fill_color else None,
                                         s.font_size if hasattr(s, 'font_size') else 22,
                                         s.font_bold if hasattr(s, 'font_bold') else False,
                                         s.font_italic if hasattr(s, 'font_italic') else False) for s in self.shapes])
        self.redo_stack = []
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append([TutorShape(s.mode, s.points[0], s.color.name(), s.thickness, s.text, 
                                             s.fill_color.name() if s.fill_color else None,
                                             s.font_size if hasattr(s, 'font_size') else 22,
                                             s.font_bold if hasattr(s, 'font_bold') else False,
                                             s.font_italic if hasattr(s, 'font_italic') else False) for s in self.shapes])
            self.shapes = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append([TutorShape(s.mode, s.points[0], s.color.name(), s.thickness, s.text, 
                                             s.fill_color.name() if s.fill_color else None,
                                             s.font_size if hasattr(s, 'font_size') else 22,
                                             s.font_bold if hasattr(s, 'font_bold') else False,
                                             s.font_italic if hasattr(s, 'font_italic') else False) for s in self.shapes])
            self.shapes = self.redo_stack.pop()
            self.update()

    def update_canvas(self):
        if self.is_hidden and self.toolbar.isVisible() and not self.toolbar.underMouse() and not self.hide_handle.underMouse():
            self.toolbar.hide()
        
        # Ensure toolbar stays accessible
        if not self.is_hidden and self.toolbar.isVisible():
            self.toolbar.raise_()
        
        now = time.monotonic()
        for trail in self.laser_trails[:]:
            trail.cleanup_old_points(now)
            if trail.is_empty():
                self.laser_trails.remove(trail)
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        
        # Apply zoom transformation if active
        if self.is_zoom_active and self.zoom_factor > 1.0:
            painter.translate(self.zoom_center)
            painter.scale(self.zoom_factor, self.zoom_factor)
            painter.translate(-self.zoom_center)
        
        for s in self.shapes + ([self.current_shape] if self.current_shape else []):
            if not s:
                continue
            w = self.current_thickness if not hasattr(s, 'thickness') else s.thickness
            w = w + 2 if s.is_selected else w
            
            # Determine line style based on current setting
            line_style = getattr(self, 'current_line_style', 'solid')
            
            if line_style == 'dashed':
                pen = QPen(s.color, w, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin)
            elif line_style == 'hand_drawn':
                # For hand-drawn effect, use a custom dash pattern
                pen = QPen(s.color, w, Qt.CustomDashLine, Qt.RoundCap, Qt.RoundJoin)
                # Create a pattern that mimics hand-drawn style
                dash_pattern = [4, 4]  # Customize this for different hand-drawn effects
                pen.setDashPattern(dash_pattern)
            else:  # solid
                pen = QPen(s.color, w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            
            painter.setPen(pen)
            
            if s.fill_color:
                painter.setBrush(QBrush(s.fill_color))
            else:
                painter.setBrush(Qt.NoBrush)
            
            if s.mode == "pencil":
                path = QPainterPath()
                if len(s.points) > 1:
                    path.moveTo(s.points[0])
                    for i in range(1, len(s.points)):
                        path.quadTo(s.points[i-1], (s.points[i-1] + s.points[i]) / 2)
                    path.lineTo(s.points[-1])
                    painter.drawPath(path)
            elif s.mode == "highlighter":
                # Text-aware highlighter
                if hasattr(s, 'text_bounds') and s.text_bounds:
                    # Highlight existing text - align with text bounds
                    highlight_color = QColor(255, 255, 0, 128)  # Yellow with 50% transparency
                    painter.setPen(QPen(highlight_color, max(8, w * 2), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.setBrush(QBrush(highlight_color))
                    # Draw highlight rectangle that matches text bounds
                    painter.drawRect(s.text_bounds)
                else:
                    # Free-form highlighter drawing
                    highlight_color = QColor(255, 255, 0, 128)  # Yellow with 50% transparency
                    painter.setPen(QPen(highlight_color, max(8, w * 2), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    path = QPainterPath()
                    if len(s.points) > 1:
                        path.moveTo(s.points[0])
                        for i in range(1, len(s.points)):
                            path.quadTo(s.points[i-1], (s.points[i-1] + s.points[i]) / 2)
                        path.lineTo(s.points[-1])
                        painter.drawPath(path)
            elif s.mode == "text":
                # Use the shape's font properties
                font_weight = QFont.Bold if s.font_bold else QFont.Normal
                font_style = QFont.StyleItalic if s.font_italic else QFont.StyleNormal
                font = QFont("Segoe Print", s.font_size, font_weight)
                font.setStyle(font_style)
                painter.setFont(font)
                painter.drawText(s.points[0], s.text)
            elif s.mode == "rect":
                painter.drawRect(QRectF(s.points[0], s.end_pos).normalized())
            elif s.mode == "ellipse":
                painter.drawEllipse(QRectF(s.points[0], s.end_pos).normalized())
            elif s.mode == "circle":
                radius = math.hypot(s.end_pos.x() - s.points[0].x(), s.end_pos.y() - s.points[0].y())
                painter.drawEllipse(s.points[0], radius, radius)
            elif s.mode == "diamond":
                r = QRectF(s.points[0], s.end_pos).normalized()
                diamond_points = [QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()), 
                                   QPointF(r.center().x(), r.bottom()), QPointF(r.left(), r.center().y())]
                diamond_polygon = QPolygonF(diamond_points)
                painter.drawPolygon(diamond_polygon)
            elif s.mode == "arrow":
                # Draw arrow shape
                start = s.points[0]
                end = s.end_pos
                
                # Draw the line
                painter.drawLine(start, end)
                
                # Calculate arrowhead
                dx = end.x() - start.x()
                dy = end.y() - start.y()
                length = math.sqrt(dx*dx + dy*dy)
                
                if length > 0:
                    # Normalize direction vector
                    unit_dx = dx / length
                    unit_dy = dy / length
                    
                    # Arrowhead size
                    arrow_size = 10 + w  # Make arrowhead proportional to line width
                    
                    # Calculate arrowhead points
                    arrow_angle = math.pi / 6  # 30 degrees
                    cos_angle = math.cos(arrow_angle)
                    sin_angle = math.sin(arrow_angle)
                    
                    # Perpendicular vectors for arrowhead
                    perp_dx = -unit_dy
                    perp_dy = unit_dx
                    
                    # Arrowhead tip at the end point
                    tip = end
                    
                    # Arrowhead base points
                    left_base_x = end.x() - arrow_size * (unit_dx * cos_angle + perp_dx * sin_angle)
                    left_base_y = end.y() - arrow_size * (unit_dy * cos_angle + perp_dy * sin_angle)
                    right_base_x = end.x() - arrow_size * (unit_dx * cos_angle - perp_dx * sin_angle)
                    right_base_y = end.y() - arrow_size * (unit_dy * cos_angle - perp_dy * sin_angle)
                    
                    left_point = QPointF(left_base_x, left_base_y)
                    right_point = QPointF(right_base_x, right_base_y)
                    
                    # Draw arrowhead
                    polygon = QPolygonF([tip, left_point, right_point])
                    painter.drawPolygon(polygon)
            elif s.mode == "triangle":
                # Draw triangle shape
                r = QRectF(s.points[0], s.end_pos).normalized()
                triangle_points = [QPointF(r.center().x(), r.top()), 
                                   QPointF(r.right(), r.bottom()), 
                                   QPointF(r.left(), r.bottom())]
                triangle_polygon = QPolygonF(triangle_points)
                painter.drawPolygon(triangle_polygon)
            elif s.mode == "hexagon":
                # Draw hexagon shape
                r = QRectF(s.points[0], s.end_pos).normalized()
                center = r.center()
                width = r.width()
                height = r.height()
                points = []
                for i in range(6):
                    angle = 2 * math.pi * i / 6
                    x = center.x() + (width/2) * math.cos(angle)
                    y = center.y() + (height/2) * math.sin(angle)
                    points.append(QPointF(x, y))
                hexagon_polygon = QPolygonF(points)
                painter.drawPolygon(hexagon_polygon)
            elif s.mode == "pentagon":
                # Draw pentagon shape
                r = QRectF(s.points[0], s.end_pos).normalized()
                center = r.center()
                width = r.width()
                height = r.height()
                points = []
                for i in range(5):
                    angle = 2 * math.pi * i / 5 - math.pi/2  # Start from top
                    x = center.x() + (width/2) * math.cos(angle)
                    y = center.y() + (height/2) * math.sin(angle)
                    points.append(QPointF(x, y))
                pentagon_polygon = QPolygonF(points)
                painter.drawPolygon(pentagon_polygon)
            elif s.mode == "octagon":
                # Draw octagon shape
                r = QRectF(s.points[0], s.end_pos).normalized()
                center = r.center()
                width = r.width()
                height = r.height()
                points = []
                for i in range(8):
                    angle = 2 * math.pi * i / 8
                    x = center.x() + (width/2) * math.cos(angle)
                    y = center.y() + (height/2) * math.sin(angle)
                    points.append(QPointF(x, y))
                octagon_polygon = QPolygonF(points)
                painter.drawPolygon(octagon_polygon)
            elif s.mode == "star":
                # Draw star shape (5-pointed)
                r = QRectF(s.points[0], s.end_pos).normalized()
                center = r.center()
                outer_radius = min(r.width(), r.height()) / 2
                inner_radius = outer_radius * 0.4
                points = []
                for i in range(10):
                    angle = math.pi * i / 5 - math.pi/2
                    radius = outer_radius if i % 2 == 0 else inner_radius
                    x = center.x() + radius * math.cos(angle)
                    y = center.y() + radius * math.sin(angle)
                    points.append(QPointF(x, y))
                star_polygon = QPolygonF(points)
                painter.drawPolygon(star_polygon)
            elif s.mode == "double_arrow":
                # Draw double arrow (arrow at both ends)
                start = s.points[0]
                end = s.end_pos
                
                # Draw the line
                painter.drawLine(start, end)
                
                # Calculate arrowheads for both ends
                dx = end.x() - start.x()
                dy = end.y() - start.y()
                length = math.sqrt(dx*dx + dy*dy)
                
                if length > 0:
                    unit_dx = dx / length
                    unit_dy = dy / length
                    arrow_size = 10 + w
                    arrow_angle = math.pi / 6
                    cos_angle = math.cos(arrow_angle)
                    sin_angle = math.sin(arrow_angle)
                    perp_dx = -unit_dy
                    perp_dy = unit_dx
                    
                    # Arrowhead at end point
                    tip_end = end
                    left_end_x = end.x() - arrow_size * (unit_dx * cos_angle + perp_dx * sin_angle)
                    left_end_y = end.y() - arrow_size * (unit_dy * cos_angle + perp_dx * sin_angle)
                    right_end_x = end.x() - arrow_size * (unit_dx * cos_angle - perp_dx * sin_angle)
                    right_end_y = end.y() - arrow_size * (unit_dy * cos_angle - perp_dy * sin_angle)
                    
                    # Arrowhead at start point
                    tip_start = start
                    left_start_x = start.x() + arrow_size * (unit_dx * cos_angle + perp_dx * sin_angle)
                    left_start_y = start.y() + arrow_size * (unit_dy * cos_angle + perp_dy * sin_angle)
                    right_start_x = start.x() + arrow_size * (unit_dx * cos_angle - perp_dx * sin_angle)
                    right_start_y = start.y() + arrow_size * (unit_dy * cos_angle - perp_dy * sin_angle)
                    
                    # Draw both arrowheads
                    end_arrow_polygon = QPolygonF([tip_end, QPointF(left_end_x, left_end_y), QPointF(right_end_x, right_end_y)])
                    start_arrow_polygon = QPolygonF([tip_start, QPointF(left_start_x, left_start_y), QPointF(right_start_x, right_start_y)])
                    painter.drawPolygon(end_arrow_polygon)
                    painter.drawPolygon(start_arrow_polygon)
            elif s.mode == "curved_arrow":
                # Draw curved arrow
                start = s.points[0]
                end = s.end_pos
                
                # Create a curved path
                path = QPainterPath()
                path.moveTo(start)
                
                # Control point for the curve
                ctrl_x = (start.x() + end.x()) / 2
                ctrl_y = min(start.y(), end.y()) - 50  # Curve upward
                path.quadTo(QPointF(ctrl_x, ctrl_y), end)
                
                painter.drawPath(path)
                
                # Draw arrowhead at the end
                # Simple arrowhead for curved arrow
                painter.drawLine(end.x() - 10, end.y() - 5, end.x(), end.y())
                painter.drawLine(end.x() - 10, end.y() + 5, end.x(), end.y())
            elif s.mode == "cloud":
                # Draw cloud shape
                r = QRectF(s.points[0], s.end_pos).normalized()
                painter.drawEllipse(int(r.left()), int(r.top()), int(r.width()/3), int(r.height()/2))
                painter.drawEllipse(int(r.left() + r.width()/3), int(r.top() - r.height()/4), int(r.width()/3), int(r.height()/2))
                painter.drawEllipse(int(r.left() + 2*r.width()/3), int(r.top()), int(r.width()/3), int(r.height()/2))
                painter.drawEllipse(int(r.left() + r.width()/6), int(r.top() + r.height()/4), int(r.width()/2), int(r.height()/2))
            elif s.mode == "callout":
                # Draw callout shape (rectangle with tail)
                r = QRectF(s.points[0], s.end_pos).normalized()
                # Draw main rectangle
                painter.drawRect(r)
                # Draw tail
                tail_start = QPointF(r.center().x(), r.bottom())
                tail_end = QPointF(r.center().x() + 20, r.bottom() + 20)
                painter.drawLine(tail_start, tail_end)
            elif s.mode == "speech_bubble":
                # Draw speech bubble
                r = QRectF(s.points[0], s.end_pos).normalized()
                # Draw main ellipse
                painter.drawEllipse(r)
                # Draw tail
                tail_start = QPointF(r.right() - 20, r.bottom() - 10)
                tail_end = QPointF(r.right() + 10, r.bottom() + 10)
                painter.drawLine(tail_start, tail_end)
            elif s.mode == "db_table":
                # Draw database table (rectangle with header)
                r = QRectF(s.points[0], s.end_pos).normalized()
                # Draw main rectangle
                painter.drawRect(r)
                # Draw header separator
                header_height = r.height() * 0.25
                painter.drawLine(QPointF(r.left(), r.top() + header_height), QPointF(r.right(), r.top() + header_height))
                # Draw column separators
                col_width = r.width() / 3
                for i in range(1, 3):
                    x = r.left() + i * col_width
                    painter.drawLine(QPointF(x, r.top() + header_height), QPointF(x, r.bottom()))
            elif s.mode == "entity":
                # Draw entity (rectangle with bold border)
                r = QRectF(s.points[0], s.end_pos).normalized()
                # Save current pen
                old_pen = painter.pen()
                # Make border thicker for entity
                thick_pen = QPen(old_pen.color(), old_pen.width() + 2)
                painter.setPen(thick_pen)
                painter.drawRect(r)
                # Restore pen
                painter.setPen(old_pen)
            elif s.mode == "relationship":
                # Draw relationship (diamond shape)
                r = QRectF(s.points[0], s.end_pos).normalized()
                center = r.center()
                diamond_points = [QPointF(center.x(), r.top()),
                                  QPointF(r.right(), center.y()),
                                  QPointF(center.x(), r.bottom()),
                                  QPointF(r.left(), center.y())]
                diamond_polygon = QPolygonF(diamond_points)
                painter.drawPolygon(diamond_polygon)
            elif s.mode == "note":
                # Draw note (rectangle with folded corner)
                r = QRectF(s.points[0], s.end_pos).normalized()
                # Draw main rectangle
                painter.drawRect(r)
                # Draw folded corner
                corner_size = min(r.width(), r.height()) * 0.2
                fold_points = [QPointF(r.right(), r.top() + corner_size),
                               QPointF(r.right() - corner_size, r.top()),
                               QPointF(r.right() - corner_size, r.top() + corner_size)]
                fold_polygon = QPolygonF(fold_points)
                painter.drawPolygon(fold_polygon)
            elif s.mode == "component":
                # Draw component (rectangle with icon)
                r = QRectF(s.points[0], s.end_pos).normalized()
                painter.drawRect(r)
                # Draw simple component icon
                icon_size = min(r.width(), r.height()) * 0.3
                icon_rect = QRectF(r.center().x() - icon_size/2, r.center().y() - icon_size/2, icon_size, icon_size)
                painter.drawEllipse(icon_rect)
            elif s.mode == "class":
                # Draw UML class (rectangle with three sections)
                r = QRectF(s.points[0], s.end_pos).normalized()
                painter.drawRect(r)
                # Draw section separators
                section_height = r.height() / 3
                for i in range(1, 3):
                    y = r.top() + i * section_height
                    painter.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
            elif s.mode == "use_case":
                # Draw use case (ellipse)
                r = QRectF(s.points[0], s.end_pos).normalized()
                painter.drawEllipse(r)
            elif s.mode in ["orthogonal_line", "curved_connection", "dashed_line", "elbow_connector"]:
                # Draw connection lines
                start = s.points[0]
                end = s.end_pos
                
                if s.mode == "orthogonal_line":
                    # Draw orthogonal connection (right angles)
                    mid_x = (start.x() + end.x()) / 2
                    painter.drawLine(int(start.x()), int(start.y()), int(mid_x), int(start.y()))
                    painter.drawLine(int(mid_x), int(start.y()), int(mid_x), int(end.y()))
                    painter.drawLine(int(mid_x), int(end.y()), int(end.x()), int(end.y()))
                elif s.mode == "curved_connection":
                    # Draw curved connection
                    path = QPainterPath()
                    path.moveTo(start)
                    ctrl_x = (start.x() + end.x()) / 2
                    ctrl_y = min(start.y(), end.y()) - 30
                    path.quadTo(QPointF(ctrl_x, ctrl_y), end)
                    painter.drawPath(path)
                elif s.mode == "dashed_line":
                    # Draw dashed line
                    old_style = painter.pen().style()
                    pen = painter.pen()
                    pen.setStyle(Qt.DashLine)
                    painter.setPen(pen)
                    painter.drawLine(start, end)
                    pen.setStyle(old_style)
                    painter.setPen(pen)
                elif s.mode == "elbow_connector":
                    # Draw elbow connector (L-shape)
                    if abs(end.x() - start.x()) > abs(end.y() - start.y()):
                        # Horizontal first
                        mid_x = (start.x() + end.x()) / 2
                        painter.drawLine(int(start.x()), int(start.y()), int(mid_x), int(start.y()))
                        painter.drawLine(int(mid_x), int(start.y()), int(mid_x), int(end.y()))
                        painter.drawLine(int(mid_x), int(end.y()), int(end.x()), int(end.y()))
                    else:
                        # Vertical first
                        mid_y = (start.y() + end.y()) / 2
                        painter.drawLine(int(start.x()), int(start.y()), int(start.x()), int(mid_y))
                        painter.drawLine(int(start.x()), int(mid_y), int(end.x()), int(mid_y))
                        painter.drawLine(int(end.x()), int(mid_y), int(end.x()), int(end.y()))

        # Enhanced Smooth Laser Rendering
        now = time.monotonic()
        for trail in self.laser_trails:
            interpolated = trail.get_interpolated_points(self.laser_smoothness)
            if len(interpolated) >= 2:
                for i in range(len(interpolated) - 1):
                    age1 = now - trail.timestamps[min(i, len(trail.timestamps) - 1)]
                    age2 = now - trail.timestamps[min(i + 1, len(trail.timestamps) - 1)]
                    alpha1 = max(0, 255 * (1 - age1 / self.laser_duration))
                    alpha2 = max(0, 255 * (1 - age2 / self.laser_duration))
                    c1 = QColor(trail.color)
                    c2 = QColor(trail.color)
                    c1.setAlpha(int(alpha1))
                    c2.setAlpha(int(alpha2))
                    
                    if self.laser_glow:
                        # Draw glow effect
                        for glow_size in [3, 2, 1]:
                            glow_alpha = max(0, alpha1 * (0.3 - glow_size * 0.1))
                            glow_c = QColor(trail.color)
                            glow_c.setAlpha(int(glow_alpha))
                            painter.setPen(QPen(glow_c, trail.thickness + glow_size * 2, Qt.SolidLine, Qt.RoundCap))
                            painter.drawLine(interpolated[i], interpolated[i + 1])
                    
                    # Draw main laser line
                    grad = QRadialGradient(interpolated[i], trail.thickness / 2)
                    grad.setColorAt(0, c1)
                    grad.setColorAt(1, c2)
                    painter.setPen(QPen(QBrush(grad), trail.thickness, Qt.SolidLine, Qt.RoundCap))
                    painter.drawLine(interpolated[i], interpolated[i + 1])

        # Draw selection handles for selected shapes
        for s in self.shapes:
            if s.is_selected:
                # Calculate the bounding rectangle of the shape
                bounding_rect = self.calculate_shape_bounding_rect(s)
                if bounding_rect:
                    # Draw selection box
                    painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.DashLine))  # Blue dashed outline
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(bounding_rect)
                    
                    # Draw resize handles at corners and edges
                    handle_size = 8  # Visual size of handles
                    handle_color = QColor(0, 120, 215)
                    painter.setPen(QPen(handle_color, 1))
                    painter.setBrush(handle_color)
                    
                    # Corner handles
                    corners = [
                        (bounding_rect.topLeft(), 'top-left'),
                        (bounding_rect.topRight(), 'top-right'),
                        (bounding_rect.bottomLeft(), 'bottom-left'),
                        (bounding_rect.bottomRight(), 'bottom-right'),
                        # Edge handles
                        (QPointF(bounding_rect.center().x(), bounding_rect.top()), 'top-center'),
                        (QPointF(bounding_rect.center().x(), bounding_rect.bottom()), 'bottom-center'),
                        (QPointF(bounding_rect.left(), bounding_rect.center().y()), 'left-center'),
                        (QPointF(bounding_rect.right(), bounding_rect.center().y()), 'right-center'),
                    ]
                    
                    for pos, handle_type in corners:
                        # Adjust position to center the handle
                        handle_rect = QRectF(pos.x() - handle_size/2, pos.y() - handle_size/2, handle_size, handle_size)
                        painter.drawRect(handle_rect)
                    
                    # Draw rotation handle (a circle above the shape)
                    rotation_handle_pos = QPointF(bounding_rect.center().x(), bounding_rect.top() - 25)
                    painter.setBrush(QColor(255, 0, 0))  # Red color for rotation handle
                    rotation_handle_rect = QRectF(rotation_handle_pos.x() - handle_size/2, rotation_handle_pos.y() - handle_size/2, handle_size, handle_size)
                    painter.drawEllipse(rotation_handle_rect)

    def get_handle_at_position(self, shape, pos):
        """Check if the position is on any of the selection handles"""
        bounding_rect = self.calculate_shape_bounding_rect(shape)
        if not bounding_rect:
            return None
        
        handle_size = 12  # Larger hit area for handles (was 8)
        
        # Define handles at corners and edges
        handles = {
            'top-left': bounding_rect.topLeft(),
            'top-right': bounding_rect.topRight(),
            'bottom-left': bounding_rect.bottomLeft(),
            'bottom-right': bounding_rect.bottomRight(),
            'top-center': QPointF(bounding_rect.center().x(), bounding_rect.top()),
            'bottom-center': QPointF(bounding_rect.center().x(), bounding_rect.bottom()),
            'left-center': QPointF(bounding_rect.left(), bounding_rect.center().y()),
            'right-center': QPointF(bounding_rect.right(), bounding_rect.center().y()),
        }
        
        # Add rotation handle at top center (a bit above)
        rotation_handle_pos = QPointF(bounding_rect.center().x(), bounding_rect.top() - 25)
        handles['rotation'] = rotation_handle_pos
        
        for handle_name, handle_pos in handles.items():
            handle_rect = QRectF(handle_pos.x() - handle_size/2, handle_pos.y() - handle_size/2, handle_size, handle_size)
            if handle_rect.contains(pos):
                return handle_name
        
        # Also check if the position is inside the shape for moving
        if bounding_rect.contains(pos):
            return 'move'
        
        return None

    def get_cursor_for_handle(self, handle_type):
        """Return appropriate cursor for the given handle type"""
        if handle_type == 'move':
            return Qt.SizeAllCursor
        elif handle_type in ['top-left', 'bottom-right']:
            return Qt.SizeFDiagCursor
        elif handle_type in ['top-right', 'bottom-left']:
            return Qt.SizeBDiagCursor
        elif handle_type in ['top-center', 'bottom-center']:
            return Qt.SizeVerCursor
        elif handle_type in ['left-center', 'right-center']:
            return Qt.SizeHorCursor
        elif handle_type == 'rotation':
            return Qt.PointingHandCursor
        else:
            return Qt.ArrowCursor

    def resize_shape(self, pos):
        """Resize the selected shape based on the active handle"""
        if not self.selected_shape or not self.active_handle:
            return
            
        # Handle rotation separately
        if self.active_handle == 'rotation':
            self.rotate_shape(pos)
            return
                
        # Calculate the scale factors based on drag distance
        if self.original_bounding_rect and self.drag_start_pos:
            # Calculate the new position relative to the drag start
            dx = pos.x() - self.drag_start_pos.x()
            dy = pos.y() - self.drag_start_pos.y()
                
            # Calculate relative position within the original bounding box
            orig_width = self.original_bounding_rect.width()
            orig_height = self.original_bounding_rect.height()
                
            if orig_width == 0: orig_width = 1
            if orig_height == 0: orig_height = 1
                
            # Different behavior depending on which handle is being dragged
            if self.active_handle == 'top-left':
                # Resize from top-left corner - adjust both width and height negatively
                new_width = max(10, orig_width - dx)
                new_height = max(10, orig_height - dy)
                scale_x = new_width / orig_width
                scale_y = new_height / orig_height
                self.apply_scale_to_shape(scale_x, scale_y, self.original_bounding_rect.topLeft())
            elif self.active_handle == 'top-right':
                # Resize from top-right corner - adjust width positively, height negatively
                new_width = max(10, orig_width + dx)
                new_height = max(10, orig_height - dy)
                scale_x = new_width / orig_width
                scale_y = new_height / orig_height
                self.apply_scale_to_shape(scale_x, scale_y, self.original_bounding_rect.topRight())
            elif self.active_handle == 'bottom-left':
                # Resize from bottom-left corner - adjust width negatively, height positively
                new_width = max(10, orig_width - dx)
                new_height = max(10, orig_height + dy)
                scale_x = new_width / orig_width
                scale_y = new_height / orig_height
                self.apply_scale_to_shape(scale_x, scale_y, self.original_bounding_rect.bottomLeft())
            elif self.active_handle == 'bottom-right':
                # Resize from bottom-right corner - adjust both width and height positively
                new_width = max(10, orig_width + dx)
                new_height = max(10, orig_height + dy)
                scale_x = new_width / orig_width
                scale_y = new_height / orig_height
                self.apply_scale_to_shape(scale_x, scale_y, self.original_bounding_rect.bottomRight())
            elif self.active_handle == 'top-center':
                # Resize vertically from top edge only
                new_height = max(10, orig_height - dy)
                scale_y = new_height / orig_height
                self.apply_scale_to_shape(1.0, scale_y, self.original_bounding_rect.bottomLeft())
            elif self.active_handle == 'bottom-center':
                # Resize vertically from bottom edge only
                new_height = max(10, orig_height + dy)
                scale_y = new_height / orig_height
                self.apply_scale_to_shape(1.0, scale_y, self.original_bounding_rect.topLeft())
            elif self.active_handle == 'left-center':
                # Resize horizontally from left edge only
                new_width = max(10, orig_width - dx)
                scale_x = new_width / orig_width
                self.apply_scale_to_shape(scale_x, 1.0, self.original_bounding_rect.topRight())
            elif self.active_handle == 'right-center':
                # Resize horizontally from right edge only
                new_width = max(10, orig_width + dx)
                scale_x = new_width / orig_width
                self.apply_scale_to_shape(scale_x, 1.0, self.original_bounding_rect.topLeft())
    
    def rotate_shape(self, pos):
        """Rotate the selected shape based on mouse movement"""
        if not self.selected_shape or not self.original_bounding_rect:
            return
                
        # Calculate the center of the shape
        center = self.original_bounding_rect.center()
            
        # Calculate angle between original position and current position
        original_angle = math.atan2(self.drag_start_pos.y() - center.y(), self.drag_start_pos.x() - center.x())
        current_angle = math.atan2(pos.y() - center.y(), pos.x() - center.x())
            
        # Calculate rotation angle in degrees
        angle_delta = (current_angle - original_angle) * 180 / math.pi
            
        # Store the rotation angle in the shape
        if not hasattr(self.selected_shape, 'rotation'):
            self.selected_shape.rotation = 0
        self.selected_shape.rotation = angle_delta

    def apply_scale_to_shape(self, scale_x, scale_y, anchor_point):
        """Apply scaling transformation to the shape with respect to an anchor point"""
        if not self.selected_shape or not self.original_shape_points:
            return
        
        # Scale the shape based on the anchor point
        for i, orig_point in enumerate(self.original_shape_points):
            if i < len(self.selected_shape.points):
                # Calculate offset from anchor point
                offset_x = orig_point.x() - anchor_point.x()
                offset_y = orig_point.y() - anchor_point.y()
                
                # Apply scaling
                new_offset_x = offset_x * scale_x
                new_offset_y = offset_y * scale_y
                
                # Calculate new position
                new_x = anchor_point.x() + new_offset_x
                new_y = anchor_point.y() + new_offset_y
                
                self.selected_shape.points[i] = QPointF(new_x, new_y)
        
        # Also scale the end_pos if it exists
        if self.original_shape_end_pos and hasattr(self.selected_shape, 'end_pos'):
            offset_x = self.original_shape_end_pos.x() - anchor_point.x()
            offset_y = self.original_shape_end_pos.y() - anchor_point.y()
            
            new_offset_x = offset_x * scale_x
            new_offset_y = offset_y * scale_y
            
            new_x = anchor_point.x() + new_offset_x
            new_y = anchor_point.y() + new_offset_y
            
            self.selected_shape.end_pos = QPointF(new_x, new_y)

    def calculate_shape_bounding_rect(self, shape):
        """Calculate the bounding rectangle for a given shape"""
        if shape.mode == "text":
            # For text, calculate based on font metrics
            font = QFont("Segoe Print", 22, QFont.Bold)
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(shape.text)
            text_height = fm.height()
            return QRectF(shape.points[0].x(), shape.points[0].y() - fm.ascent(), text_width, text_height)
        elif shape.mode in ["rect", "ellipse", "diamond"]:
            # For geometric shapes, use the two defining points
            top_left = QPointF(min(shape.points[0].x(), shape.end_pos.x()), min(shape.points[0].y(), shape.end_pos.y()))
            bottom_right = QPointF(max(shape.points[0].x(), shape.end_pos.x()), max(shape.points[0].y(), shape.end_pos.y()))
            return QRectF(top_left, bottom_right)
        elif shape.mode in ["pencil", "highlighter"]:
            # For freehand drawing, calculate from all points
            if not shape.points:
                return QRectF()
            min_x = min(p.x() for p in shape.points)
            max_x = max(p.x() for p in shape.points)
            min_y = min(p.y() for p in shape.points)
            max_y = max(p.y() for p in shape.points)
            return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        else:
            # For other shapes, use a reasonable bounding box
            return QRectF(shape.points[0].x() - 10, shape.points[0].y() - 10, 20, 20)

    def is_point_in_shape(self, shape, point):
        """Check if a point is inside a shape for selection purposes"""
        if shape.mode == "text":
            text_rect = QRectF(shape.points[0].x(), shape.points[0].y() - 20, 200, 40)
            return text_rect.contains(point)
        elif shape.mode in ["rect", "ellipse", "diamond"]:
            rect = QRectF(shape.points[0], shape.end_pos).normalized()
            return rect.contains(point)
        elif shape.mode == "arrow":
            p1, p2 = shape.points[0], shape.end_pos
            # Simple distance check for arrow
            dist = ((point.x() - p1.x()) * (p2.y() - p1.y()) - (point.y() - p1.y()) * (p2.x() - p1.x())) / math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
            return abs(dist) < 10  # 10 pixel tolerance
        elif shape.mode in ["pencil", "highlighter"]:
            # For freehand shapes, check if point is near any of the points
            for p in shape.points:
                if math.hypot(point.x() - p.x(), point.y() - p.y()) < 15:  # 15 pixel tolerance
                    return True
            return False
        elif shape.mode in ["db_table", "entity", "relationship", "note", "component", "class", "use_case"]:
            # For diagram shapes, use rectangular bounding box
            rect = QRectF(shape.points[0], shape.end_pos).normalized()
            return rect.contains(point)
        elif shape.mode in ["orthogonal_line", "curved_connection", "dashed_line", "elbow_connector"]:
            # For connection lines, check if point is near the line
            p1, p2 = shape.points[0], shape.end_pos
            # Simple distance check for lines
            dist = ((point.x() - p1.x()) * (p2.y() - p1.y()) - (point.y() - p1.y()) * (p2.x() - p1.x())) / math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
            return abs(dist) < 10  # 10 pixel tolerance
        return False

    def get_text_shape_at_position(self, pos):
        """Find text shape at given position"""
        for s in reversed(self.shapes):
            if s.mode == "text" and self.is_point_in_shape(s, pos):
                return s
        return None
    
    def get_text_bounds(self, text_shape):
        """Calculate the bounding rectangle for the given text shape"""
        if text_shape.mode != "text":
            return None
        
        # Use QFontMetrics to get accurate text dimensions
        font = QFont("Segoe Print", 22, QFont.Bold)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text_shape.text)
        text_height = fm.height()
        
        # Position the highlight rectangle around the text
        # Adjust for font baseline and padding
        x = text_shape.points[0].x()
        y = text_shape.points[0].y() - fm.ascent()  # Adjust for baseline
        
        # Add some padding to make the highlight more visible
        padding = 2
        return QRectF(x - padding, y - padding, text_width + 2 * padding, text_height + 2 * padding)
    
    def erase_at(self, pos):
        for s in self.shapes[:]:
            if self.is_point_in_shape(s, pos):
                self.shapes.remove(s)
                self.save_state()
                break
        self.update()
    
    def apply_zoom_area(self):
        """Apply zoom to the selected area"""
        if not self.zoom_start_pos or not self.zoom_end_pos:
            return
            
        # Calculate the center and dimensions of the zoom area
        x1, y1 = self.zoom_start_pos.x(), self.zoom_start_pos.y()
        x2, y2 = self.zoom_end_pos.x(), self.zoom_end_pos.y()
        
        # Ensure coordinates are in correct order
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Set zoom factor based on the selected area size
        base_size = 100  # Base size for 2x zoom
        area_size = min(width, height)
        
        if area_size > 0:
            self.zoom_factor = max(base_size / area_size, 1.0)
        else:
            self.zoom_factor = 2.0
            
        # Set the center of the zoom to the center of the selected area
        self.zoom_center = QPointF(left + width / 2, top + height / 2)
        
        # Show zoom effect temporarily
        self.is_zoom_active = True
        QTimer.singleShot(2000, lambda: setattr(self, 'is_zoom_active', False))  # Turn off zoom after 2 seconds

    def mousePressEvent(self, event):
        if self.mode == "mouse":
            return
            
        pos = event.pos()
        
        # Check if click is on toolbar area to prevent drawing there
        toolbar_geo = self.toolbar.geometry()
        toolbar_global_pos = self.mapToGlobal(self.toolbar.pos())
        toolbar_rect = QRect(toolbar_global_pos, self.toolbar.size())
        
        if toolbar_rect.contains(event.globalPos()):
            # Click is on toolbar area, let toolbar handle it
            self.toolbar.raise_()
            return
        
        if self.mode == "select":
            # First, check if we're clicking on a handle of an already selected shape
            if self.selected_shape and self.selected_shape.is_selected:
                handle_at_pos = self.get_handle_at_position(self.selected_shape, pos)
                if handle_at_pos:
                    # We're interacting with a handle of the selected shape
                    self.active_handle = handle_at_pos
                    self.drag_start_pos = pos
                    self.original_shape_points = [QPointF(p) for p in self.selected_shape.points]
                    if hasattr(self.selected_shape, 'end_pos'):
                        self.original_shape_end_pos = QPointF(self.selected_shape.end_pos)
                    self.original_bounding_rect = self.calculate_shape_bounding_rect(self.selected_shape)
                    self.last_pos = pos
                    self.update()
                    return  # Early return to prevent deselection
            
            # If we reach here, either no shape was selected or click was not on a handle
            # Deselect any currently selected shape
            if self.selected_shape:
                self.selected_shape.is_selected = False
            self.selected_shape = None
            self.active_handle = None
            
            # Now check if clicked on any shape
            for s in reversed(self.shapes):
                if self.is_point_in_shape(s, pos):
                    # Check if it's a text shape and handle double-click for editing
                    if s.mode == "text" and hasattr(self, 'last_click_time') and hasattr(self, 'last_click_pos'):
                        current_time = time.time()
                        if (current_time - self.last_click_time < 0.5 and  # Double click within 500ms
                            math.hypot(pos.x() - self.last_click_pos.x(), pos.y() - self.last_click_pos.y()) < 10):  # Close position
                            self.edit_text_shape(s, s.points[0])
                            return
                    
                    # Deselect any other selected shapes
                    for other_shape in self.shapes:
                        other_shape.is_selected = False
                    self.selected_shape = s
                    s.is_selected = True
                    # Check if clicked on a handle
                    self.active_handle = self.get_handle_at_position(s, pos)
                    if self.active_handle:
                        self.drag_start_pos = pos
                        self.original_shape_points = [QPointF(p) for p in s.points]
                        if hasattr(s, 'end_pos'):
                            self.original_shape_end_pos = QPointF(s.end_pos)
                        self.original_bounding_rect = self.calculate_shape_bounding_rect(s)
                    self.last_pos = pos
                    
                    # Store click information for double-click detection
                    self.last_click_time = time.time()
                    self.last_click_pos = QPointF(pos)
                    break
            else:
                # Clicked on empty space - deselect all
                for s in self.shapes:
                    s.is_selected = False
                self.selected_shape = None
        elif self.mode == "text":
            self.open_text_input(pos)
        elif self.mode == "laser":
            self.current_laser = LaserTrail(pos, self.laser_color, self.laser_thickness, self.laser_duration, self.laser_smoothness)
            self.laser_trails.append(self.current_laser)
        elif self.mode == "zoom":
            self.zoom_start_pos = pos
            self.is_zoom_active = True
        elif self.mode == "eraser":
            self.erase_at(pos)
        elif self.mode == "highlighter":
            # Check if we're highlighting over existing text
            text_shape = self.get_text_shape_at_position(pos)
            if text_shape:
                # Create a text-aligned highlight
                self.current_shape = TutorShape(self.mode, pos, self.current_color, self.current_thickness)
                self.current_shape.text_bounds = self.get_text_bounds(text_shape)
            else:
                # Free-form highlighter drawing
                self.current_shape = TutorShape(self.mode, pos, self.current_color, self.current_thickness)
        else:
            self.current_shape = TutorShape(self.mode, pos, self.current_color, self.current_thickness)
            if self.enable_fill and self.mode in ["rect", "ellipse", "diamond"]:
                self.current_shape.fill_color = self.current_color
        
        self.update()

    def mouseMoveEvent(self, event):
        if self.mode == "mouse":
            return
            
        pos = event.pos()
        
        # Handle cursor changes based on hover position when in select mode
        if self.mode == "select":
            if self.selected_shape and not self.active_handle:
                # Check if we're hovering over a handle (only when not actively dragging)
                handle = self.get_handle_at_position(self.selected_shape, pos)
                if handle:
                    cursor = self.get_cursor_for_handle(handle)
                    self.setCursor(cursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
            elif self.selected_shape and self.active_handle:
                # During active dragging, don't change cursor as it's handled by the transformation
                pass
            else:
                self.setCursor(Qt.ArrowCursor)
        
        if self.mode == "select" and self.selected_shape:
            if self.active_handle:
                # Handle resizing and transformation
                if self.active_handle == 'move':
                    # Moving the shape
                    delta = pos - self.last_pos
                    # For line/pencil shapes, move all points
                    if self.selected_shape.mode in ["pencil", "highlighter"]:
                        for i in range(len(self.selected_shape.points)):
                            self.selected_shape.points[i] += delta
                    else:
                        # For other shapes, move the main points
                        self.selected_shape.points[0] += delta
                        if hasattr(self.selected_shape, 'end_pos'):
                            self.selected_shape.end_pos += delta
                    self.last_pos = pos
                else:
                    # Resizing the shape based on handle
                    self.resize_shape(pos)
            else:
                # Moving the entire shape
                delta = pos - self.last_pos
                # For line/pencil shapes, move all points
                if self.selected_shape.mode in ["pencil", "highlighter"]:
                    for i in range(len(self.selected_shape.points)):
                        self.selected_shape.points[i] += delta
                else:
                    # For other shapes, move the main points
                    self.selected_shape.points[0] += delta
                    if hasattr(self.selected_shape, 'end_pos'):
                        self.selected_shape.end_pos += delta
                self.last_pos = pos
        elif self.mode == "laser" and self.current_laser:
            self.current_laser.add_point(pos)
        elif self.mode == "zoom" and self.zoom_start_pos:
            self.zoom_end_pos = pos
        elif self.current_shape:
            if self.mode in ["pencil", "highlighter"]:
                self.current_shape.points.append(pos)
            else:
                self.current_shape.end_pos = pos
        
        self.update()

    def mouseReleaseEvent(self, event):
        if self.mode == "mouse":
            return
            
        if self.mode == "select":
            # Don't deselect the shape - keep it selected until another tool is chosen or another element is selected
            pass
        elif self.mode == "laser":
            self.current_laser = None
        elif self.mode == "zoom" and self.zoom_start_pos and self.zoom_end_pos:
            self.apply_zoom_area()
            self.zoom_start_pos = None
            self.zoom_end_pos = None
            self.is_zoom_active = False
        elif self.current_shape:
            if self.mode in ["pencil", "highlighter"]:
                self.current_shape.points.append(event.pos())
            else:
                self.current_shape.end_pos = event.pos()
            self.shapes.append(self.current_shape)
            self.save_state()
            self.current_shape = None
        
        self.update()

    def keyPressEvent(self, event):
        # Handle all shortcut combinations for tool switching
        key_text = event.text().upper() if event.text() else ""
        
        # Build the shortcut string based on modifiers
        shortcut_parts = []
        
        if event.modifiers() & Qt.ControlModifier:
            shortcut_parts.append("Ctrl")
        if event.modifiers() & Qt.ShiftModifier:
            shortcut_parts.append("Shift")
        if event.modifiers() & Qt.AltModifier:
            shortcut_parts.append("Alt")
        
        # Add the key character
        if key_text and key_text.isalpha():
            shortcut_parts.append(key_text)
        
        # Create full shortcut string
        if shortcut_parts:
            shortcut_str = "+".join(shortcut_parts)
            
            # Check if this shortcut matches any tool
            for mode, shortcut in self.shortcuts.items():
                if shortcut.upper() == shortcut_str.upper():
                    self.set_mode(mode)
                    event.accept()
                    return
        
        # Handle special keys
        if event.key() == Qt.Key_Escape:
            QApplication.instance().quit()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.undo()
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            self.redo()
        elif event.key() == Qt.Key_B and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
            # Toggle board mode with Ctrl+Shift+B
            self.quick_toggle_board()
        elif event.key() == Qt.Key_H and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
            # Toggle toolbar hide/unhide with Ctrl+Shift+H
            self.toggle_toolbar_visibility()
        else:
            event.ignore()

    def apply_theme(self, theme_name):
        """Apply the specified theme to the canvas and all components"""
        self.current_theme = theme_name
        # Import theme manager inside the method to avoid circular imports
        from src.themes_system import theme_manager
        theme_data = theme_manager.get_theme_stylesheet(theme_name)
        
        # Apply theme to canvas background
        if self.board_transparent:
            bg_color = theme_data["canvas_bg"]
        else:
            bg_color = theme_data["bg_color"]
            
        self.setStyleSheet(f"background-color: {bg_color};")
        
        # Update toolbar if it exists
        if hasattr(self, 'toolbar'):
            self.toolbar.apply_theme(theme_name)
        
        # Update hide handle if it exists
        if hasattr(self, 'hide_handle'):
            self.hide_handle.apply_theme(theme_name)
        
        # Update other UI components as needed
        self.update()
        
    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme