from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QApplication, QSlider, QComboBox
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QFont
import time

class InteractiveCaptureControls(QWidget):
    """Enhanced interactive capture controls with real-time options"""
    
    # Signals
    start_capture = pyqtSignal(str, object)  # mode, area
    pause_capture = pyqtSignal()
    resume_capture = pyqtSignal()
    stop_capture = pyqtSignal()
    save_capture = pyqtSignal()
    cancel_capture = pyqtSignal()
    scroll_speed_changed = pyqtSignal(int)
    capture_mode_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # State tracking
        self.is_capturing = False
        self.is_paused = False
        self.current_mode = "scrolling"
        self.captured_sections = 0
        self.start_time = time.time()
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Setup the interactive UI"""
        # Main container
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 40, 230);
                border-radius: 12px;
                border: 2px solid #6965db;
            }
        """)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # Header with title and status
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("_CAPTURE CONTROLS_", self)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #6965db;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        header_layout.addWidget(self.title_label)
        
        self.status_label = QLabel("READY", self)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #88ff88;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
                background-color: rgba(0, 100, 0, 100);
                border-radius: 8px;
            }
        """)
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:", self))
        
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems(["Scrolling", "Area", "Window", "Full Screen", "Code Editor"])
        self.mode_combo.setCurrentText("Scrolling")
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #444444;
                color: white;
                border: 1px solid #666666;
                border-radius: 6px;
                padding: 5px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #888888;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)
        
        # Scroll speed control (only for scrolling mode)
        self.speed_layout = QHBoxLayout()
        self.speed_layout.addWidget(QLabel("Scroll Speed:", self))
        
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #444444;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6965db;
                border: 1px solid #555555;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
        """)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        self.speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("5", self)
        self.speed_label.setStyleSheet("color: white; min-width: 20px;")
        self.speed_layout.addWidget(self.speed_label)
        self.speed_layout.addStretch()
        main_layout.addLayout(self.speed_layout)
        
        # Progress info
        self.progress_layout = QHBoxLayout()
        self.progress_label = QLabel("Sections: 0", self)
        self.progress_label.setStyleSheet("color: #aaaaaa;")
        self.progress_layout.addWidget(self.progress_label)
        
        self.timer_label = QLabel("00:00", self)
        self.timer_label.setStyleSheet("color: white; font-family: monospace; font-size: 14px;")
        self.progress_layout.addWidget(self.timer_label)
        self.progress_layout.addStretch()
        main_layout.addLayout(self.progress_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        # Start/Stop button
        self.start_stop_btn = QPushButton("Start Capture", self)
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.start_stop_btn.clicked.connect(self.toggle_capture)
        button_layout.addWidget(self.start_stop_btn)
        
        # Pause/Resume button
        self.pause_resume_btn = QPushButton("Pause", self)
        self.pause_resume_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.pause_resume_btn.clicked.connect(self.toggle_pause)
        self.pause_resume_btn.setEnabled(False)
        button_layout.addWidget(self.pause_resume_btn)
        
        # Save button
        self.save_btn = QPushButton("Save", self)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.save_btn.clicked.connect(self.save_capture.emit)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_capture.emit)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set container size and position
        self.container.setFixedSize(400, 220)
        self.setFixedSize(400, 220)
        
        # Position at bottom right
        screen_geo = QApplication.primaryScreen().geometry()
        self.move(screen_geo.bottomRight() - QPoint(self.width() + 20, self.height() + 20))
        
    def setup_timer(self):
        """Setup the capture timer"""
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.update_timer)
        
    def toggle_capture(self):
        """Toggle start/stop capture"""
        if not self.is_capturing:
            self.start_capture_process()
        else:
            self.stop_capture_process()
            
    def start_capture_process(self):
        """Start the capture process"""
        self.is_capturing = True
        self.is_paused = False
        
        # Update UI
        self.start_stop_btn.setText("Stop Capture")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        self.pause_resume_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.status_label.setText("CAPTURING")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
                background-color: rgba(255, 0, 0, 100);
                border-radius: 8px;
            }
        """)
        
        # Start timer
        self.start_time = time.time()
        self.capture_timer.start(1000)
        
        # Emit signal
        self.start_capture.emit(self.current_mode.lower().replace(" ", "_"), None)
        
    def stop_capture_process(self):
        """Stop the capture process"""
        self.is_capturing = False
        self.is_paused = False
        
        # Update UI
        self.start_stop_btn.setText("Start Capture")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.pause_resume_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.pause_resume_btn.setText("Pause")
        self.status_label.setText("COMPLETE")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6bff8c;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
                background-color: rgba(0, 150, 0, 100);
                border-radius: 8px;
            }
        """)
        
        # Stop timer
        self.capture_timer.stop()
        
        # Emit signal
        self.stop_capture.emit()
        
    def toggle_pause(self):
        """Toggle pause/resume"""
        if not self.is_capturing:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_resume_btn.setText("Resume")
            self.status_label.setText("PAUSED")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffd93d;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 2px 8px;
                    background-color: rgba(255, 217, 61, 100);
                    border-radius: 8px;
                }
            """)
            self.capture_timer.stop()
            self.pause_capture.emit()
        else:
            self.pause_resume_btn.setText("Pause")
            self.status_label.setText("CAPTURING")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 2px 8px;
                    background-color: rgba(255, 0, 0, 100);
                    border-radius: 8px;
                }
            """)
            self.capture_timer.start(1000)
            self.resume_capture.emit()
            
    def on_mode_changed(self, mode):
        """Handle mode change"""
        self.current_mode = mode
        self.capture_mode_changed.emit(mode.lower().replace(" ", "_"))
        
        # Show/hide speed control based on mode
        if mode == "Scrolling":
            self.speed_layout.parent().layout().insertLayout(2, self.speed_layout)  # Re-add if removed
        else:
            # Remove speed layout for non-scrolling modes
            pass
            
    def on_speed_changed(self, value):
        """Handle scroll speed change"""
        self.speed_label.setText(str(value))
        self.scroll_speed_changed.emit(value)
        
    def update_timer(self):
        """Update the timer display"""
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        
    def update_progress(self, sections):
        """Update capture progress"""
        self.captured_sections = sections
        self.progress_label.setText(f"Sections: {sections}")
        
    def reset_controls(self):
        """Reset all controls to initial state"""
        self.is_capturing = False
        self.is_paused = False
        self.captured_sections = 0
        
        # Reset UI
        self.start_stop_btn.setText("Start Capture")
        self.pause_resume_btn.setText("Pause")
        self.status_label.setText("READY")
        self.progress_label.setText("Sections: 0")
        self.timer_label.setText("00:00")
        
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.status_label.setStyleSheet("""
            QLabel {
                color: #88ff88;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
                background-color: rgba(0, 100, 0, 100);
                border-radius: 8px;
            }
        """)
        
        self.pause_resume_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.capture_timer.stop()