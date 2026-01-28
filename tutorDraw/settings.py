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
        from tutorDraw.themes import get_theme_stylesheet_comprehensive
        theme_data = get_theme_stylesheet_comprehensive(getattr(canvas, 'current_theme', 'Light'))
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
        
        for action, key in list(self.canvas.shortcuts.items())[:10]:
            row = QHBoxLayout()
            lbl = QLabel(action.title())
            lbl.setFixedWidth(150)
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
        
        save_btn = QPushButton("Save & Close")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6965db, stop:1 #8b87ff); color: white; border-radius: 12px; padding: 14px; font-weight: bold; border: none; font-size: 15px;")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #6965db; padding: 15px 0 8px 0; line-height: 1.4;")
        return lbl
        
    def pick_laser_color(self):
        c = QColorDialog.getColor(QColor(self.canvas.laser_color), self, "Pick Laser Color")
        if c.isValid():
            self.canvas.laser_color = c.name()
            self.c_btn.setStyleSheet(f"background: {c.name()}; border-radius: 8px; border: 2px solid #ccc;")
    
    def save_and_close(self):
        self.canvas.default_thickness = self.thick_spin.value()
        self.canvas.enable_fill = self.fill_check.isChecked()
        self.canvas.laser_glow = self.glow_check.isChecked()
        self.canvas.toolbar_orientation = "vertical" if self.orientation_check.isChecked() else "horizontal"
        new_theme = self.theme_combo.currentText()
        self.canvas.current_theme = new_theme
        # Apply the theme to canvas and all components to refresh icons
        self.canvas.apply_theme(new_theme)
        self.accept()