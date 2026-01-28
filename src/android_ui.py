"""
Android-specific UI module for TutorDraw
Implements the gallery/grid tool selection system when hide icon is clicked
"""
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QDialog, 
    QVBoxLayout, QScrollArea, QFrame, QScroller
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette


class ToolGalleryDialog(QDialog):
    """Modal dialog showing all tools in a grid/gallery format for Android"""
    
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setWindowTitle("Tool Gallery")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        
        # Set up the layout
        layout = QVBoxLayout()
        
        # Create scrollable grid area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.grid_layout = QGridLayout(scroll_widget)
        self.grid_layout.setAlignment(Qt.AlignCenter)
        
        # Define tools with their icons and descriptions
        self.tools = [
            ("🖱️", "mouse", "Mouse Control"),
            ("✎", "pencil", "Pencil"),
            ("▢", "rect", "Rectangle"),
            ("◇", "diamond", "Diamond"),
            ("○", "ellipse", "Ellipse"),
            ("→", "arrow", "Arrow"),
            ("🔤", "text", "Text"),
            ("🪄", "laser", "Laser Pointer"),
            ("🧽", "eraser", "Eraser"),
            ("↶", "undo", "Undo"),
            ("↷", "redo", "Redo"),
            ("◎", "transparency", "Transparency"),
            ("📊", "board", "Board Mode"),
            ("📷", "capture", "Capture"),
            ("⚙️", "settings", "Settings"),
        ]
        
        # Create tool buttons in a grid (3 columns)
        for i, (icon, mode, description) in enumerate(self.tools):
            row = i // 3
            col = i % 3
            
            btn = QPushButton(icon)
            btn.setToolTip(description)
            btn.setFixedSize(100, 100)  # Larger for touch
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 32px;
                    border: 2px solid #ccc;
                    border-radius: 15px;
                    background: white;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                    border: 2px solid #aaa;
                }
                QPushButton:pressed {
                    background: #e0e0e0;
                }
            """)
            
            # Connect to tool selection
            btn.clicked.connect(lambda checked=False, m=mode: self.select_tool(m))
            self.grid_layout.addWidget(btn, row, col)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(scroll_area)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background: #f0f0f0;
            }
            QPushButton:pressed {
                background: #d0d0d0;
            }
        """)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.resize(350, 500)
        
        # Apply theme if available
        if hasattr(self.canvas, 'theme') and self.canvas.theme:
            theme = self.canvas.theme
            bg_color = QColor(255, 255, 255, 230) if 'light' in theme.get('name', 'light') else QColor(40, 40, 40, 230)
            self.setStyleSheet(f"background-color: {bg_color.name()}; border: 1px solid #aaa;")
    
    def select_tool(self, mode):
        """Select a tool and close the dialog"""
        if mode == "undo":
            self.canvas.undo()
        elif mode == "redo":
            self.canvas.redo()
        elif mode == "transparency":
            self.canvas.toggle_canvas_transparency()
        elif mode == "board":
            self.canvas.toggle_board()
        elif mode == "capture":
            # Show the more menu which contains capture options
            self.canvas.toolbar.show_more_menu()
        elif mode == "settings":
            # Open settings
            self.canvas.open_settings()
        else:
            # Set drawing mode
            self.canvas.set_mode(mode)
        
        self.accept()


class AndroidHideHandle(QWidget):
    """Android-specific hide handle that shows tool gallery when clicked"""
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(70, 70)  # Large touch target
        
        # Style the hide handle as a small icon
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(105, 101, 219, 0.9);
                border-radius: 18px;
                border: 3px solid white;
            }
        """)
        
        self.hide()
    
    def paintEvent(self, event):
        """Draw a small icon representing the hidden toolbar"""
        from PySide6.QtGui import QPainter, QFont
        from PySide6.QtCore import Qt
        
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        
        # Draw a simplified toolbar icon
        painter.setPen(Qt.white)
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        
        # Draw a simple menu icon (three horizontal lines)
        painter.drawText(self.rect(), Qt.AlignCenter, "⋮")
    
    def mousePressEvent(self, event):
        """Show tool gallery when hide handle is pressed"""
        self.show_tool_gallery()
    
    def show_tool_gallery(self):
        """Show the tool gallery dialog"""
        dialog = ToolGalleryDialog(self.canvas, self)
        
        # Position dialog near the hide handle
        dialog.move(self.mapToGlobal(self.rect().topRight()))
        
        # Show dialog and handle result
        if dialog.exec() == QDialog.Accepted:
            # Tool was selected, hide the dialog
            pass
        else:
            # Dialog was cancelled, just close it
            pass


def create_android_optimized_toolbar(canvas):
    """Create an Android-optimized version of the toolbar"""
    # For Android, we use a minimal approach:
    # - Show only the hide handle (small icon)
    # - When clicked, show full tool gallery
    # - After tool selection, return to hide handle mode
    
    android_handle = AndroidHideHandle(canvas)
    return android_handle