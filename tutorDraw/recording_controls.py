from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QApplication, QStyle, QStyleOptionButton, QFrame
from PySide6.QtCore import Qt, QTimer, QTime, QPoint
from PySide6.QtGui import QColor, QPainter, QPixmap, QPen

class RecordingControlsWindow(QWidget):
    def __init__(self, canvas_instance, parent=None):
        super().__init__(parent)
        self.canvas = canvas_instance
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(250, 60) # Adjusted size for cleaner look
        self.move(QApplication.primaryScreen().geometry().bottomRight() - QPoint(self.width() + 20, self.height() + 20)) # Bottom right corner

        self.recording_started_time = QTime()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5) # Smaller margins

        # Background frame for styling
        self.bg_frame = QFrame(self)
        self.bg_frame.setStyleSheet("background-color: rgba(40, 40, 40, 200); border-radius: 15px;")
        
        # Inner layout for controls
        controls_layout = QHBoxLayout(self.bg_frame)
        controls_layout.setContentsMargins(10, 5, 10, 5)
        controls_layout.setSpacing(10)

        # Record indicator
        self.record_indicator = QLabel("● REC", self)
        self.record_indicator.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        controls_layout.addWidget(self.record_indicator)

        # Timer label
        self.timer_label = QLabel("00:00:00", self)
        self.timer_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        controls_layout.addWidget(self.timer_label)

        # Start/Pause Button
        self.start_pause_button = QPushButton("", self)
        self.start_pause_button.clicked.connect(self._toggle_pause_resume)
        self._set_button_icon(self.start_pause_button, QStyle.SP_MediaPause)
        self.start_pause_button.setStyleSheet("background-color: #555; border-radius: 5px; width: 30px; height: 30px;")
        controls_layout.addWidget(self.start_pause_button)

        # Stop Button
        self.stop_button = QPushButton("", self)
        self.stop_button.clicked.connect(self.canvas.stop_recording_action)
        self._set_button_icon(self.stop_button, QStyle.SP_MediaStop)
        self.stop_button.setStyleSheet("background-color: #555; border-radius: 5px; width: 30px; height: 30px;")
        controls_layout.addWidget(self.stop_button)

        main_layout.addWidget(self.bg_frame)
        self.setLayout(main_layout)

        self.start_timer()

    def _set_button_icon(self, button, icon_enum):
        icon = self.style().standardIcon(icon_enum)
        button.setIcon(icon)

    def _toggle_pause_resume(self):
        if self.canvas.recorder:
            if self.canvas.recorder.is_paused:
                self.canvas.resume_recording_action()
                self._set_button_icon(self.start_pause_button, QStyle.SP_MediaPause) # Show pause icon
                self.record_indicator.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
                self.timer.start(1000)
            else:
                self.canvas.pause_recording_action()
                self._set_button_icon(self.start_pause_button, QStyle.SP_MediaPlay) # Show play icon
                self.record_indicator.setStyleSheet("color: gray; font-weight: bold; font-size: 14px;") # Grey out when paused
                self.timer.stop()

    def start_timer(self):
        self.recording_started_time.start()
        self.timer.start(1000) # Update every second
        self._set_button_icon(self.start_pause_button, QStyle.SP_MediaPause) # Start with pause icon

    def update_timer_display(self):
        elapsed_seconds = self.recording_started_time.elapsed() / 1000
        hours, remainder = divmod(int(elapsed_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
        super().mousePressEvent(event) # Call base class method to ensure default behavior

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event) # Call base class method
