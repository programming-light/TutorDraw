from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QKeySequenceEdit, QSpinBox, QSlider, QCheckBox, QColorDialog, QFrame, QScrollArea, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QColor

class SettingsDialog(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 700)
        
        # Create scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setGeometry(10, 10, 480, 680)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        self.main_frame = QFrame()
        # Apply theme-aware styling
        from src.themes_system import theme_manager
        theme_data = theme_manager.get_theme_stylesheet(getattr(canvas, 'current_theme', 'Light'))
        bg_color = theme_data["bg_color"]
        text_color = theme_data["text_color"]
        border_color = theme_data["border_color"]
        secondary_color = theme_data["secondary_color"]
        
        self.main_frame.setStyleSheet(f"""
            QFrame {{ 
                background-color: {bg_color}; 
                border: 1px solid {border_color}; 
                border-radius: 20px; 
            }}
            QLabel {{ 
                color: {text_color}; 
                font-family: 'Segoe UI'; 
                font-weight: 600; 
                border: none; 
                font-size: 13px; 
            }}
            QKeySequenceEdit, QSpinBox {{ 
                background: {secondary_color}; 
                color: {text_color}; 
                padding: 8px; 
                border-radius: 8px; 
                border: 1px solid {border_color}; 
            }}
            QCheckBox {{ 
                color: {text_color}; 
                font-weight: 500; 
            }}
            QComboBox {{
                background: {secondary_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 5px;
            }}
            QComboBox QAbstractItemView {{
                background: {bg_color};
                color: {text_color};
                selection-background-color: {theme_data["highlight_color"]};
            }}
        """)

        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        scroll_area.setWidget(self.main_frame)
        
        header = QHBoxLayout()
        title = QLabel("⚙️ Settings")
        title.setStyleSheet(f"font-size: 24px; color: {theme_data['accent_color']}; font-weight: 800;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"background: {theme_data['secondary_color']}; color: {theme_data['accent_color']}; border-radius: 18px; font-weight: bold; border: none; font-size: 18px;")
        close_btn.clicked.connect(self.reject)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        layout.addSpacing(5)
        layout.addWidget(self._section_label("🎹 SHORTCUTS"))
        
        # Show all shortcuts including the new ones
        shortcut_items = list(self.canvas.shortcuts.items())
        for action, key in shortcut_items:
            row = QHBoxLayout()
            # Format the action name for better display
            display_name = action.replace("_", " ").title()
            lbl = QLabel(display_name)
            lbl.setFixedWidth(180)
            row.addWidget(lbl)
            ks = QKeySequenceEdit(QKeySequence(key))
            ks.editingFinished.connect(lambda a=action, k=ks: self.canvas.shortcuts.update({a: k.keySequence().toString()}))
            row.addWidget(ks)
            layout.addLayout(row)

        layout.addSpacing(8)
        layout.addWidget(self._section_label("✏️ DRAWING"))
        
        thick_row = QHBoxLayout()
        thick_label = QLabel("Default Thickness:")
        thick_label.setFixedWidth(150)
        thick_row.addWidget(thick_label)
        self.thick_spin = QSpinBox()
        self.thick_spin.setRange(1, 20)
        self.thick_spin.setValue(self.canvas.default_thickness)
        thick_row.addWidget(self.thick_spin)
        layout.addLayout(thick_row)
        
        self.fill_check = QCheckBox("Enable shape fill by default")
        self.fill_check.setChecked(self.canvas.enable_fill)
        layout.addWidget(self.fill_check)

        layout.addSpacing(15)
        layout.addWidget(self._section_label("🪄 LASER POINTER"))
        
        self.lbl_t = QLabel(f"Thickness: {self.canvas.laser_thickness}px")
        self.lbl_t.setFixedWidth(150)
        layout.addWidget(self.lbl_t)
        t_slider = QSlider(Qt.Horizontal)
        t_slider.setRange(4, 50)
        t_slider.setValue(self.canvas.laser_thickness)
        t_slider.valueChanged.connect(lambda v: (setattr(self.canvas, 'laser_thickness', v), self.lbl_t.setText(f"Thickness: {v}px")))
        layout.addWidget(t_slider)

        self.lbl_d = QLabel(f"Duration: {self.canvas.laser_duration}s")
        self.lbl_d.setFixedWidth(150)
        layout.addWidget(self.lbl_d)
        d_slider = QSlider(Qt.Horizontal)
        d_slider.setRange(5, 100)
        d_slider.setValue(int(self.canvas.laser_duration * 10))
        d_slider.valueChanged.connect(lambda v: (setattr(self.canvas, 'laser_duration', v/10.0), self.lbl_d.setText(f"Duration: {v/10.0:.1f}s")))
        layout.addWidget(d_slider)

        self.lbl_s = QLabel(f"Smoothness: {self.canvas.laser_smoothness}")
        self.lbl_s.setFixedWidth(150)
        layout.addWidget(self.lbl_s)
        s_slider = QSlider(Qt.Horizontal)
        s_slider.setRange(1, 10)
        s_slider.setValue(self.canvas.laser_smoothness)
        s_slider.valueChanged.connect(lambda v: (setattr(self.canvas, 'laser_smoothness', v), self.lbl_s.setText(f"Smoothness: {v}")))
        layout.addWidget(s_slider)

        row_c = QHBoxLayout()
        laser_color_label = QLabel("Laser Color:")
        laser_color_label.setFixedWidth(150)
        row_c.addWidget(laser_color_label)
        self.c_btn = QPushButton()
        self.c_btn.setFixedSize(50, 30)
        self.c_btn.setCursor(Qt.PointingHandCursor)
        self.c_btn.setStyleSheet(f"background: {self.canvas.laser_color}; border-radius: 8px; border: 2px solid #ccc;")
        self.c_btn.clicked.connect(self.pick_laser_color)
        row_c.addWidget(self.c_btn)
        row_c.addStretch()
        layout.addLayout(row_c)
        
        self.glow_check = QCheckBox("Enable glow effect")
        self.glow_check.setChecked(self.canvas.laser_glow)
        layout.addWidget(self.glow_check)

        layout.addSpacing(8)
        layout.addWidget(self._section_label("🏙️ TOOLBAR"))
        
        self.orientation_check = QCheckBox("Vertical Toolbar")
        self.orientation_check.setChecked(self.canvas.toolbar_orientation == "vertical")
        layout.addWidget(self.orientation_check)

        layout.addSpacing(15)
        layout.addWidget(self._section_label("🎨 THEMES"))
        
        # Theme selection
        theme_row = QHBoxLayout()
        theme_label = QLabel("Select Theme:")
        theme_label.setFixedWidth(150)
        theme_row.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Charcoal", "Deep Blue", "Colorful", "Jellyfish", "Deep Green"])
        
        # Set current theme based on canvas setting
        current_theme = getattr(self.canvas, 'current_theme', 'Light')
        index = self.theme_combo.findText(current_theme, Qt.MatchFixedString)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        theme_row.addWidget(self.theme_combo)
        layout.addLayout(theme_row)

        layout.addStretch()
        
        # Reset shortcuts button
        reset_shortcuts_btn = QPushButton("↺ Reset All Shortcuts to Defaults")
        reset_shortcuts_btn.setCursor(Qt.PointingHandCursor)
        reset_shortcuts_btn.setStyleSheet("""
            QPushButton {
                background: #ff6b6b;
                color: white;
                border-radius: 12px;
                padding: 12px;
                font-weight: bold;
                border: none;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background: #ff5252;
            }
        """)
        reset_shortcuts_btn.clicked.connect(self.reset_shortcuts_to_defaults)
        layout.addWidget(reset_shortcuts_btn)
        
        save_btn = QPushButton("Save & Close")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6965db, stop:1 #8b87ff); color: white; border-radius: 12px; padding: 14px; font-weight: bold; border: none; font-size: 15px;")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)
        
        # Add save paths section
        layout.addSpacing(15)
        layout.addWidget(self._section_label("📁 SAVE LOCATIONS"))
        
        # Screenshots path
        screenshots_row = QHBoxLayout()
        screenshots_label = QLabel("Screenshots Path:")
        screenshots_label.setFixedWidth(120)
        screenshots_row.addWidget(screenshots_label)
        
        self.screenshots_path_input = QLabel()
        self.screenshots_path_input.setText(self.canvas.screenshots_path)
        self.screenshots_path_input.setStyleSheet(f"color: {text_color}; background: {secondary_color}; padding: 5px; border-radius: 5px; border: 1px solid {border_color};")
        screenshots_row.addWidget(self.screenshots_path_input)
        
        screenshots_browse_btn = QPushButton("Browse")
        screenshots_browse_btn.clicked.connect(self.browse_screenshots_path)
        screenshots_row.addWidget(screenshots_browse_btn)
        
        layout.addLayout(screenshots_row)
        
        # Videos path
        videos_row = QHBoxLayout()
        videos_label = QLabel("Videos Path:")
        videos_label.setFixedWidth(120)
        videos_row.addWidget(videos_label)
        
        self.videos_path_input = QLabel()
        self.videos_path_input.setText(self.canvas.videos_path)
        self.videos_path_input.setStyleSheet(f"color: {text_color}; background: {secondary_color}; padding: 5px; border-radius: 5px; border: 1px solid {border_color};")
        videos_row.addWidget(self.videos_path_input)
        
        videos_browse_btn = QPushButton("Browse")
        videos_browse_btn.clicked.connect(self.browse_videos_path)
        videos_row.addWidget(videos_browse_btn)
        
        layout.addLayout(videos_row)

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #6965db; padding: 15px 0 8px 0; line-height: 1.4;")
        return lbl
        
    def pick_laser_color(self):
        c = QColorDialog.getColor(QColor(self.canvas.laser_color), self, "Pick Laser Color")
        if c.isValid():
            self.canvas.laser_color = c.name()
            self.c_btn.setStyleSheet(f"background: {c.name()}; border-radius: 8px; border: 2px solid #ccc;")
    
    def reset_shortcuts_to_defaults(self):
        """Reset all shortcuts to their default values"""
        # Define default shortcuts
        default_shortcuts = {
            "mouse": "Ctrl+Alt+M", "select": "Ctrl+Alt+V", "pencil": "Ctrl+Alt+P", 
            "rect": "Ctrl+Alt+R", "ellipse": "Ctrl+Alt+E", "arrow": "Ctrl+Alt+A", 
            "text": "Ctrl+Alt+T", "eraser": "Ctrl+Alt+X", "clear": "Ctrl+Alt+C",
            "hide_show": "Ctrl+Alt+H", "toggle_board": "Ctrl+Alt+B", "undo": "Ctrl+Alt+Z", 
            "redo": "Ctrl+Alt+Y", "full_screenshot": "Ctrl+Alt+S", "area_screenshot": "Ctrl+Alt+Shift+S",
            "long_screenshot": "Ctrl+Alt+L", "scrolling_screenshot": "Ctrl+Alt+Shift+L",
            "toggle_recording": "Ctrl+Alt+Rec", "record_area": "Ctrl+Alt+Shift+Rec",
            "toggle_fill": "Ctrl+Alt+F"
        }
        
        # Update canvas shortcuts
        self.canvas.shortcuts.update(default_shortcuts)
        
        # Show confirmation
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Shortcuts Reset", "All shortcuts have been reset to their default values.")
        
        # Close and reopen settings to refresh the display
        self.accept()
        new_settings = SettingsDialog(self.canvas, self.parent())
        new_settings.exec_()
    
    def save_and_close(self):
        self.canvas.default_thickness = self.thick_spin.value()
        self.canvas.enable_fill = self.fill_check.isChecked()
        self.canvas.laser_glow = self.glow_check.isChecked()
        self.canvas.toolbar_orientation = "vertical" if self.orientation_check.isChecked() else "horizontal"
        new_theme = self.theme_combo.currentText()
        self.canvas.current_theme = new_theme
        # Apply the theme to canvas and all components to refresh icons
        if hasattr(self.canvas, 'apply_theme'):
            self.canvas.apply_theme(new_theme)
        self.accept()
        
    def browse_screenshots_path(self):
        from PyQt5.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Screenshots Directory", 
            self.canvas.screenshots_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.canvas.screenshots_path = directory
            self.screenshots_path_input.setText(directory)
            
    def browse_videos_path(self):
        from PyQt5.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Videos Directory", 
            self.canvas.videos_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.canvas.videos_path = directory
            self.videos_path_input.setText(directory)