import json
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox, QFormLayout
from PyQt5.QtCore import Qt

class ModernSettingsDialog(QDialog):
    """Modern settings dialog for capture paths and preferences"""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config or {}
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the modern UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #6965db;
                padding-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Paths group
        paths_group = QGroupBox("Save Locations")
        paths_layout = QFormLayout(paths_group)
        paths_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        paths_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        paths_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        paths_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Screenshots path
        self.screenshots_path = QLineEdit()
        self.screenshots_path.setReadOnly(True)
        self.screenshots_btn = QPushButton("Browse...")
        self.screenshots_btn.clicked.connect(self.browse_screenshots)
        
        screenshots_layout = QHBoxLayout()
        screenshots_layout.addWidget(self.screenshots_path)
        screenshots_layout.addWidget(self.screenshots_btn)
        paths_layout.addRow("Screenshots:", screenshots_layout)
        
        # Videos path
        self.videos_path = QLineEdit()
        self.videos_path.setReadOnly(True)
        self.videos_btn = QPushButton("Browse...")
        self.videos_btn.clicked.connect(self.browse_videos)
        
        videos_layout = QHBoxLayout()
        videos_layout.addWidget(self.videos_path)
        videos_layout.addWidget(self.videos_btn)
        paths_layout.addRow("Videos:", videos_layout)
        
        layout.addWidget(paths_group)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        # Theme selection
        from PyQt5.QtWidgets import QComboBox
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(appearance_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        
    def load_settings(self):
        """Load current settings"""
        # Load screenshot path
        screenshots_path = self.config.get("screenshots_path", os.path.join(os.path.expanduser("~"), "Pictures", "TutorDraw"))
        self.screenshots_path.setText(screenshots_path)
        
        # Load videos path
        videos_path = self.config.get("videos_path", os.path.join(os.path.expanduser("~"), "Videos", "TutorDraw"))
        self.videos_path.setText(videos_path)
        
        # Load theme
        theme = self.config.get("current_theme", "light")
        self.theme_combo.setCurrentText(theme.capitalize())
        
    def browse_screenshots(self):
        """Browse for screenshots directory"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Screenshots Directory", 
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.screenshots_path.setText(directory)
            
    def browse_videos(self):
        """Browse for videos directory"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Videos Directory", 
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.videos_path.setText(directory)
            
    def reset_to_defaults(self):
        """Reset to default settings"""
        default_screenshots = os.path.join(os.path.expanduser("~"), "Pictures", "TutorDraw")
        default_videos = os.path.join(os.path.expanduser("~"), "Videos", "TutorDraw")
        
        self.screenshots_path.setText(default_screenshots)
        self.videos_path.setText(default_videos)
        self.theme_combo.setCurrentText("Light")
        
    def get_settings(self):
        """Get current settings"""
        return {
            "screenshots_path": self.screenshots_path.text(),
            "videos_path": self.videos_path.text(),
            "current_theme": self.theme_combo.currentText().lower()
        }