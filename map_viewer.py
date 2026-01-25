"""
Map Viewer Module
Interactive map viewer with Google Maps-like navigation for shapefiles.

Author: Bobby Azad
Version: 1.1
Date: 2026-01-25
"""

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import contextily as ctx

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QSlider, QWidget, QGridLayout, QSizePolicy, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from layout_designer import MapLayoutDialog


class MapDialog(QDialog):
    """
    Interactive map viewer with Google Maps-like navigation.
    Features mouse pan/zoom, dynamic basemap loading, and smooth interaction.
    """

    def __init__(self, gdf, parent=None):
        super().__init__(parent)
        # Close stray figures so no extra "Figure 1" window appears.
        plt.close('all')
        self.setWindowTitle("Shapefile Map Viewer - v1.1")
        self.resize(1000, 700)
        self.gdf = gdf
        self.current_alpha = 1.0  # Current transparency for the shapefile overlay.
        self.is_updating = False  # Prevent recursive updates

        main_layout = QVBoxLayout(self)

        # --- Top Controls for Coloring ---
        control_layout = QHBoxLayout()
        self.column_combo = QComboBox()
        self.column_combo.addItem("<No color column>")
        for col_name in self.gdf.columns:
            if col_name != "geometry":
                self.column_combo.addItem(col_name)
        control_layout.addWidget(QLabel("Color by:"))
        control_layout.addWidget(self.column_combo)
        # Default to 'zone' if present.
        idx = self.column_combo.findText("zone")
        if idx >= 0:
            self.column_combo.setCurrentIndex(idx)
        self.cmap_combo = QComboBox()
        colormaps = ["viridis", "plasma", "coolwarm", "Reds", "Blues", "Greens", "Set1"]
        for cm in colormaps:
            self.cmap_combo.addItem(cm)
        control_layout.addWidget(QLabel("Colormap:"))
        control_layout.addWidget(self.cmap_combo)
        self.update_btn = QPushButton("Update Map")
        self.update_btn.clicked.connect(self.update_map)
        control_layout.addWidget(self.update_btn)
        self.reset_btn = QPushButton("Reset View")
        self.reset_btn.clicked.connect(self.reset_view)
        control_layout.addWidget(self.reset_btn)
        self.layout_btn = QPushButton("Layout Designer")
        self.layout_btn.clicked.connect(self.open_layout_designer)
        control_layout.addWidget(self.layout_btn)
        self.export_png_btn = QPushButton("Export PNG")
        self.export_png_btn.clicked.connect(lambda: self.export_map("png"))
        control_layout.addWidget(self.export_png_btn)
        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(lambda: self.export_map("pdf"))
        control_layout.addWidget(self.export_pdf_btn)
        main_layout.addLayout(control_layout)

        # --- Map and Controls Layout ---
        map_layout = QHBoxLayout()

        # Navigation buttons widget.
        nav_widget = QWidget()
        nav_grid = QGridLayout()
        nav_grid.setSpacing(0)
        nav_grid.setContentsMargins(0, 0, 0, 0)
        nav_grid.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)

        self.btn_up = QPushButton("↑")
        self.btn_down = QPushButton("↓")
        self.btn_left = QPushButton("←")
        self.btn_right = QPushButton("→")

        for btn in (self.btn_up, self.btn_down, self.btn_left, self.btn_right):
            btn.setFixedSize(40, 40)

        # Connect each button to pan 20% of the current view.
        self.btn_up.clicked.connect(lambda: self.move_map(0, 0.2))
        self.btn_down.clicked.connect(lambda: self.move_map(0, -0.2))
        self.btn_left.clicked.connect(lambda: self.move_map(-0.2, 0))
        self.btn_right.clicked.connect(lambda: self.move_map(0.2, 0))

        # Arrange the buttons in a "+" shape
        nav_grid.addWidget(self.btn_up, 0, 1)
        nav_grid.addWidget(self.btn_left, 1, 0)
        nav_grid.addWidget(self.btn_right, 1, 2)
        nav_grid.addWidget(self.btn_down, 2, 1)
        nav_widget.setLayout(nav_grid)
        nav_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        map_layout.addWidget(nav_widget)

        # Canvas and its related controls.
        canvas_layout = QVBoxLayout()
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        canvas_layout.addWidget(self.toolbar)
        canvas_layout.addWidget(self.canvas)

        # Enable mouse wheel zoom and pan
        self.canvas.mpl_connect('scroll_event', self.on_mouse_scroll)
        # Connect to matplotlib navigation events to reload basemap
        self.canvas.mpl_connect('button_release_event', self.on_pan_zoom_release)

        # Horizontal zoom slider.
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.valueChanged.connect(self.on_slider_zoom)
        canvas_layout.addWidget(self.zoom_slider)
        map_layout.addLayout(canvas_layout)

        # Vertical transparency slider.
        self.transparency_slider = QSlider(Qt.Orientation.Vertical)
        self.transparency_slider.setMinimum(0)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(100)
        self.transparency_slider.setTickInterval(10)
        self.transparency_slider.setTickPosition(QSlider.TickPosition.TicksRight)
        self.transparency_slider.valueChanged.connect(self.on_slider_transparency)
        map_layout.addWidget(self.transparency_slider)

        main_layout.addLayout(map_layout)

        self.plot_initial()

    def plot_initial(self):
        """Initial plot of the shapefile with basemap."""
        self.ax.clear()
        current_col = self.column_combo.currentText()
        cmap = self.cmap_combo.currentText()

        # Reproject to Web Mercator (EPSG:3857) for basemap compatibility
        if self.gdf.crs is not None:
            try:
                if self.gdf.crs.to_epsg() != 3857:
                    self.display_gdf = self.gdf.to_crs(epsg=3857)
                else:
                    self.display_gdf = self.gdf
            except Exception as e:
                print("Error in reprojection:", e)
                self.display_gdf = self.gdf
        else:
            self.display_gdf = self.gdf

        # Plot the shapefile
        if current_col == "<No color column>":
            self.display_gdf.plot(ax=self.ax, zorder=2, alpha=self.current_alpha,
                                edgecolor='white', linewidth=0.5)
        else:
            self.display_gdf.plot(column=current_col, cmap=cmap, legend=True,
                                ax=self.ax, zorder=2, alpha=self.current_alpha,
                                edgecolor='white', linewidth=0.5)

        # Add basemap
        if self.gdf.crs is not None:
            try:
                ctx.add_basemap(self.ax,
                              source=ctx.providers.Esri.WorldImagery,
                              zorder=1, attribution='')
            except Exception as e:
                print("Basemap could not be added:", e)

        self.ax.set_title("Shapefile Geometry (Use mouse to pan/zoom)")
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.fig.tight_layout()
        self.canvas.draw()

        # Store original extent for reset
        self.original_xlim = self.ax.get_xlim()
        self.original_ylim = self.ax.get_ylim()

    def reload_basemap(self):
        """Dynamically reload the basemap based on current view extent."""
        if self.is_updating:
            return

        self.is_updating = True
        try:
            # Get current view limits before clearing
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            # Clear and redraw everything
            self.ax.clear()

            col = self.column_combo.currentText()
            cmap = self.cmap_combo.currentText()

            # Plot shapefile
            if col == "<No color column>":
                self.display_gdf.plot(ax=self.ax, zorder=2, alpha=self.current_alpha,
                                    edgecolor='white', linewidth=0.5)
            else:
                self.display_gdf.plot(column=col, cmap=cmap, legend=True,
                                    ax=self.ax, zorder=2, alpha=self.current_alpha,
                                    edgecolor='white', linewidth=0.5)

            # Restore view limits
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)

            # Add basemap for current view
            if self.gdf.crs is not None:
                try:
                    ctx.add_basemap(self.ax,
                                  source=ctx.providers.Esri.WorldImagery,
                                  zorder=1, attribution='')
                except Exception as e:
                    print("Basemap reload failed:", e)

            self.ax.set_title("Shapefile Geometry (Use mouse to pan/zoom)")
            self.ax.set_xticks([])
            self.ax.set_yticks([])

            self.canvas.draw_idle()
        finally:
            self.is_updating = False

    def update_map(self):
        """Update map when color/colormap settings change."""
        self.reload_basemap()
        self.zoom_slider.setValue(100)
        self.original_xlim = self.ax.get_xlim()
        self.original_ylim = self.ax.get_ylim()

    def reset_view(self):
        """Reset the view to the original base view."""
        self.ax.set_xlim(self.original_xlim)
        self.ax.set_ylim(self.original_ylim)
        self.zoom_slider.setValue(100)
        self.reload_basemap()

    def on_mouse_scroll(self, event):
        """Handle mouse wheel zoom."""
        if event.inaxes != self.ax:
            return

        # Get current limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        # Get event location
        xdata = event.xdata
        ydata = event.ydata

        # Zoom factor
        if event.button == 'up':
            scale_factor = 0.8  # Zoom in
        elif event.button == 'down':
            scale_factor = 1.25  # Zoom out
        else:
            return

        # Calculate new limits centered on mouse position
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])

        # Reload basemap with new extent
        self.reload_basemap()

    def on_pan_zoom_release(self, event):
        """Called when mouse button is released after pan/zoom from toolbar."""
        if event.button in [1, 3]:  # Left or right mouse button
            self.reload_basemap()

    def on_slider_zoom(self, value):
        """Adjust the view limits based on the zoom slider value."""
        scale = value / 100.0
        x_center = (self.original_xlim[0] + self.original_xlim[1]) / 2
        y_center = (self.original_ylim[0] + self.original_ylim[1]) / 2
        half_width = (self.original_xlim[1] - self.original_xlim[0]) / 2
        half_height = (self.original_ylim[1] - self.original_ylim[0]) / 2

        new_xlim = [x_center - half_width / scale, x_center + half_width / scale]
        new_ylim = [y_center - half_height / scale, y_center + half_height / scale]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Reload basemap with new zoom level
        self.reload_basemap()

    def on_slider_transparency(self, value):
        """Update the transparency of the shapefile overlay."""
        new_alpha = value / 100.0
        self.current_alpha = new_alpha
        for coll in self.ax.collections:
            if coll.get_zorder() == 2:
                coll.set_alpha(new_alpha)
        self.canvas.draw_idle()

    def move_map(self, dx_frac, dy_frac):
        """Pan the view by a fraction of the current view's width/height."""
        # Get the current view limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        # Calculate the width and height of the current view
        width = cur_xlim[1] - cur_xlim[0]
        height = cur_ylim[1] - cur_ylim[0]

        # Calculate the new view limits based on the panning fractions
        dx = dx_frac * width
        dy = dy_frac * height
        new_xlim = (cur_xlim[0] + dx, cur_xlim[1] + dx)
        new_ylim = (cur_ylim[0] + dy, cur_ylim[1] + dy)

        # Set the new view limits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Reload basemap with new extent
        self.reload_basemap()

        # Update the base view so that the zoom slider works relative to the new view
        self.original_xlim = self.ax.get_xlim()
        self.original_ylim = self.ax.get_ylim()

    def export_map(self, fmt):
        """Export the current map view to PNG or PDF."""
        file_filter = "PNG Image (*.png)" if fmt == "png" else "PDF File (*.pdf)"
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export Map as {fmt.upper()}", "", file_filter
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
            QMessageBox.critical(self, "Export Error", f"Failed to export map:\n{str(e)}")

    def open_layout_designer(self):
        """Open the map layout designer dialog."""
        current_col = self.column_combo.currentText()
        current_cmap = self.cmap_combo.currentText()
        gdf_for_layout = getattr(self, "display_gdf", self.gdf)
        dlg = MapLayoutDialog(gdf_for_layout, current_col, current_cmap, parent=self)
        dlg.exec()
