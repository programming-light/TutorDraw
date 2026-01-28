import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.themes_system import theme_manager

class TestThemes(unittest.TestCase):
    def test_themes_exist(self):
        themes = list(theme_manager.themes.keys())
        self.assertIn('Light', themes)
        self.assertIn('Dark', themes)
        self.assertIn('Deep Blue', themes)

if __name__ == '__main__':
    unittest.main()
