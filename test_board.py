#!/usr/bin/env python3
"""
Test script to verify board functionality
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.canvas import TutorCanvas

def test_board_functionality():
    """Test the board toggle functionality"""
    app = QApplication(sys.argv)
    
    # Create canvas
    canvas = TutorCanvas()
    print(f"Initial board mode: {canvas.board_mode}")
    
    # Test toggle cycle
    print("Testing board toggle functionality...")
    
    # First toggle: transparent -> white
    canvas.toggle_board()
    print(f"After 1st toggle: {canvas.board_mode}")
    
    # Second toggle: white -> black
    canvas.toggle_board()
    print(f"After 2nd toggle: {canvas.board_mode}")
    
    # Third toggle: black -> transparent
    canvas.toggle_board()
    print(f"After 3rd toggle: {canvas.board_mode}")
    
    print("Board functionality test completed successfully!")

if __name__ == "__main__":
    test_board_functionality()