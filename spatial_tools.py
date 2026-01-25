"""
Spatial Tools Module
Provides spatial operations for GeoDataFrames.

Author: Bobby Azad
Version: 1.1
Date: 2026-01-25
"""

import geopandas as gpd

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QFormLayout, QStackedWidget, QWidget
)


class SpatialToolsDialog(QDialog):
    """Dialog for running spatial tools on a GeoDataFrame."""

    def __init__(self, gdf, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spatial Tools")
        self.resize(480, 320)
        self.gdf = gdf
        self.result_gdf = None
        self.status_message = ""

        main_layout = QVBoxLayout(self)

        header = QLabel("Select a spatial operation to apply:")
        main_layout.addWidget(header)

        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "Buffer",
            "Dissolve",
            "Clip",
            "Intersect",
            "Union",
            "Calculate Area",
            "Calculate Length",
        ])
        self.operation_combo.currentTextChanged.connect(self._on_operation_changed)
        main_layout.addWidget(self.operation_combo)

        self.stack = QStackedWidget()
        self.stack_map = {}

        self.stack_map["Buffer"] = self._build_buffer_widget()
        self.stack_map["Dissolve"] = self._build_dissolve_widget()
        self.stack_map["Clip"] = self._build_overlay_widget()
        self.stack_map["Intersect"] = self._build_overlay_widget()
        self.stack_map["Union"] = self._build_overlay_widget()
        self.stack_map["Calculate Area"] = self._build_area_widget()
        self.stack_map["Calculate Length"] = self._build_length_widget()

        for widget in self.stack_map.values():
            self.stack.addWidget(widget)

        main_layout.addWidget(self.stack)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self._run_tool)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(run_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)

        self._on_operation_changed(self.operation_combo.currentText())

    def _build_buffer_widget(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.buffer_distance = QLineEdit("10")
        layout.addRow("Distance:", self.buffer_distance)
        return widget

    def _build_dissolve_widget(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.dissolve_field = QComboBox()
        self.dissolve_field.addItem("<All>")
        for col in self.gdf.columns:
            if col != "geometry":
                self.dissolve_field.addItem(col)
        layout.addRow("Dissolve by:", self.dissolve_field)
        return widget

    def _build_overlay_widget(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        path_layout = QHBoxLayout()
        self.overlay_path = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_overlay)
        path_layout.addWidget(self.overlay_path)
        path_layout.addWidget(browse_btn)
        layout.addRow("Overlay layer:", path_layout)
        return widget

    def _build_area_widget(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.area_field = QLineEdit("area")
        layout.addRow("Output field:", self.area_field)
        return widget

    def _build_length_widget(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.length_field = QLineEdit("length")
        layout.addRow("Output field:", self.length_field)
        return widget

    def _on_operation_changed(self, operation):
        self.stack.setCurrentWidget(self.stack_map[operation])

    def _browse_overlay(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Overlay Layer",
            "",
            "Vector Files (*.shp *.geojson *.gpkg);;All Files (*)"
        )
        if file_path:
            self.overlay_path.setText(file_path)

    def _load_overlay_layer(self):
        path = self.overlay_path.text().strip()
        if not path:
            QMessageBox.warning(self, "Missing File", "Please select an overlay layer.")
            return None
        try:
            other = gpd.read_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read overlay layer:\n{str(e)}")
            return None
        if self.gdf.crs and other.crs and self.gdf.crs != other.crs:
            try:
                other = other.to_crs(self.gdf.crs)
            except Exception as e:
                QMessageBox.critical(
                    self, "CRS Error", f"Failed to reproject overlay layer:\n{str(e)}"
                )
                return None
        return other

    def _confirm_overwrite(self, field_name):
        if field_name in self.gdf.columns:
            reply = QMessageBox.question(
                self,
                "Overwrite Column",
                f"Column '{field_name}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes
        return True

    def _warn_geographic_crs(self, operation_name):
        if self.gdf.crs and not self.gdf.crs.is_projected:
            message = (
                f"{operation_name} is being run on a geographic CRS (degrees). "
                "Results may be inaccurate. Reproject to a projected CRS "
                "for distance/area calculations.\n\nContinue anyway?"
            )
            reply = QMessageBox.warning(
                self,
                "Geographic CRS Warning",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes
        return True

    def _run_tool(self):
        if "geometry" not in self.gdf.columns:
            QMessageBox.critical(self, "Error", "No geometry column found in the layer.")
            return
        operation = self.operation_combo.currentText()
        try:
            if operation == "Buffer":
                distance = float(self.buffer_distance.text())
                if not self._warn_geographic_crs("Buffer"):
                    return
                result = self.gdf.copy()
                result["geometry"] = result.geometry.buffer(distance)
                self.result_gdf = result
                self.status_message = f"Buffer applied (distance={distance})."

            elif operation == "Dissolve":
                field = self.dissolve_field.currentText()
                if field == "<All>":
                    result = self.gdf.dissolve()
                    result = result.reset_index(drop=True)
                else:
                    result = self.gdf.dissolve(by=field).reset_index()
                self.result_gdf = result
                self.status_message = "Dissolve completed."

            elif operation in ["Clip", "Intersect", "Union"]:
                other = self._load_overlay_layer()
                if other is None:
                    return
                if operation == "Clip":
                    result = gpd.clip(self.gdf, other)
                    self.status_message = "Clip completed."
                else:
                    how = "intersection" if operation == "Intersect" else "union"
                    result = gpd.overlay(self.gdf, other, how=how)
                    self.status_message = f"{operation} completed."
                self.result_gdf = result

            elif operation == "Calculate Area":
                field = self.area_field.text().strip() or "area"
                if not self._confirm_overwrite(field):
                    return
                if not self._warn_geographic_crs("Calculate Area"):
                    return
                result = self.gdf.copy()
                result[field] = result.geometry.area
                self.result_gdf = result
                if self.gdf.crs and not self.gdf.crs.is_projected:
                    self.status_message = (
                        "Area calculated (note: CRS is geographic; units may be degrees)."
                    )
                else:
                    self.status_message = "Area calculated."

            elif operation == "Calculate Length":
                field = self.length_field.text().strip() or "length"
                if not self._confirm_overwrite(field):
                    return
                if not self._warn_geographic_crs("Calculate Length"):
                    return
                result = self.gdf.copy()
                result[field] = result.geometry.length
                self.result_gdf = result
                if self.gdf.crs and not self.gdf.crs.is_projected:
                    self.status_message = (
                        "Length calculated (note: CRS is geographic; units may be degrees)."
                    )
                else:
                    self.status_message = "Length calculated."

            else:
                QMessageBox.warning(self, "Unsupported", "Operation not supported.")
                return

            self.accept()

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Operation failed:\n{str(e)}")
