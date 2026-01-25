"""
About Dialog Module
About dialog for the Shapefile Editor application.

Author: Bobby Azad
Version: 1.1
Date: 2026-01-25
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap


class AboutDialog(QDialog):
    """
    About dialog with application information.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Shapefile Editor")
        self.setFixedSize(600, 500)
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Application Title
        title = QLabel("Shapefile Editor")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Version
        version = QLabel("Version 1.1")
        version_font = QFont()
        version_font.setPointSize(14)
        version.setFont(version_font)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #666;")
        main_layout.addWidget(version)

        # Separator line
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        line1.setStyleSheet("background-color: #ccc;")
        main_layout.addWidget(line1)

        # Description
        description = QLabel(
            "A comprehensive tool for viewing, editing, and analyzing ESRI Shapefiles.\n\n"
            "Designed specifically for agronomists and GIS professionals working with\n"
            "agricultural and spatial data."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description_font = QFont()
        description_font.setPointSize(11)
        description.setFont(description_font)
        description.setStyleSheet("color: #444; line-height: 1.6;")
        main_layout.addWidget(description)

        # Features Section
        features_label = QLabel("Key Features")
        features_font = QFont()
        features_font.setPointSize(12)
        features_font.setBold(True)
        features_label.setFont(features_font)
        features_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(features_label)

        features = QLabel(
            "• Interactive map viewer with Google Maps-like navigation\n"
            "• Real-time basemap integration (satellite imagery)\n"
            "• Advanced attribute table editor\n"
            "• Mass update operations\n"
            "• Comprehensive statistics with visual charts\n"
            "• Multiple geometry type support\n"
            "• CRS transformation capabilities"
        )
        features_font = QFont()
        features_font.setPointSize(10)
        features.setFont(features_font)
        features.setStyleSheet("color: #555; padding-left: 10px;")
        main_layout.addWidget(features)

        # Separator line
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        line2.setStyleSheet("background-color: #ccc;")
        main_layout.addWidget(line2)

        # Developer Information
        dev_layout = QVBoxLayout()
        dev_layout.setSpacing(5)

        developer = QLabel("Developer")
        dev_font = QFont()
        dev_font.setPointSize(10)
        dev_font.setBold(True)
        developer.setFont(dev_font)
        developer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_layout.addWidget(developer)

        dev_name = QLabel("Bobby Azad")
        dev_name_font = QFont()
        dev_name_font.setPointSize(12)
        dev_name.setFont(dev_name_font)
        dev_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_name.setStyleSheet("color: #2c3e50;")
        dev_layout.addWidget(dev_name)

        release_date = QLabel("Released: January 25, 2026")
        release_font = QFont()
        release_font.setPointSize(9)
        release_date.setFont(release_font)
        release_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        release_date.setStyleSheet("color: #777;")
        dev_layout.addWidget(release_date)

        main_layout.addLayout(dev_layout)

        # Technology Stack
        tech_label = QLabel("Built with")
        tech_font = QFont()
        tech_font.setPointSize(9)
        tech_font.setItalic(True)
        tech_label.setFont(tech_font)
        tech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tech_label.setStyleSheet("color: #888;")
        main_layout.addWidget(tech_label)

        tech_stack = QLabel("Python • PySide6 • GeoPandas • Matplotlib • Contextily")
        tech_stack_font = QFont()
        tech_stack_font.setPointSize(9)
        tech_stack.setFont(tech_stack_font)
        tech_stack.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tech_stack.setStyleSheet("color: #999;")
        main_layout.addWidget(tech_stack)

        main_layout.addStretch()

        # Close Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(100, 35)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Set dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                background-color: transparent;
                color: #212529;
            }
        """)
