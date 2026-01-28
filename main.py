#!/usr/bin/env python3
"""
TutorDraw - Professional Drawing and Annotation Tool
Modular, Clean, Developer-Friendly Implementation
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.canvas import TutorCanvas

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("TutorDraw")
    app.setApplicationVersion("1.0.0")
    
    # Set application icon with fallback
    import os
    if os.path.exists("tutorDraw-logoX92.png"):
        app.setWindowIcon(QIcon("tutorDraw-logoX92.png"))
    
    # Create and show the main canvas
    window = TutorCanvas()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()