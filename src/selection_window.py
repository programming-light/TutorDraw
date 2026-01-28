from PySide6.QtWidgets import QWidget, QApplication, QPushButton
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QPen, QColor

class SelectionWindow(QWidget):
    selection_made = Signal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.showFullScreen()
        
        self.origin = QPoint()
        self.current_rect = QRect()
        self.selecting = False
        
        self.setCursor(Qt.CrossCursor)

        # Add buttons for confirm and cancel
        self.confirm_button = QPushButton("Confirm (Enter)", self)
        self.confirm_button.setStyleSheet("background-color: green; color: white; padding: 10px;")
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.confirm_button.hide()

        self.cancel_button = QPushButton("Cancel (Esc)", self)
        self.cancel_button.setStyleSheet("background-color: red; color: white; padding: 10px;")
        self.cancel_button.clicked.connect(self.cancel_selection)
        self.cancel_button.hide()
        
        # Make sure key events are processed
        self.setFocusPolicy(Qt.StrongFocus)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.current_rect = QRect(self.origin, self.origin)
            self.selecting = True
            self.update()
            self.confirm_button.hide()
            self.cancel_button.hide()

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.current_rect = QRect(self.origin, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            self.current_rect = QRect(self.origin, event.pos()).normalized()
            self.update_button_positions()
            self.confirm_button.show()
            self.cancel_button.show()
        elif event.button() == Qt.RightButton:
            self.cancel_selection()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))  # Dim background
        
        if not self.current_rect.isNull():
            painter.setPen(QPen(QColor(255, 0, 0), 2)) # Red border
            painter.setBrush(QColor(0, 0, 0, 0)) # Transparent fill for selection area
            painter.drawRect(self.current_rect)
            
            # Clear the dimmed background from the selected area
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(self.current_rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.confirm_selection()
        elif event.key() == Qt.Key_Escape:
            self.cancel_selection()

    def confirm_selection(self):
        if not self.current_rect.isNull() and not self.current_rect.isEmpty():
            self.selection_made.emit(self.current_rect)
        self.close()

    def cancel_selection(self):
        self.selection_made.emit(QRect()) # Emit an empty QRect to signify cancellation
        self.close()

    def update_button_positions(self):
        if not self.current_rect.isNull():
            # Position buttons below the selection or at the bottom right if selection is small
            btn_width = self.confirm_button.width() + self.cancel_button.width() + 20 # 20 for spacing
            
            # Try to place below the selection
            x_pos = self.current_rect.right() - btn_width
            y_pos = self.current_rect.bottom() + 10 # 10 pixels below selection
            
            # If placing below goes off screen, try placing inside bottom right
            if y_pos + self.confirm_button.height() > self.height() or x_pos < 0:
                x_pos = self.current_rect.right() - btn_width - 10
                y_pos = self.current_rect.bottom() - self.confirm_button.height() - 10

            self.confirm_button.move(x_pos, y_pos)
            self.cancel_button.move(x_pos + self.confirm_button.width() + 10, y_pos)
        
        self.confirm_button.raise_()
        self.cancel_button.raise_()
