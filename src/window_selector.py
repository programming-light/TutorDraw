from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QApplication, QDesktopWidget
from PyQt5.QtGui import QScreen
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QPixmap, QRegion, QScreen
import pyautogui
import time

class WindowSelector(QWidget):
    """Interactive window selection tool"""
    
    window_selected = pyqtSignal(QRect)
    selection_cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        # Get all screens
        self.screens = QApplication.screens()
        self.screen_geometries = [screen.geometry() for screen in self.screens]
        
        # Combined geometry covering all screens
        self.combined_geometry = self.get_combined_screen_geometry()
        self.setGeometry(self.combined_geometry)
        
        # Selection state
        self.is_selecting = False
        self.start_pos = None
        self.current_pos = None
        self.selected_window = None
        self.highlighted_window = None
        
        # Window detection
        self.detected_windows = self.detect_windows()
        
        # Instructions
        self.instruction_label = QLabel("Click and drag to select area, or click a window to capture it", self)
        self.instruction_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.instruction_label.move(50, 50)
        self.instruction_label.show()
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 180);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 50, 50, 200);
            }
        """)
        self.cancel_btn.move(self.width() - 100, 50)
        self.cancel_btn.clicked.connect(self.cancel_selection)
        self.cancel_btn.show()
        
    def get_combined_screen_geometry(self):
        """Get geometry that covers all screens"""
        if not self.screen_geometries:
            return QRect(0, 0, 1920, 1080)
            
        min_x = min(screen.x() for screen in self.screen_geometries)
        min_y = min(screen.y() for screen in self.screen_geometries)
        max_x = max(screen.x() + screen.width() for screen in self.screen_geometries)
        max_y = max(screen.y() + screen.height() for screen in self.screen_geometries)
        
        return QRect(min_x, min_y, max_x - min_x, max_y - min_y)
        
    def detect_windows(self):
        """Detect visible windows (simplified implementation)"""
        try:
            # This is a simplified version - in practice, you'd use platform-specific APIs
            # For Windows: win32gui.EnumWindows
            # For macOS: Quartz.CGWindowListCreate
            # For Linux: X11 functions
            
            windows = []
            # Get active window position as example
            try:
                active_window = pyautogui.getActiveWindow()
                if active_window:
                    windows.append({
                        'title': active_window.title,
                        'geometry': QRect(
                            active_window.left, 
                            active_window.top, 
                            active_window.width, 
                            active_window.height
                        ),
                        'handle': active_window._hWnd if hasattr(active_window, '_hWnd') else None
                    })
            except:
                pass
                
            return windows
        except Exception as e:
            print(f"Window detection error: {e}")
            return []
            
    def paintEvent(self, event):
        """Draw overlay with window highlights"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # Draw detected windows
        for window in self.detected_windows:
            geometry = window['geometry']
            
            # Highlight color based on state
            if window == self.highlighted_window:
                color = QColor(0, 255, 0, 100)  # Green for highlighted
                border_color = QColor(0, 255, 0, 255)
            else:
                color = QColor(100, 150, 255, 80)  # Blue for normal
                border_color = QColor(100, 150, 255, 200)
            
            # Fill window area
            painter.fillRect(geometry, color)
            
            # Draw border
            painter.setPen(QPen(border_color, 2))
            painter.drawRect(geometry)
            
            # Draw window title
            if window['title']:
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(geometry.adjusted(5, 5, -5, -5), 
                               Qt.AlignTop | Qt.AlignLeft, 
                               window['title'][:30] + "..." if len(window['title']) > 30 else window['title'])
        
        # Draw selection rectangle
        if self.is_selecting and self.start_pos and self.current_pos:
            rect = QRect(self.start_pos, self.current_pos)
            painter.setPen(QPen(QColor(255, 255, 0), 2, Qt.DashLine))
            painter.drawRect(rect)
            
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.current_pos = event.pos()
            self.is_selecting = True
            
            # Check if clicked on a window
            clicked_window = self.get_window_at_position(event.pos())
            if clicked_window:
                self.select_window(clicked_window)
                return
                
    def mouseMoveEvent(self, event):
        """Handle mouse movement for selection"""
        self.current_pos = event.pos()
        
        # Update highlighted window
        highlighted = self.get_window_at_position(event.pos())
        if highlighted != self.highlighted_window:
            self.highlighted_window = highlighted
            self.update()
            
        if self.is_selecting:
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release to complete selection"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            
            # If we have a selection rectangle
            if self.start_pos and self.current_pos:
                selection_rect = QRect(self.start_pos, self.current_pos).normalized()
                if selection_rect.width() > 10 and selection_rect.height() > 10:
                    self.window_selected.emit(selection_rect)
                    self.close()
                    return
                    
            # Reset if no valid selection
            self.start_pos = None
            self.current_pos = None
            self.update()
            
    def get_window_at_position(self, pos):
        """Get window at specific position"""
        for window in self.detected_windows:
            if window['geometry'].contains(pos):
                return window
        return None
        
    def select_window(self, window):
        """Select a specific window"""
        self.window_selected.emit(window['geometry'])
        self.close()
        
    def cancel_selection(self):
        """Cancel the selection process"""
        self.selection_cancelled.emit()
        self.close()
        
    def keyPressEvent(self, event):
        """Handle escape key to cancel"""
        if event.key() == Qt.Key_Escape:
            self.cancel_selection()