"""
Shapefile Editor - Main Application
A comprehensive tool for viewing, editing, and analyzing ESRI Shapefiles.

Author: Bobby Azad
Version: 1.1
Date: 2026-01-25
"""

import sys
import geopandas as gpd
import pandas as pd

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QMessageBox, QDialog, QDialogButtonBox,
    QCheckBox, QRadioButton, QGroupBox, QLabel, QLineEdit, QHBoxLayout, QComboBox,
    QInputDialog, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

# Import custom modules
from map_viewer import MapDialog
from statistics_viewer import StatisticsDialog
from about_dialog import AboutDialog
from spatial_tools import SpatialToolsDialog


class MassUpdateDialog(QDialog):
    """Dialog for mass updating table columns with arithmetic operations."""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mass Update Columns")
        self.selectedColumns = []
        self.operation = None
        self.value = 0

        main_layout = QVBoxLayout(self)

        columns_groupbox = QGroupBox("Select Columns to Update:")
        columns_layout = QVBoxLayout()
        self.checkboxes = []
        for col in columns:
            cb = QCheckBox(col)
            columns_layout.addWidget(cb)
            self.checkboxes.append(cb)
        columns_groupbox.setLayout(columns_layout)
        main_layout.addWidget(columns_groupbox)

        operations_groupbox = QGroupBox("Operation:")
        operations_layout = QVBoxLayout()
        self.radio_add = QRadioButton("Add")
        self.radio_sub = QRadioButton("Subtract")
        self.radio_mul = QRadioButton("Multiply")
        self.radio_div = QRadioButton("Divide")
        self.radio_add.setChecked(True)
        operations_layout.addWidget(self.radio_add)
        operations_layout.addWidget(self.radio_sub)
        operations_layout.addWidget(self.radio_mul)
        operations_layout.addWidget(self.radio_div)
        operations_groupbox.setLayout(operations_layout)
        main_layout.addWidget(operations_groupbox)

        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Value:"))
        self.value_edit = QLineEdit()
        self.value_edit.setText("0")
        value_layout.addWidget(self.value_edit)
        main_layout.addLayout(value_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def accept(self):
        self.selectedColumns = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        if self.radio_add.isChecked():
            self.operation = "add"
        elif self.radio_sub.isChecked():
            self.operation = "subtract"
        elif self.radio_mul.isChecked():
            self.operation = "multiply"
        elif self.radio_div.isChecked():
            self.operation = "divide"
        try:
            self.value = float(self.value_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Value", "Please enter a valid numeric value.")
            return
        super().accept()

    def getSelectedColumns(self):
        return self.selectedColumns

    def getOperation(self):
        return self.operation

    def getValue(self):
        return self.value


class MainWindow(QMainWindow):
    """Main application window for shapefile editing."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapefile Editor v1.1 - by Bobby Azad")
        self.resize(1000, 700)

        # Menu Bar
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open Shapefile", self)
        open_action.triggered.connect(self.open_shapefile)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        save_action = QAction("Save Shapefile As...", self)
        save_action.triggered.connect(self.save_shapefile)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        export_geojson_action = QAction("Export GeoJSON...", self)
        export_geojson_action.triggered.connect(self.export_geojson)
        file_menu.addAction(export_geojson_action)

        export_gpkg_action = QAction("Export GeoPackage...", self)
        export_gpkg_action.triggered.connect(self.export_geopackage)
        file_menu.addAction(export_gpkg_action)

        export_csv_action = QAction("Export Attributes CSV...", self)
        export_csv_action.triggered.connect(self.export_csv_attributes)
        file_menu.addAction(export_csv_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        stats_action = QAction("Show Statistics", self)
        stats_action.triggered.connect(self.show_statistics)
        stats_action.setShortcut("Ctrl+T")
        tools_menu.addAction(stats_action)

        spatial_action = QAction("Spatial Tools...", self)
        spatial_action.triggered.connect(self.open_spatial_tools)
        spatial_action.setShortcut("Ctrl+Shift+S")
        tools_menu.addAction(spatial_action)

        # Help Menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        about_action.setShortcut("F1")
        help_menu.addAction(about_action)

        # Main widget layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # --- Filter Section ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter column:"))
        self.filterColumnCombo = QComboBox()
        filter_layout.addWidget(self.filterColumnCombo, 1)
        filter_layout.addWidget(QLabel("Filter text:"))
        self.filterLineEdit = QLineEdit()
        filter_layout.addWidget(self.filterLineEdit, 3)
        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.apply_filter)
        filter_layout.addWidget(apply_filter_btn)
        clear_filter_btn = QPushButton("Clear Filter")
        clear_filter_btn.clicked.connect(self.clear_filter)
        filter_layout.addWidget(clear_filter_btn)
        self.main_layout.addLayout(filter_layout)

        # Table widget
        self.tableWidget = QTableWidget()
        self.main_layout.addWidget(self.tableWidget)

        # First row of buttons
        buttons_layout = QHBoxLayout()
        self.massUpdateButton = QPushButton("Mass Update")
        self.massUpdateButton.clicked.connect(self.mass_update)
        buttons_layout.addWidget(self.massUpdateButton)
        self.viewMapButton = QPushButton("View Map")
        self.viewMapButton.clicked.connect(self.view_map)
        buttons_layout.addWidget(self.viewMapButton)
        self.main_layout.addLayout(buttons_layout)

        # Second row of buttons for adding/deleting columns/rows
        crud_layout = QHBoxLayout()
        self.addColumnButton = QPushButton("Add Column")
        self.addColumnButton.clicked.connect(self.add_column)
        crud_layout.addWidget(self.addColumnButton)
        self.delColumnButton = QPushButton("Delete Selected Column")
        self.delColumnButton.clicked.connect(self.delete_column)
        crud_layout.addWidget(self.delColumnButton)
        self.addRowButton = QPushButton("Add Row")
        self.addRowButton.clicked.connect(self.add_row)
        crud_layout.addWidget(self.addRowButton)
        self.delRowButton = QPushButton("Delete Selected Row")
        self.delRowButton.clicked.connect(self.delete_row)
        crud_layout.addWidget(self.delRowButton)
        self.main_layout.addLayout(crud_layout)

        # Status Bar
        self.statusBar().showMessage("Ready - No shapefile loaded")

        # Internal references
        self.shapefile_path = None
        self.gdf = None
        self.attr_columns = []

    def apply_table_theme(self):
        """Apply styling to the table widget."""
        # Behavior
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.setWordWrap(False)
        self.tableWidget.setShowGrid(True)

        # Sizing
        vh = self.tableWidget.verticalHeader()
        hh = self.tableWidget.horizontalHeader()
        vh.setDefaultSectionSize(28)
        vh.setVisible(False)
        hh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hh.setStretchLastSection(True)
        self.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Stylesheet
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                gridline-color: #444;
                alternate-background-color: #2b2b2b;
                background: #1f1f1f;
                color: #eaeaea;
                selection-background-color: #3a6ea5;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #303030;
                color: #dcdcdc;
                font-weight: 600;
                font-size: 12px;
                padding: 6px 8px;
                border: 0px;
                border-bottom: 2px solid #555;
            }
            QTableCornerButton::section {
                background-color: #303030;
                border: 0px;
                border-bottom: 2px solid #555;
            }
        """)

    def apply_filter(self):
        """Apply text filter to table rows."""
        col_text = self.filterColumnCombo.currentText()
        if col_text in ["--", ""]:
            QMessageBox.warning(self, "Filter Error", "Please select a valid column to filter.")
            return
        filter_text = self.filterLineEdit.text().lower()
        col_index = self.filterColumnCombo.currentIndex()
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, col_index)
            if item is not None:
                cell_text = item.text().lower()
                self.tableWidget.setRowHidden(row, filter_text not in cell_text)

    def clear_filter(self):
        """Clear all filters and show all rows."""
        self.filterLineEdit.clear()
        for row in range(self.tableWidget.rowCount()):
            self.tableWidget.setRowHidden(row, False)

    def open_shapefile(self):
        """Open a shapefile using file dialog."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open Shapefile", "", "Shapefiles (*.shp)"
        )
        if file_path:
            self.load_shapefile(file_path)

    def load_shapefile(self, shp_path):
        """Load shapefile into the application."""
        try:
            gdf = gpd.read_file(shp_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Shapefile:\n{str(e)}")
            return
        self.shapefile_path = shp_path
        self.gdf = gdf
        self.attr_columns = [c for c in self.gdf.columns if c != "geometry"]
        self.populate_table()
        self.statusBar().showMessage(f"Loaded: {shp_path}")

    def populate_table(self):
        """Populate the table widget with shapefile attributes."""
        if self.gdf is None or len(self.attr_columns) == 0:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return
        df_attrs = self.gdf[self.attr_columns].copy()
        num_rows = len(df_attrs)
        num_cols = len(df_attrs.columns)
        self.tableWidget.clear()
        self.tableWidget.setRowCount(num_rows)
        self.tableWidget.setColumnCount(num_cols)
        self.tableWidget.setHorizontalHeaderLabels(df_attrs.columns.tolist())
        for row_idx in range(num_rows):
            for col_idx in range(num_cols):
                val = df_attrs.iat[row_idx, col_idx]
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.tableWidget.setItem(row_idx, col_idx, item)
        self.apply_table_theme()
        self.filterColumnCombo.clear()
        self.filterColumnCombo.addItems(self.attr_columns)

        # Auto size columns
        self.tableWidget.resizeColumnsToContents()
        for col in range(self.tableWidget.columnCount()):
            w = self.tableWidget.columnWidth(col)
            self.tableWidget.setColumnWidth(col, min(max(w, 120), 320))

    def add_column(self):
        """Add a new column to the table."""
        col_name, ok = QInputDialog.getText(self, "New Column", "Enter column name:")
        if not ok or not col_name:
            return
        default_value, ok2 = QInputDialog.getText(
            self, "Default Value", "Enter default value for new column:"
        )
        if not ok2:
            return
        col_index = self.tableWidget.columnCount()
        self.tableWidget.insertColumn(col_index)
        self.tableWidget.setHorizontalHeaderItem(col_index, QTableWidgetItem(col_name))
        row_count = self.tableWidget.rowCount()
        for row in range(row_count):
            item = QTableWidgetItem(default_value)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.tableWidget.setItem(row, col_index, item)
        self.attr_columns.append(col_name)
        self.apply_table_theme()
        self.filterColumnCombo.clear()
        self.filterColumnCombo.addItems(self.attr_columns)

    def delete_column(self):
        """Delete the selected column from the table."""
        col_index = self.tableWidget.currentColumn()
        if col_index < 0:
            QMessageBox.warning(self, "Delete Column", "No column selected.")
            return
        self.tableWidget.removeColumn(col_index)
        if col_index < len(self.attr_columns):
            self.attr_columns.pop(col_index)
        self.apply_table_theme()
        self.filterColumnCombo.clear()
        self.filterColumnCombo.addItems(self.attr_columns)

    def add_row(self):
        """Add a new row to the table."""
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        self.apply_table_theme()

    def delete_row(self):
        """Delete the selected row from the table."""
        row_index = self.tableWidget.currentRow()
        if row_index < 0:
            QMessageBox.warning(self, "Delete Row", "No row selected.")
            return
        self.tableWidget.removeRow(row_index)
        self.apply_table_theme()

    def mass_update(self):
        """Perform mass update operation on selected columns."""
        if self.gdf is None or not len(self.attr_columns):
            QMessageBox.warning(self, "No Data", "No shapefile data loaded.")
            return
        dialog = MassUpdateDialog(self.attr_columns, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_columns = dialog.getSelectedColumns()
            operation = dialog.getOperation()
            value = dialog.getValue()
            for col_idx, col_name in enumerate(self.attr_columns):
                if col_name in selected_columns:
                    for row in range(self.tableWidget.rowCount()):
                        item = self.tableWidget.item(row, col_idx)
                        if item is not None:
                            try:
                                old_val = float(item.text())
                                if operation == "add":
                                    new_val = old_val + value
                                elif operation == "subtract":
                                    new_val = old_val - value
                                elif operation == "multiply":
                                    new_val = old_val * value
                                elif operation == "divide":
                                    if value == 0:
                                        QMessageBox.warning(
                                            self, "Error", "Cannot divide by zero."
                                        )
                                        return
                                    new_val = old_val / value
                                else:
                                    new_val = old_val
                                item.setText(str(new_val))
                            except ValueError:
                                pass
            QMessageBox.information(self, "Success", "Mass update operation applied.")

    def save_shapefile(self):
        """Save the shapefile with current edits."""
        if self.gdf is None:
            QMessageBox.warning(self, "No Shapefile Loaded", "Please open a shapefile first.")
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Shapefile As", self.shapefile_path, "Shapefiles (*.shp)"
        )
        if not save_path:
            return
        records = []
        for row_idx in range(self.tableWidget.rowCount()):
            row_data = {}
            for col_idx, col_name in enumerate(self.attr_columns):
                item = self.tableWidget.item(row_idx, col_idx)
                val_str = item.text() if item else ""
                if col_name in self.gdf.columns and pd.api.types.is_numeric_dtype(
                    self.gdf[col_name]
                ):
                    try:
                        val = float(val_str)
                    except ValueError:
                        val = None
                else:
                    val = val_str
                row_data[col_name] = val
            records.append(row_data)
        updated_df = pd.DataFrame(records, columns=self.attr_columns)
        if "geometry" in self.gdf.columns:
            geom = self.gdf["geometry"]
        else:
            QMessageBox.critical(self, "Error", "No geometry found in the GeoDataFrame.")
            return
        new_gdf = gpd.GeoDataFrame(updated_df, geometry=geom, crs=self.gdf.crs)
        try:
            new_gdf.to_file(save_path, driver="ESRI Shapefile")
            QMessageBox.information(
                self, "Success", f"Shapefile saved successfully:\n{save_path}"
            )
            self.statusBar().showMessage(f"Saved: {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save shapefile:\n{str(e)}")
        self.gdf = new_gdf

    def export_geojson(self):
        """Export the current layer to GeoJSON."""
        if self.gdf is None:
            QMessageBox.warning(self, "No Shapefile Loaded", "Please open a shapefile first.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export GeoJSON", "", "GeoJSON (*.geojson)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".geojson"):
            file_path += ".geojson"
        try:
            self.gdf.to_file(file_path, driver="GeoJSON")
            QMessageBox.information(self, "Export Complete", f"Saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export GeoJSON:\n{str(e)}")

    def export_geopackage(self):
        """Export the current layer to GeoPackage."""
        if self.gdf is None:
            QMessageBox.warning(self, "No Shapefile Loaded", "Please open a shapefile first.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export GeoPackage", "", "GeoPackage (*.gpkg)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".gpkg"):
            file_path += ".gpkg"
        try:
            self.gdf.to_file(file_path, driver="GPKG", layer="data")
            QMessageBox.information(self, "Export Complete", f"Saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export GeoPackage:\n{str(e)}")

    def export_csv_attributes(self):
        """Export attribute table to CSV (no geometry)."""
        if self.gdf is None:
            QMessageBox.warning(self, "No Shapefile Loaded", "Please open a shapefile first.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Attributes CSV", "", "CSV (*.csv)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"
        try:
            df = self.gdf.drop(columns=["geometry"]) if "geometry" in self.gdf.columns else self.gdf
            df.to_csv(file_path, index=False)
            QMessageBox.information(self, "Export Complete", f"Saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{str(e)}")

    def view_map(self):
        """Open the map viewer dialog."""
        if self.gdf is None:
            QMessageBox.warning(self, "No Shapefile Loaded", "Please open a shapefile first.")
            return
        try:
            dlg = MapDialog(self.gdf, parent=self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open map viewer:\n{str(e)}")

    def show_statistics(self):
        """Open the statistics viewer dialog."""
        if self.gdf is None:
            QMessageBox.information(self, "Statistics", "No shapefile loaded.")
            return
        try:
            dlg = StatisticsDialog(self.gdf, parent=self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open statistics:\n{str(e)}")

    def show_about(self):
        """Show the about dialog."""
        dlg = AboutDialog(self)
        dlg.exec()

    def open_spatial_tools(self):
        """Open the spatial tools dialog."""
        if self.gdf is None:
            QMessageBox.warning(self, "No Shapefile Loaded", "Please open a shapefile first.")
            return
        dlg = SpatialToolsDialog(self.gdf, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_gdf is not None:
            self.gdf = dlg.result_gdf
            self.attr_columns = [c for c in self.gdf.columns if c != "geometry"]
            self.populate_table()
            if dlg.status_message:
                self.statusBar().showMessage(dlg.status_message)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
