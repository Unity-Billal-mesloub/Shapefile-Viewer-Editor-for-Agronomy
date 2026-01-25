"""
Statistics Viewer Module
Enhanced statistics viewer with charts and detailed spatial information.

Author: Bobby Azad
Version: 1.1
Date: 2026-01-25
"""

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatisticsDialog(QDialog):
    """
    Enhanced statistics viewer with tabbed interface showing:
    - General statistics
    - Spatial information
    - Attribute statistics
    - Visual charts
    """

    def __init__(self, gdf, parent=None):
        super().__init__(parent)
        self.gdf = gdf
        self.setWindowTitle("Shapefile Statistics - v1.1")
        self.resize(900, 700)

        main_layout = QVBoxLayout(self)

        # Create tabbed interface
        self.tabs = QTabWidget()

        # Tab 1: General Information
        self.tabs.addTab(self._create_general_tab(), "General Info")

        # Tab 2: Spatial Information
        self.tabs.addTab(self._create_spatial_tab(), "Spatial Info")

        # Tab 3: Attribute Statistics
        self.tabs.addTab(self._create_attributes_tab(), "Attributes")

        # Tab 4: Visual Charts
        self.tabs.addTab(self._create_charts_tab(), "Charts")

        main_layout.addWidget(self.tabs)

    def _create_general_tab(self):
        """Create the general information tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("General Information")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Create info group
        info_group = QGroupBox("Dataset Overview")
        info_layout = QVBoxLayout()

        num_features = len(self.gdf)
        num_attributes = len([col for col in self.gdf.columns if col != "geometry"])

        # Information labels
        info_items = [
            ("Number of Features:", str(num_features)),
            ("Number of Attributes:", str(num_attributes)),
            ("Geometry Types:", ", ".join(self.gdf.geom_type.unique())),
            ("Coordinate Reference System:", str(self.gdf.crs) if self.gdf.crs else "None"),
            ("EPSG Code:", str(self.gdf.crs.to_epsg()) if self.gdf.crs and self.gdf.crs.to_epsg() else "N/A"),
        ]

        for label_text, value_text in info_items:
            h_layout = QHBoxLayout()
            label = QLabel(label_text)
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            value = QLabel(value_text)
            h_layout.addWidget(label)
            h_layout.addWidget(value)
            h_layout.addStretch()
            info_layout.addLayout(h_layout)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        return widget

    def _create_spatial_tab(self):
        """Create the spatial information tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Spatial Information")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Bounding Box Group
        bbox_group = QGroupBox("Bounding Box")
        bbox_layout = QVBoxLayout()

        bounds = self.gdf.total_bounds
        bbox_items = [
            ("Minimum X:", f"{bounds[0]:.6f}"),
            ("Minimum Y:", f"{bounds[1]:.6f}"),
            ("Maximum X:", f"{bounds[2]:.6f}"),
            ("Maximum Y:", f"{bounds[3]:.6f}"),
            ("Width:", f"{bounds[2] - bounds[0]:.6f}"),
            ("Height:", f"{bounds[3] - bounds[1]:.6f}"),
        ]

        for label_text, value_text in bbox_items:
            h_layout = QHBoxLayout()
            label = QLabel(label_text)
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            value = QLabel(value_text)
            h_layout.addWidget(label)
            h_layout.addWidget(value)
            h_layout.addStretch()
            bbox_layout.addLayout(h_layout)

        bbox_group.setLayout(bbox_layout)
        layout.addWidget(bbox_group)

        # Area Statistics Group (if projected)
        if self.gdf.crs and self.gdf.crs.is_projected:
            area_group = QGroupBox("Area Statistics")
            area_layout = QVBoxLayout()

            total_area = self.gdf.area.sum()
            avg_area = self.gdf.area.mean()
            min_area = self.gdf.area.min()
            max_area = self.gdf.area.max()

            area_items = [
                ("Total Area:", f"{total_area:.2f} square units"),
                ("Average Area:", f"{avg_area:.2f} square units"),
                ("Minimum Area:", f"{min_area:.2f} square units"),
                ("Maximum Area:", f"{max_area:.2f} square units"),
            ]

            for label_text, value_text in area_items:
                h_layout = QHBoxLayout()
                label = QLabel(label_text)
                label_font = QFont()
                label_font.setBold(True)
                label.setFont(label_font)
                value = QLabel(value_text)
                h_layout.addWidget(label)
                h_layout.addWidget(value)
                h_layout.addStretch()
                area_layout.addLayout(h_layout)

            area_group.setLayout(area_layout)
            layout.addWidget(area_group)
        else:
            note = QLabel("Note: Area calculations require a projected coordinate system.")
            note.setWordWrap(True)
            layout.addWidget(note)

        layout.addStretch()
        return widget

    def _create_attributes_tab(self):
        """Create the attributes statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Attribute Statistics")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Create table for attribute statistics
        table = QTableWidget()
        attr_columns = [col for col in self.gdf.columns if col != "geometry"]

        table.setRowCount(len(attr_columns))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Attribute", "Type", "Unique Values", "Min", "Max"])

        for row_idx, col_name in enumerate(attr_columns):
            # Attribute name
            table.setItem(row_idx, 0, QTableWidgetItem(col_name))

            # Data type
            dtype = str(self.gdf[col_name].dtype)
            table.setItem(row_idx, 1, QTableWidgetItem(dtype))

            # Unique values count
            unique_count = self.gdf[col_name].nunique()
            table.setItem(row_idx, 2, QTableWidgetItem(str(unique_count)))

            # Min and Max (for numeric columns)
            try:
                if self.gdf[col_name].dtype in ['int64', 'float64']:
                    min_val = self.gdf[col_name].min()
                    max_val = self.gdf[col_name].max()
                    table.setItem(row_idx, 3, QTableWidgetItem(f"{min_val:.2f}"))
                    table.setItem(row_idx, 4, QTableWidgetItem(f"{max_val:.2f}"))
                else:
                    table.setItem(row_idx, 3, QTableWidgetItem("N/A"))
                    table.setItem(row_idx, 4, QTableWidgetItem("N/A"))
            except:
                table.setItem(row_idx, 3, QTableWidgetItem("N/A"))
                table.setItem(row_idx, 4, QTableWidgetItem("N/A"))

        table.resizeColumnsToContents()
        table.setAlternatingRowColors(True)
        layout.addWidget(table)

        return widget

    def _create_charts_tab(self):
        """Create the visual charts tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Visual Analysis")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Create matplotlib figure with subplots
        fig = Figure(figsize=(10, 8))
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create subplots
        if self.gdf.crs and self.gdf.crs.is_projected:
            # 2x2 grid for charts
            ax1 = fig.add_subplot(2, 2, 1)
            ax2 = fig.add_subplot(2, 2, 2)
            ax3 = fig.add_subplot(2, 2, 3)
            ax4 = fig.add_subplot(2, 2, 4)

            # Chart 1: Area distribution
            try:
                areas = self.gdf.area
                ax1.hist(areas, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
                ax1.set_title('Area Distribution')
                ax1.set_xlabel('Area (square units)')
                ax1.set_ylabel('Frequency')
                ax1.grid(True, alpha=0.3)
            except Exception as e:
                ax1.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center')

            # Chart 2: Geometry type distribution
            geom_types = self.gdf.geom_type.value_counts()
            ax2.pie(geom_types.values, labels=geom_types.index, autopct='%1.1f%%',
                   colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
            ax2.set_title('Geometry Type Distribution')

            # Chart 3: Feature count
            ax3.bar(['Total Features'], [len(self.gdf)], color='green', alpha=0.7)
            ax3.set_ylabel('Count')
            ax3.set_title('Feature Count')
            ax3.grid(True, alpha=0.3, axis='y')

            # Chart 4: Simple spatial plot
            self.gdf.plot(ax=ax4, color='lightblue', edgecolor='darkblue', linewidth=0.5)
            ax4.set_title('Spatial Overview')
            ax4.set_xticks([])
            ax4.set_yticks([])

        else:
            # Single large plot if not projected
            ax = fig.add_subplot(1, 1, 1)
            self.gdf.plot(ax=ax, color='lightblue', edgecolor='darkblue', linewidth=0.5)
            ax.set_title('Spatial Overview')
            ax.set_xticks([])
            ax.set_yticks([])

        fig.tight_layout()
        layout.addWidget(canvas)

        return widget
