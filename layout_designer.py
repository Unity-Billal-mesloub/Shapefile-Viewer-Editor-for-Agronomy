"""
Map Layout Designer Module
Provides a layout preview with scale bar, north arrow, and legend.

Author: Bobby Azad
Version: 1.1
Date: 2026-01-25
"""

import math
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Patch

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt


class MapLayoutDialog(QDialog):
    """Layout designer with scale bar, north arrow, and legend."""

    def __init__(self, gdf, current_column=None, current_cmap="viridis", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Layout Designer")
        self.resize(1000, 720)
        self.gdf = gdf
        self.current_column = current_column if current_column else "<No color column>"
        self.current_cmap = current_cmap
        self.unit_label = "units"

        main_layout = QVBoxLayout(self)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit("Shapefile Layout")
        controls_layout.addWidget(self.title_edit, 2)

        controls_layout.addWidget(QLabel("Color by:"))
        self.column_combo = QComboBox()
        self.column_combo.addItem("<No color column>")
        for col in self.gdf.columns:
            if col != "geometry":
                self.column_combo.addItem(col)
        idx = self.column_combo.findText(self.current_column)
        if idx >= 0:
            self.column_combo.setCurrentIndex(idx)
        controls_layout.addWidget(self.column_combo, 2)

        controls_layout.addWidget(QLabel("Colormap:"))
        self.cmap_combo = QComboBox()
        colormaps = ["viridis", "plasma", "coolwarm", "Reds", "Blues", "Greens", "Set1"]
        for cm in colormaps:
            self.cmap_combo.addItem(cm)
        cmap_idx = self.cmap_combo.findText(self.current_cmap)
        if cmap_idx >= 0:
            self.cmap_combo.setCurrentIndex(cmap_idx)
        controls_layout.addWidget(self.cmap_combo, 1)

        main_layout.addLayout(controls_layout)

        option_layout = QHBoxLayout()
        self.legend_check = QCheckBox("Legend")
        self.legend_check.setChecked(True)
        self.scale_check = QCheckBox("Scale bar")
        self.scale_check.setChecked(True)
        self.north_check = QCheckBox("North arrow")
        self.north_check.setChecked(True)
        option_layout.addWidget(self.legend_check)
        option_layout.addWidget(self.scale_check)
        option_layout.addWidget(self.north_check)
        option_layout.addStretch()
        main_layout.addLayout(option_layout)

        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        update_btn = QPushButton("Update Preview")
        update_btn.clicked.connect(self.render_layout)
        export_png_btn = QPushButton("Export PNG")
        export_png_btn.clicked.connect(lambda: self._export_layout("png"))
        export_pdf_btn = QPushButton("Export PDF")
        export_pdf_btn.clicked.connect(lambda: self._export_layout("pdf"))
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(export_png_btn)
        button_layout.addWidget(export_pdf_btn)
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)

        self.render_layout()

    def _get_display_gdf(self):
        if self.gdf.crs is not None:
            try:
                if self.gdf.crs.to_epsg() != 3857:
                    display = self.gdf.to_crs(epsg=3857)
                else:
                    display = self.gdf
            except Exception:
                display = self.gdf
        else:
            display = self.gdf
        if display.crs and display.crs.to_epsg() == 3857:
            self.unit_label = "m"
        else:
            self.unit_label = "units"
        return display

    def render_layout(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        display_gdf = self._get_display_gdf()
        column = self.column_combo.currentText()
        cmap = self.cmap_combo.currentText()

        if column == "<No color column>":
            display_gdf.plot(
                ax=ax, color="#4c78a8", edgecolor="white", linewidth=0.5, alpha=0.9
            )
            if self.legend_check.isChecked():
                ax.legend(
                    handles=[Patch(facecolor="#4c78a8", edgecolor="white", label="Layer")],
                    loc="lower left"
                )
        else:
            display_gdf.plot(
                column=column,
                cmap=cmap,
                legend=self.legend_check.isChecked(),
                ax=ax,
                edgecolor="white",
                linewidth=0.5,
                alpha=0.9
            )

        title = self.title_edit.text().strip()
        if title:
            ax.set_title(title, fontsize=14, pad=12)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal", adjustable="box")

        if self.scale_check.isChecked():
            self._add_scale_bar(ax)
        if self.north_check.isChecked():
            self._add_north_arrow(ax)

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _nice_scale_length(self, raw_length):
        if raw_length <= 0:
            return 1
        magnitude = 10 ** int(math.floor(math.log10(raw_length)))
        residual = raw_length / magnitude
        if residual < 2:
            nice = 1
        elif residual < 5:
            nice = 2
        elif residual < 10:
            nice = 5
        else:
            nice = 10
        return nice * magnitude

    def _add_scale_bar(self, ax):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        if x_range <= 0 or y_range <= 0:
            return

        raw_length = x_range * 0.2
        length = self._nice_scale_length(raw_length)
        x_start = xlim[0] + x_range * 0.1
        y_start = ylim[0] + y_range * 0.05

        ax.plot(
            [x_start, x_start + length],
            [y_start, y_start],
            color="black",
            linewidth=3
        )
        tick_height = y_range * 0.01
        ax.plot([x_start, x_start], [y_start, y_start + tick_height], color="black", linewidth=3)
        ax.plot(
            [x_start + length, x_start + length],
            [y_start, y_start + tick_height],
            color="black",
            linewidth=3
        )
        ax.text(
            x_start + length / 2,
            y_start + tick_height * 1.6,
            f"{length:,.0f} {self.unit_label}",
            ha="center",
            va="bottom",
            fontsize=8
        )

    def _add_north_arrow(self, ax):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        if x_range <= 0 or y_range <= 0:
            return

        x = xlim[0] + x_range * 0.9
        y = ylim[0] + y_range * 0.1
        arrow_len = y_range * 0.08

        ax.annotate(
            "",
            xy=(x, y + arrow_len),
            xytext=(x, y),
            arrowprops=dict(facecolor="black", width=4, headwidth=12)
        )
        ax.text(x, y + arrow_len * 1.1, "N", ha="center", va="bottom", fontsize=10, fontweight="bold")

    def _export_layout(self, fmt):
        file_filter = "PNG Image (*.png)" if fmt == "png" else "PDF File (*.pdf)"
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export Layout as {fmt.upper()}", "", file_filter
        )
        if not file_path:
            return
        if fmt == "png" and not file_path.lower().endswith(".png"):
            file_path += ".png"
        if fmt == "pdf" and not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"
        try:
            self.fig.savefig(file_path, dpi=300, bbox_inches="tight")
            QMessageBox.information(self, "Export Complete", f"Saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export layout:\n{str(e)}")
