import time
import math
import os
import json
import tempfile

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QMessageBox, QColorDialog, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QRect
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QPainterPath, QFont, QRadialGradient, QBrush, QFontMetrics, QIcon
)

CONFIG_FILE = "tutordraw_settings.json"

class TutorShape:
    def __init__(self, mode, start, color, thickness=4, text="", fill_color=None):
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
        self.setFixedSize(30, 30)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Import theme manager inside the method to avoid circular imports
        from src.themes_system import theme_manager
        self.apply_theme(getattr(self.canvas, 'current_theme', 'Light'))
        self.hide()

    def apply_theme(self, theme_name):
        """Apply theme to the hide handle"""
        # Import theme manager inside the method to avoid circular imports
        from src.themes_system import theme_manager
        theme_data = theme_manager.get_theme_stylesheet(theme_name)
        accent_color = theme_data['accent_color']
        icon_color = theme_data['icon_color']
        
        self.setStyleSheet(f"""
            background: {accent_color};
            border-radius: 15px;
            border: 2px solid {icon_color};
        """)
    
    def mousePressEvent(self, event):
        self.canvas.peek_toolbar()
    
    def enterEvent(self, event):
        self.setStyleSheet("""
            background: rgba(105, 101, 219, 1.0);
            border-radius: 15px;
            border: 2px solid white;
        """)
    
    def leaveEvent(self, event):
        self.setStyleSheet("""
            background: rgba(105, 101, 219, 0.9);
            border-radius: 15px;
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
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setGeometry(QApplication.primaryScreen().geometry())
        
        # Set window icon with fallback
        import os
        if os.path.exists("tutorDraw-logoX92.png"):
            self.setWindowIcon(QIcon("tutorDraw-logoX92.png"))
        
        # Initialize attributes needed by original toolbar first
        self.current_theme = "Light"  # Default theme
        self.toolbar_orientation = "horizontal"
        self.current_color = QColor(255, 0, 0)  # Red default for visibility
        self.current_thickness = 4
        self.default_thickness = 4
        self.enable_fill = False
        self.board_transparent = True  # Start in annotation mode
        
        # Selection and transformation attributes
        self.active_handle = None  # Which handle is currently being manipulated
        self.drag_start_pos = None  # Starting position for dragging/resizing
        self.original_shape_points = None  # Original points before transformation
        self.original_shape_end_pos = None  # Original end_pos before transformation
        self.original_bounding_rect = None  # Original bounding rect for transformations
        
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
        
        self.shortcuts = {"mouse": "M", "select": "V", "pencil": "P", "rect": "R", "diamond": "D", "ellipse": "E", "arrow": "A", "text": "T", "laser": "L", "eraser": "X", "clear": "C"}
        self.load_config()

        # Use original toolbar design with 3-dot menu
        from src.toolbar import TutorToolbar
        from src.themes_system import theme_manager
        self.toolbar = TutorToolbar(self)
        self.hide_handle = HideHandle(self)
        self.toolbar.show()
        self.toolbar.move((self.width() - self.toolbar.width()) // 2, 60)
        # Ensure toolbar stays on top
        self.toolbar.raise_()
        
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
                    self.shortcuts.update(d.get("shortcuts", {}))
                    self.laser_color = d.get("laser_color", self.laser_color)
                    self.laser_thickness = d.get("laser_thickness", self.laser_thickness)
                    self.laser_duration = d.get("laser_duration", self.laser_duration)
                    self.laser_smoothness = d.get("laser_smoothness", self.laser_smoothness)
                    self.laser_glow = d.get("laser_glow", self.laser_glow)
                    self.default_thickness = d.get("default_thickness", self.default_thickness)
                    self.enable_fill = d.get("enable_fill", self.enable_fill)
                    self.toolbar_orientation = d.get("toolbar_orientation", self.toolbar_orientation)
                    self.current_theme = d.get("current_theme", self.current_theme)
            except:
                pass

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"shortcuts": self.shortcuts, "laser_color": self.laser_color, "laser_thickness": self.laser_thickness, "laser_duration": self.laser_duration, "laser_smoothness": self.laser_smoothness, "laser_glow": self.laser_glow, "default_thickness": self.default_thickness, "enable_fill": self.enable_fill, "toolbar_orientation": self.toolbar_orientation, "current_theme": self.current_theme}, f, indent=2)

    def hide_toolbar_permanent(self):
        self.is_hidden = True
        self.toolbar_last_pos = self.toolbar.pos()
        self.toolbar.hide()
        self.hide_handle.move(10, 10)
        self.hide_handle.show()
        
    def peek_toolbar(self):
        if self.is_hidden:
            if self.toolbar_orientation == "horizontal":
                self.toolbar.move(self.hide_handle.x(), self.hide_handle.y() + self.hide_handle.height())
            else:
                self.toolbar.move(self.hide_handle.x() + self.hide_handle.width(), self.hide_handle.y())
            self.toolbar.show()
            self.toolbar.raise_()
            
    def restore_toolbar(self):
        self.is_hidden = False
        self.hide_handle.hide()
        if self.toolbar_last_pos:
            self.toolbar.move(self.toolbar_last_pos)
        self.toolbar.show()

    def set_mode(self, mode):
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

    def open_color_picker(self):
        d = QColorDialog(self.current_color, self)
        d.setWindowFlags(Qt.WindowStaysOnTopHint)
        if d.exec_() == QColorDialog.Accepted:
            self.current_color = d.selectedColor()
            # Original toolbar doesn't have update_color_button method
            # Just update the color and refresh the display
            self.update()
    
    def toggle_board(self):
        """Toggle between transparent annotation and whiteboard mode"""
        self.board_transparent = not self.board_transparent
        if self.board_transparent:
            # Transparent annotation mode
            self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        else:
            # Whiteboard mode
            self.setStyleSheet("background-color: rgba(255, 255, 255, 220);")
        self.hide()
        self.show()
    
    # Methods for original toolbar compatibility
    def hide_toolbar_permanent_func(self):
        """Hide toolbar permanently until restored"""
        self.is_hidden = True
        self.toolbar_last_pos = self.toolbar.pos()
        self.toolbar.hide()
        self.hide_handle.move(10, 10)
        self.hide_handle.show()
        
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

    def open_text_input(self, pos):
        if self.input_box:
            self.finish_text(self.input_box_pos)
        self.input_box_pos = pos
        self.input_box = QLineEdit(self)
        self.input_box.setStyleSheet(f"border: 1px dashed #6965db; background: white; color: {self.current_color.name()}; font-size: 20px; padding: 5px;")
        self.input_box.move(int(pos.x()), int(pos.y()))
        self.input_box.show()
        self.input_box.setFocus()
        self.input_box.editingFinished.connect(lambda: self.finish_text(pos))

    def finish_text(self, pos):
        if self.input_box:
            txt = self.input_box.text()
            if txt.strip():
                shape = TutorShape("text", pos, self.current_color, self.default_thickness, txt)
                self.shapes.append(shape)
                self.save_state()
            self.input_box.deleteLater()
            self.input_box = None
            self.update()

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
                self.toolbar.update_theme_style()

    def save_state(self):
        self.undo_stack.append([TutorShape(s.mode, s.points[0], s.color.name(), s.thickness, s.text, s.fill_color.name() if s.fill_color else None) for s in self.shapes])
        self.redo_stack = []
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append([TutorShape(s.mode, s.points[0], s.color.name(), s.thickness, s.text, s.fill_color.name() if s.fill_color else None) for s in self.shapes])
            self.shapes = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append([TutorShape(s.mode, s.points[0], s.color.name(), s.thickness, s.text, s.fill_color.name() if s.fill_color else None) for s in self.shapes])
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
            w = self.default_thickness if not hasattr(s, 'thickness') else s.thickness
            w = w + 2 if s.is_selected else w
            painter.setPen(QPen(s.color, w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
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
                painter.setFont(QFont("Segoe Print", 22, QFont.Bold))
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
                painter.drawPolygon([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()), 
                                   QPointF(r.center().x(), r.bottom()), QPointF(r.left(), r.center().y())])

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
                    handle_size = 6
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

    def get_handle_at_position(self, shape, pos):
        """Check if the position is on any of the selection handles"""
        bounding_rect = self.calculate_shape_bounding_rect(shape)
        if not bounding_rect:
            return None
        
        handle_size = 8  # Larger hit area for handles
        
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
        
        for handle_name, handle_pos in handles.items():
            handle_rect = QRectF(handle_pos.x() - handle_size/2, handle_pos.y() - handle_size/2, handle_size, handle_size)
            if handle_rect.contains(pos):
                return handle_name
        
        # Also check if the position is inside the shape for moving
        if bounding_rect.contains(pos):
            return 'move'
        
        return None

    def resize_shape(self, pos):
        """Resize the selected shape based on the active handle"""
        if not self.selected_shape or not self.active_handle:
            return
        
        # Calculate the scale factors based on drag distance
        if self.original_bounding_rect and self.drag_start_pos:
            dx = pos.x() - self.drag_start_pos.x()
            dy = pos.y() - self.drag_start_pos.y()
            
            # Calculate relative position within the original bounding box
            orig_width = self.original_bounding_rect.width()
            orig_height = self.original_bounding_rect.height()
            
            if orig_width == 0: orig_width = 1
            if orig_height == 0: orig_height = 1
            
            # Different behavior depending on which handle is being dragged
            if self.active_handle == 'top-left':
                # Resize from top-left corner
                scale_x = max(0.1, (orig_width - dx) / orig_width)
                scale_y = max(0.1, (orig_height - dy) / orig_height)
                self.apply_scale_to_shape(scale_x, scale_y, self.original_bounding_rect.topLeft())
            elif self.active_handle == 'top-right':
                # Resize from top-right corner
                scale_x = max(0.1, (orig_width + dx) / orig_width)
                scale_y = max(0.1, (orig_height - dy) / orig_height)
                self.apply_scale_to_shape(scale_x, scale_y, QPointF(self.original_bounding_rect.right(), self.original_bounding_rect.top()))
            elif self.active_handle == 'bottom-left':
                # Resize from bottom-left corner
                scale_x = max(0.1, (orig_width - dx) / orig_width)
                scale_y = max(0.1, (orig_height + dy) / orig_height)
                self.apply_scale_to_shape(scale_x, scale_y, QPointF(self.original_bounding_rect.left(), self.original_bounding_rect.bottom()))
            elif self.active_handle == 'bottom-right':
                # Resize from bottom-right corner
                scale_x = max(0.1, (orig_width + dx) / orig_width)
                scale_y = max(0.1, (orig_height + dy) / orig_height)
                self.apply_scale_to_shape(scale_x, scale_y, self.original_bounding_rect.bottomRight())
            elif self.active_handle == 'top-center':
                # Resize vertically from top edge
                scale_y = max(0.1, (orig_height - dy) / orig_height)
                self.apply_scale_to_shape(1.0, scale_y, QPointF(self.original_bounding_rect.center().x(), self.original_bounding_rect.top()))
            elif self.active_handle == 'bottom-center':
                # Resize vertically from bottom edge
                scale_y = max(0.1, (orig_height + dy) / orig_height)
                self.apply_scale_to_shape(1.0, scale_y, QPointF(self.original_bounding_rect.center().x(), self.original_bounding_rect.bottom()))
            elif self.active_handle == 'left-center':
                # Resize horizontally from left edge
                scale_x = max(0.1, (orig_width - dx) / orig_width)
                self.apply_scale_to_shape(scale_x, 1.0, QPointF(self.original_bounding_rect.left(), self.original_bounding_rect.center().y()))
            elif self.active_handle == 'right-center':
                # Resize horizontally from right edge
                scale_x = max(0.1, (orig_width + dx) / orig_width)
                self.apply_scale_to_shape(scale_x, 1.0, QPointF(self.original_bounding_rect.right(), self.original_bounding_rect.center().y()))

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
            # Deselect any currently selected shape
            if self.selected_shape:
                self.selected_shape.is_selected = False
            self.selected_shape = None
            self.active_handle = None
            
            # Check if clicked on a handle of a selected shape
            if self.selected_shape and self.selected_shape.is_selected:
                self.active_handle = self.get_handle_at_position(self.selected_shape, pos)
                if self.active_handle:
                    self.drag_start_pos = pos
                    self.original_shape_points = [QPointF(p) for p in self.selected_shape.points]
                    if hasattr(self.selected_shape, 'end_pos'):
                        self.original_shape_end_pos = QPointF(self.selected_shape.end_pos)
                    self.original_bounding_rect = self.calculate_shape_bounding_rect(self.selected_shape)
                else:
                    # Check if clicked on any shape
                    for s in reversed(self.shapes):
                        if self.is_point_in_shape(s, pos):
                            self.selected_shape = s
                            s.is_selected = True
                            self.last_pos = pos
                            break
            else:
                # Check if clicked on any shape
                for s in reversed(self.shapes):
                    if self.is_point_in_shape(s, pos):
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
                        else:
                            self.last_pos = pos
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
                self.current_shape = TutorShape(self.mode, pos, self.current_color, self.default_thickness)
                self.current_shape.text_bounds = self.get_text_bounds(text_shape)
            else:
                # Free-form highlighter drawing
                self.current_shape = TutorShape(self.mode, pos, self.current_color, self.default_thickness)
        else:
            self.current_shape = TutorShape(self.mode, pos, self.current_color, self.default_thickness)
            if self.enable_fill and self.mode in ["rect", "ellipse", "diamond"]:
                self.current_shape.fill_color = self.current_color
        
        self.update()

    def mouseMoveEvent(self, event):
        if self.mode == "mouse":
            return
            
        pos = event.pos()
        
        if self.mode == "select" and self.selected_shape:
            if self.active_handle:
                # Handle resizing and transformation
                if self.active_handle == 'move':
                    # Moving the shape
                    delta = pos - self.last_pos
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
            if self.selected_shape:
                self.selected_shape.is_selected = False
                self.selected_shape = None
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

    def is_point_in_shape(self, shape, point):
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

    def keyPressEvent(self, event):
        key = event.text().upper()
        for mode, shortcut in self.shortcuts.items():
            if key == shortcut:
                self.set_mode(mode)
                return
        
        if event.key() == Qt.Key_Escape:
            QApplication.instance().quit()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.undo()
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            self.redo()

    def apply_theme(self, theme_name):
        """Apply the specified theme to the canvas and all components"""
        self.current_theme = theme_name
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