"""
Desktop main application module
"""
import sys
from PySide6.QtWidgets import QApplication
from tutorDraw.canvas import TutorCanvas
from tutorDraw.themes import get_theme

def run_desktop_app():
    """Run the desktop version of the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("TutorDraw")
    app.setApplicationVersion("2.0")
    
    # Load theme
    theme = get_theme("light")  # Could be configurable
    
    # Create main window
    canvas = TutorCanvas(theme)
    
    sys.exit(app.exec())
