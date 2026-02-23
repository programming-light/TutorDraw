from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QApplication, QStyle, QFrame, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPixmap, QPen, QFont

class CaptureControlsWindow(QWidget):
    """Enhanced capture controls with visual indicators and smart scrolling functionality"""
    
    capture_started = pyqtSignal()
    capture_paused = pyqtSignal()
    capture_resumed = pyqtSignal()
    capture_stopped = pyqtSignal()
    capture_saved = pyqtSignal()
    
    def __init__(self, canvas_instance, parent=None):
        super().__init__(parent)
        self.canvas = canvas_instance
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 80)
        
        # Position at bottom right corner
        screen_geo = QApplication.primaryScreen().geometry()
        self.move(screen_geo.bottomRight() - QPoint(self.width() + 20, self.height() + 20))
        
        # Capture state tracking
        self.is_capturing = False
        self.is_paused = False
        self.capture_mode = "idle"  # idle, scrolling, area, fullscreen
        self.captured_sections = []
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Setup the enhanced UI with visual capture indicators"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Background frame
        self.bg_frame = QFrame(self)
        self.bg_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 40, 220);
                border-radius: 15px;
                border: 2px solid #6965db;
            }
        """)
        
        controls_layout = QHBoxLayout(self.bg_frame)
        controls_layout.setContentsMargins(15, 10, 15, 10)
        controls_layout.setSpacing(12)
        
        # Capture status indicator
        self.status_indicator = QLabel("○ IDLE", self)
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #888888;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
        """)
        controls_layout.addWidget(self.status_indicator)
        
        # Capture mode indicator
        self.mode_label = QLabel("Mode: None", self)
        self.mode_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
                min-width: 90px;
            }
        """)
        controls_layout.addWidget(self.mode_label)
        
        # Timer display
        self.timer_label = QLabel("00:00", self)
        self.timer_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                font-family: monospace;
                min-width: 50px;
            }
        """)
        controls_layout.addWidget(self.timer_label)
        
        # Control buttons
        button_style = """
            QPushButton {
                background-color: #444444;
                border: 1px solid #666666;
                border-radius: 8px;
                width: 32px;
                height: 32px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #555555;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """
        
        # Pause/Resume button
        self.pause_btn = QPushButton("⏸", self)
        self.pause_btn.setStyleSheet(button_style)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)
        
        # Save button
        self.save_btn = QPushButton("💾", self)
        self.save_btn.setStyleSheet(button_style)
        self.save_btn.clicked.connect(self.save_capture)
        self.save_btn.setEnabled(False)
        controls_layout.addWidget(self.save_btn)
        
        # Stop button
        self.stop_btn = QPushButton("⏹", self)
        self.stop_btn.setStyleSheet(button_style)
        self.stop_btn.clicked.connect(self.stop_capture)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        main_layout.addWidget(self.bg_frame)
        self.setLayout(main_layout)
        
    def setup_timer(self):
        """Setup capture timer"""
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.update_timer)
        self.capture_time = QTime(0, 0)
        
    def start_capture(self, mode="scrolling"):
        """Start capture with specified mode"""
        self.is_capturing = True
        self.is_paused = False
        self.capture_mode = mode
        self.captured_sections = []
        
        # Update UI
        self.update_status("● CAPTURING", "#ff6b6b")
        self.mode_label.setText(f"Mode: {mode.title()}")
        self.pause_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setText("⏸")
        
        # Start timer
        self.capture_time = QTime(0, 0)
        self.capture_timer.start(1000)
        
        # Emit signal
        self.capture_started.emit()
        
        print(f"📸 Capture started in {mode} mode")
        
    def toggle_pause(self):
        """Toggle pause/resume capture"""
        if not self.is_capturing:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.update_status("⏸ PAUSED", "#ffd93d")
            self.pause_btn.setText("▶")
            self.capture_timer.stop()
            self.capture_paused.emit()
            print("⏸ Capture paused")
        else:
            self.update_status("● CAPTURING", "#ff6b6b")
            self.pause_btn.setText("⏸")
            self.capture_timer.start(1000)
            self.capture_resumed.emit()
            print("▶ Capture resumed")
            
    def save_capture(self):
        """Save current capture"""
        if not self.is_capturing:
            return
            
        self.capture_saved.emit()
        print("💾 Capture saved")
        
        # Brief visual feedback
        original_text = self.status_indicator.text()
        self.update_status("✓ SAVED", "#6bff8c")
        QTimer.singleShot(1000, lambda: self.update_status(original_text, "#ff6b6b"))
        
    def stop_capture(self):
        """Stop capture completely"""
        self.is_capturing = False
        self.is_paused = False
        self.capture_mode = "idle"
        
        # Update UI
        self.update_status("○ IDLE", "#888888")
        self.mode_label.setText("Mode: None")
        self.timer_label.setText("00:00")
        self.pause_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setText("⏸")
        
        # Stop timer
        self.capture_timer.stop()
        
        # Emit signal
        self.capture_stopped.emit()
        
        print("⏹ Capture stopped")
        
    def update_status(self, text, color):
        """Update status indicator with text and color"""
        self.status_indicator.setText(text)
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }}
        """)
        
    def update_timer(self):
        """Update capture timer display"""
        self.capture_time = self.capture_time.addSecs(1)
        time_str = self.capture_time.toString("mm:ss")
        self.timer_label.setText(time_str)
        
    def add_captured_section(self, section_info):
        """Add information about captured section"""
        self.captured_sections.append(section_info)
        print(f"📄 Captured section {len(self.captured_sections)}: {section_info}")
        
    def get_captured_sections(self):
        """Get list of all captured sections"""
        return self.captured_sections.copy()