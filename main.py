import sys
import time
import random
import math
import os
import json
from collections import deque
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QPushButton, QFrame, 
    QGraphicsDropShadowEffect, QVBoxLayout, QLabel, QDialog, 
    QKeySequenceEdit, QColorDialog, QMenu, QRubberBand, QLineEdit, QSlider
)
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, QPoint, QSize, QRect
from PySide6.QtGui import (
    QPainter, QPen, QColor, QPainterPath, QCursor, QPixmap, QKeySequence, QAction, QFont
)

# --- Configuration ---
CONFIG_FILE = "tutordraw_settings.json"
LOGO_FILE = "tutorDraw-logoX92.png" 
EXCALI_PURPLE = "#6965db"
EXCALI_LIGHT = "#ececfd"

# --- DATA CLASS ---

class TutorShape:
    def __init__(self, mode, start_pos, color, text=""):
        self.mode = mode
        self.points = [start_pos]
        self.end_pos = start_pos
        self.color = QColor(color)
        self.text = text
        self.seed = random.randint(0, 1000)
        self.is_selected = False

    def move_by(self, delta):
        self.points = [p + delta for p in self.points]
        self.end_pos += delta

# --- UI COMPONENTS ---

class SettingsDialog(QDialog):
    """Refined configuration panel with Close (X) button"""
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 680)
        
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(10, 10, 430, 660)
        self.main_frame.setStyleSheet("""
            QFrame { background-color: white; border: 1px solid #ddd; border-radius: 20px; }
            QLabel { color: #1e1e1e; font-family: 'Segoe UI'; font-weight: 600; border: none; font-size: 13px; }
            QKeySequenceEdit { background: #f8f9fa; color: black; padding: 6px; border-radius: 8px; border: 1px solid #ccc; }
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; color: #6965db; font-weight: 800;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("background: #ffefef; color: #ff5f5f; border-radius: 16px; font-weight: bold; border: none;")
        close_btn.clicked.connect(self.reject)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        # Shortcuts
        layout.addWidget(QLabel("KEYBOARD SHORTCUTS"))
        for action, key in self.canvas.shortcuts.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(action.title()))
            ks = QKeySequenceEdit(QKeySequence(key))
            ks.editingFinished.connect(lambda a=action, k=ks: self.update_shortcut(a, k))
            row.addWidget(ks)
            layout.addLayout(row)

        layout.addSpacing(15)
        layout.addWidget(QLabel("LASER POINTER CONFIG"))
        
        # Laser Thickness
        self.lbl_t = QLabel(f"Thickness: {self.canvas.laser_thickness}px")
        layout.addWidget(self.lbl_t)
        t_slider = QSlider(Qt.Horizontal)
        t_slider.setRange(2, 50); t_slider.setValue(self.canvas.laser_thickness)
        t_slider.valueChanged.connect(self.update_thickness); layout.addWidget(t_slider)

        # Laser Duration
        self.lbl_d = QLabel(f"Duration: {self.canvas.laser_duration}s")
        layout.addWidget(self.lbl_d)
        d_slider = QSlider(Qt.Horizontal)
        d_slider.setRange(5, 100); d_slider.setValue(int(self.canvas.laser_duration * 10))
        d_slider.valueChanged.connect(self.update_duration); layout.addWidget(d_slider)

        # Laser Color
        row_c = QHBoxLayout()
        row_c.addWidget(QLabel("Laser Color:"))
        self.c_btn = QPushButton()
        self.c_btn.setFixedSize(40, 25); self.c_btn.setCursor(Qt.PointingHandCursor)
        self.c_btn.setStyleSheet(f"background: {self.canvas.laser_color}; border-radius: 5px; border: 1px solid #ccc;")
        self.c_btn.clicked.connect(self.pick_laser_color)
        row_c.addWidget(self.c_btn); layout.addLayout(row_c)

        layout.addStretch()
        save_btn = QPushButton("Save & Close")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("background: #6965db; color: white; border-radius: 10px; padding: 12px; font-weight: bold; border: none;")
        save_btn.clicked.connect(self.accept); layout.addWidget(save_btn)

    def update_shortcut(self, action, widget): self.canvas.shortcuts[action] = widget.keySequence().toString()
    def update_thickness(self, val): self.canvas.laser_thickness = val; self.lbl_t.setText(f"Thickness: {val}px")
    def update_duration(self, val): self.canvas.laser_duration = val / 10.0; self.lbl_d.setText(f"Duration: {self.canvas.laser_duration}s")
    def pick_laser_color(self):
        c = QColorDialog.getColor(QColor(self.canvas.laser_color), self, "Laser Color")
        if c.isValid():
            self.canvas.laser_color = c.name()
            self.c_btn.setStyleSheet(f"background: {c.name()}; border-radius: 5px; border: 1px solid #ccc;")

class HideHandle(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(50, 50) 
        self.logo = QPixmap(LOGO_FILE)
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255, 240))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 48, 48, 0, 15)
        if not self.logo.isNull():
            target = self.rect().adjusted(10, 10, -10, -10)
            painter.drawPixmap(target, self.logo.scaled(target.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def enterEvent(self, event): self.canvas.peek_toolbar()
    def mousePressEvent(self, event): self.canvas.restore_toolbar()

class IconButton(QPushButton):
    def __init__(self, text, tip="", shortcut="", checkable=True):
        super().__init__(text)
        self.setFixedSize(46, 46); self.setCheckable(checkable)
        self.setToolTip(f"{tip} [{shortcut}]" if shortcut else tip)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 12px; color: #1e1e1e; font-size: 24px; }}
            QPushButton:hover {{ background: #f0f0f0; }}
            QPushButton:checked {{ background: {EXCALI_LIGHT}; color: {EXCALI_PURPLE}; border: 1px solid {EXCALI_PURPLE}; }}
        """)

# --- MAIN APP ---

class TutorToolbar(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        self.bg = QFrame()
        self.bg.setStyleSheet("QFrame { background: white; border: 1px solid #d1d1d1; border-radius: 18px; }")
        shadow = QGraphicsDropShadowEffect(self); shadow.setBlurRadius(30); shadow.setColor(QColor(0,0,0,130)); shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        inner = QHBoxLayout(self.bg)
        inner.setContentsMargins(12, 6, 12, 6)

        self.logo_lbl = QLabel()
        pix = QPixmap(LOGO_FILE)
        if not pix.isNull(): self.logo_lbl.setPixmap(pix.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_lbl.setStyleSheet("border: none; background: transparent;")
        inner.addWidget(self.logo_lbl)
        
        inner.addSpacing(5)
        sep = QFrame(); sep.setFixedWidth(1); sep.setFixedHeight(25); sep.setStyleSheet("background: #eee;")
        inner.addWidget(sep); inner.addSpacing(5)

        self.btns = {}
        tools = [("🖱️", "mouse", "PC Interaction", "M"), ("↖", "select", "Move Object", "V"),
                 ("✎", "pencil", "Pencil", "P"), ("▢", "rect", "Rectangle", "R"),
                 ("◇", "diamond", "Diamond", "D"), ("○", "ellipse", "Ellipse", "E"),
                 ("→", "arrow", "Arrow", "A"), ("🔤", "text", "Text", "T"),
                 ("🪄", "laser", "Laser", "L"), ("🧽", "eraser", "Eraser", "X")]
        
        for icon, mode, tip, key in tools:
            btn = IconButton(icon, tip, key)
            btn.clicked.connect(lambda checked=False, m=mode: self.canvas.set_mode(m))
            inner.addWidget(btn); self.btns[mode] = btn

        # Color Palette Panel with explicit background color
        inner.addSpacing(10)
        self.pal_frame = QFrame()
        self.pal_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 12px; border: 1px solid #e0e0e0;")
        pal_lay = QHBoxLayout(self.pal_frame); pal_lay.setContentsMargins(4, 2, 4, 2)
        
        self.picker = QPushButton("🎨")
        self.picker.setFixedSize(36, 36); self.picker.setCursor(Qt.PointingHandCursor)
        self.picker.setStyleSheet("background: transparent; border: none; font-size: 22px;")
        self.picker.clicked.connect(self.canvas.open_color_picker)
        pal_lay.addWidget(self.picker)
        inner.addWidget(self.pal_frame); inner.addSpacing(10)

        self.clear_btn = IconButton("⌫", "Clear Screen", "C", False)
        self.clear_btn.clicked.connect(self.canvas.clear_canvas); inner.addWidget(self.clear_btn)
        
        conf_btn = IconButton("⚙️", "Settings", "", False)
        conf_btn.clicked.connect(self.canvas.open_settings); inner.addWidget(conf_btn)

        self.more_btn = IconButton("⋮", "More", "", False)
        self.more_btn.clicked.connect(self.show_more_menu); inner.addWidget(self.more_btn)
        layout.addWidget(self.bg)

    def mousePressEvent(self, event): self.oldPos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y()); self.oldPos = event.globalPosition().toPoint()

    def show_more_menu(self):
        menu = QMenu(self); menu.addAction("🙈 Hide Toolbar").triggered.connect(self.canvas.hide_toolbar_permanent)
        menu.addSeparator(); menu.addAction("❌ Exit").triggered.connect(QApplication.instance().quit); menu.exec(QCursor.pos())

class TutorCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground); self.setAttribute(Qt.WA_NoSystemBackground)
        self.setGeometry(QApplication.primaryScreen().geometry())
        
        # State
        self.mode = "pencil"; self.current_color = "#90EE90"
        self.laser_color = "#FF1E1E"; self.laser_thickness = 14; self.laser_duration = 1.5
        self.shapes = []; self.current_shape = None; self.selected_shape = None; self.input_box = None
        self.is_hidden = False; self.laser_trails = []
        
        self.shortcuts = {"mouse": "M", "select": "V", "pencil": "P", "rect": "R", "diamond": "D", "ellipse": "E", "arrow": "A", "text": "T", "laser": "L", "eraser": "X", "clear": "C"}
        self.load_config()

        self.toolbar = TutorToolbar(self); self.hide_handle = HideHandle(self)
        self.toolbar.show(); self.toolbar.move((self.width() - 1100) // 2, 60)
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_canvas); self.timer.start(12)
        self.set_mode("pencil"); self.show()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    d = json.load(f); self.shortcuts.update(d.get("shortcuts", {}))
                    self.laser_color = d.get("laser_color", self.laser_color)
                    self.laser_thickness = d.get("laser_thickness", self.laser_thickness)
                    self.laser_duration = d.get("laser_duration", self.laser_duration)
            except: pass

    def save_config(self):
        with open(CONFIG_FILE, "w") as f: json.dump({"shortcuts": self.shortcuts, "laser_color": self.laser_color, "laser_thickness": self.laser_thickness, "laser_duration": self.laser_duration}, f)

    def hide_toolbar_permanent(self): self.is_hidden = True; self.toolbar.hide(); self.hide_handle.move(0, 0); self.hide_handle.show()
    def peek_toolbar(self):
        if self.is_hidden: self.toolbar.show(); self.toolbar.raise_()
    def restore_toolbar(self): self.is_hidden = False; self.hide_handle.hide(); self.toolbar.show()

    def set_mode(self, mode):
        self.mode = mode
        if mode != "text" and self.input_box: self.finish_text(self.input_box_pos)
        self.setWindowFlag(Qt.WindowTransparentForInput, mode == "mouse")
        self.setCursor(Qt.ArrowCursor if mode in ["mouse", "select"] else Qt.CrossCursor)
        if mode == "laser": self.setCursor(Qt.BlankCursor)
        self.hide(); self.show()
        for m, btn in self.toolbar.btns.items():
            if btn.isCheckable(): btn.setChecked(m == mode)
        self.toolbar.raise_()

    def open_color_picker(self):
        d = QColorDialog(QColor(self.current_color), self); d.setWindowFlags(Qt.WindowStaysOnTopHint)
        if d.exec() == QColorDialog.Accepted: self.current_color = d.selectedColor().name()

    def open_text_input(self, pos):
        if self.input_box: self.finish_text(self.input_box_pos)
        self.input_box_pos = pos; self.input_box = QLineEdit(self)
        self.input_box.setStyleSheet(f"border: 1px dashed {EXCALI_PURPLE}; background: white; color: {self.current_color}; font-size: 20px;")
        self.input_box.move(pos.toPoint()); self.input_box.show(); self.input_box.setFocus()
        self.input_box.editingFinished.connect(lambda: self.finish_text(pos))

    def finish_text(self, pos):
        if self.input_box:
            txt = self.input_box.text()
            if txt.strip(): self.shapes.append(TutorShape("text", pos, self.current_color, txt))
            self.input_box.deleteLater(); self.input_box = None; self.update()

    def clear_canvas(self):
        self.shapes = []; self.laser_trails = []
        if self.input_box: self.input_box.deleteLater(); self.input_box = None
        self.update()

    def open_settings(self):
        if SettingsDialog(self, self).exec(): self.save_config()

    def update_canvas(self):
        if self.is_hidden and self.toolbar.isVisible() and not self.toolbar.underMouse() and not self.hide_handle.underMouse():
            self.toolbar.hide()
        now = time.monotonic()
        for trail in self.laser_trails[:]:
            while trail and (now - trail[0][1] > self.laser_duration): trail.popleft()
            if not trail: self.laser_trails.remove(trail)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        for s in self.shapes + ([self.current_shape] if self.current_shape else []):
            if not s: continue
            w = 6 if s.is_selected else 4; painter.setPen(QPen(s.color, w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            if s.mode == "pencil":
                path = QPainterPath()
                if len(s.points) > 1:
                    path.moveTo(s.points[0])
                    for i in range(1, len(s.points)): path.quadTo(s.points[i-1], (s.points[i-1]+s.points[i])/2)
                    path.lineTo(s.points[-1]); painter.drawPath(path)
            elif s.mode == "text":
                painter.setFont(QFont("Segoe Print", 22)); painter.drawText(s.points[0], s.text)
            elif s.mode == "rect": painter.drawRect(QRectF(s.points[0], s.end_pos).normalized())
            elif s.mode == "ellipse": painter.drawEllipse(QRectF(s.points[0], s.end_pos).normalized())
            elif s.mode == "diamond":
                r = QRectF(s.points[0], s.end_pos).normalized()
                painter.drawPolygon([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()), QPointF(r.center().x(), r.bottom()), QPointF(r.left(), r.center().y())])
            elif s.mode == "arrow":
                p1, p2 = s.points[0], s.end_pos; painter.drawLine(p1, p2)
                angle = math.atan2(p2.y()-p1.y(), p2.x()-p1.x())
                painter.drawLine(p2, QPointF(p2.x()-20*math.cos(angle-0.4), p2.y()-20*math.sin(angle-0.4)))
                painter.drawLine(p2, QPointF(p2.x()-20*math.cos(angle+0.4), p2.y()-20*math.sin(angle+0.4)))

        # Liquid Laser
        now = time.monotonic()
        for trail in self.laser_trails:
            if len(trail) < 2: continue
            for i in range(1, len(trail)):
                p1, t1 = trail[i-1]; p2, t2 = trail[i]; age = (now - t2) / self.laser_duration
                alpha, size = max(0, int(255 * (1 - age))), max(0.1, self.laser_thickness * (1 - age)) 
                if alpha > 5:
                    painter.setPen(QPen(QColor(QColor(self.laser_color).red(), QColor(self.laser_color).green(), QColor(self.laser_color).blue(), alpha), size, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin))
                    painter.drawLine(p1, p2)
            painter.setPen(Qt.NoPen); painter.setBrush(QColor(self.laser_color)); painter.drawEllipse(trail[-1][0], self.laser_thickness/2.5, self.laser_thickness/2.5)

    def mousePressEvent(self, event):
        if self.toolbar.geometry().contains(event.globalPosition().toPoint()): return
        if self.mode == "mouse": return
        pos = event.position()
        if self.mode == "select":
            self.selected_shape = None
            for s in reversed(self.shapes):
                if (s.points[0] - pos).manhattanLength() < 60 or (s.end_pos - pos).manhattanLength() < 60:
                    self.selected_shape = s; s.is_selected = True; break
            self.last_pos = pos
        elif self.mode == "text": self.open_text_input(pos)
        elif self.mode == "laser":
            t = deque(); t.append((pos, time.monotonic())); self.laser_trails.append(t)
        elif self.mode == "eraser": self.erase_at(pos)
        else: self.current_shape = TutorShape(self.mode, pos, self.current_color)
        self.update()

    def mouseMoveEvent(self, event):
        if self.mode == "mouse": return
        pos = event.position()
        if self.mode == "select" and self.selected_shape:
            self.selected_shape.move_by(pos - self.last_pos); self.last_pos = pos
        elif self.mode == "laser" and self.laser_trails:
            if (pos - self.laser_trails[-1][-1][0]).manhattanLength() > 2: self.laser_trails[-1].append((pos, time.monotonic()))
        elif self.mode == "eraser": self.erase_at(pos)
        elif self.current_shape:
            if self.mode == "pencil": self.current_shape.points.append(pos)
            self.current_shape.end_pos = pos
        self.update()

    def erase_at(self, pos):
        self.shapes = [s for s in self.shapes if not any((QPointF(p) - pos).manhattanLength() < 35 for p in (s.points if s.mode=="pencil" else [s.points[0], s.end_pos]))]
        self.update()

    def mouseReleaseEvent(self, event):
        if self.current_shape: self.shapes.append(self.current_shape); self.current_shape = None
        if self.selected_shape: self.selected_shape.is_selected = False; self.selected_shape = None
        self.update(); self.toolbar.raise_()

    def keyPressEvent(self, event):
        try: mod = event.modifiers().value
        except: mod = int(event.modifiers())
        key_str = QKeySequence(event.key() | mod).toString()
        for action, mapped in self.shortcuts.items():
            if key_str == mapped:
                if action == "clear": self.clear_canvas()
                else: self.set_mode(action)
                return
        if event.key() == Qt.Key_Escape: QApplication.instance().quit()

if __name__ == "__main__":
    app = QApplication(sys.argv); canvas = TutorCanvas(); sys.exit(app.exec())