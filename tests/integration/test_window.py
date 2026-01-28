"""
Integration tests for window functionality
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestWindowIntegration(unittest.TestCase):
    """Test window-related integration functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Import here to avoid issues with QApplication instantiation
        from PyQt5.QtWidgets import QApplication
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
    
    def test_import_structure(self):
        """Test that all required modules can be imported"""
        try:
            from src.canvas import TutorCanvas
            from src.themes_system import theme_manager
            # Test successful if no ImportError is raised
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_theme_manager_availability(self):
        """Test that theme manager is properly accessible"""
        from src.themes_system import theme_manager
        
        # Test that theme manager has the expected structure
        self.assertTrue(hasattr(theme_manager, 'themes'))
        self.assertIsInstance(theme_manager.themes, dict)
        self.assertGreater(len(theme_manager.themes), 0)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.app:
            self.app.quit()

if __name__ == '__main__':
    unittest.main()