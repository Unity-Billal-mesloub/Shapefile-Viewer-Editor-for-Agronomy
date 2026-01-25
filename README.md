# Shapefile Editor v1.1

![Version](https://img.shields.io/badge/version-1.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive desktop application for viewing, editing, and analyzing ESRI Shapefiles. Designed specifically for agronomists and GIS professionals working with agricultural and spatial data.

**Developer:** Bobby Azad
**Release Date:** January 25, 2026
**Version:** 1.1

---

## ✨ Features

### 🗺️ Interactive Map Viewer
- **Google Maps-like navigation** with smooth pan and zoom
- **Mouse wheel zoom** centered on cursor position
- **Real-time satellite basemap** integration using Esri World Imagery
- **Dynamic tile loading** - basemap tiles reload automatically when navigating
- **Multiple colormaps** for data visualization
- **Transparency control** for overlay layers
- **Arrow key navigation** for precise positioning

### 📊 Attribute Table Editor
- **Full-featured table editor** with sortable columns
- **Add/Delete columns and rows** dynamically
- **Mass update operations** - apply arithmetic operations to multiple columns
- **Text filtering** - quickly find features by attribute values
- **Dark-themed interface** for comfortable long-term use
- **Auto-sizing columns** for optimal viewing

### 📈 Advanced Statistics
- **Tabbed interface** with multiple analysis views
- **General information** - feature count, geometry types, CRS details
- **Spatial information** - bounding box, area statistics
- **Attribute statistics** - data types, unique values, min/max ranges
- **Visual charts** - histograms, pie charts, and spatial overviews
- **Export-ready** statistical summaries

### ðŸ§­ Spatial Tools
- **Buffer, dissolve, clip, intersect, union** operations
- **Calculate area and length** attributes
- **Automatic CRS alignment** for overlay tools

### ðŸ“¦ Export & Sharing
- **Export GeoJSON** for web and GIS workflows
- **Export GeoPackage** for modern GIS storage
- **Export CSV (attributes only)** for spreadsheets
- **Export map view** to PNG/PDF

### ðŸ–¨ï¸ Print & Layout
- **Layout designer** with title, legend, scale bar, and north arrow
- **High-quality PNG/PDF output** for reports

### 🎨 Professional UI
- **Modern interface** with intuitive controls
- **Keyboard shortcuts** for common operations
- **Status bar** with real-time feedback
- **High-end About dialog** with full application information
- **Modular architecture** for easy maintenance and extension

---

## 📦 Installation

### Prerequisites
- **Python 3.12** or compatible version
- **pixi** package manager (recommended) or conda

### Using Pixi (Recommended)

1. **Install Pixi** (if not already installed):
   ```bash
   curl -sSL https://prefix.dev/install.sh | bash
   ```

2. **Clone or download** this repository:
   ```bash
   git clone <repository-url>
   cd Shapefile-Viewer-Editor-for-Agronomy
   ```

3. **Install dependencies** using pixi:
   ```bash
   pixi install
   ```

4. **Run the application**:
   ```bash
   pixi run python main.py
   ```

### Manual Installation with Conda

If you prefer using conda directly:

1. **Create a new environment**:
   ```bash
   conda create -n shapefile-editor python=3.12
   conda activate shapefile-editor
   ```

2. **Install dependencies**:
   ```bash
   conda install -c conda-forge geopandas contextily matplotlib-base pyside6
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

---

## 🔧 Dependencies

The application uses the following packages (all managed through conda-forge):

| Package | Version | Purpose |
|---------|---------|---------|
| **python** | 3.12.* | Programming language |
| **geopandas** | >=1.1.1, <2 | Geospatial data handling |
| **contextily** | >=1.6.2, <2 | Basemap tile provider |
| **matplotlib-base** | >=3.8.0, <4 | Plotting and visualization |
| **pyside6** | >=6.6.0, <7 | Qt6 GUI framework |

Additional dependencies installed automatically:
- **pandas** - Data manipulation
- **shapely** - Geometric operations
- **pyproj** - Coordinate system transformations
- **rasterio** - Raster data support

---

## 🚀 Usage

### Quick Start

1. **Launch the application**:
   ```bash
   pixi run python main.py
   ```

2. **Open a shapefile**:
   - Click `File → Open Shapefile` (or press `Ctrl+O`)
   - Navigate to your `.shp` file
   - The attribute table will load automatically

3. **View on map**:
   - Click the `View Map` button
   - Use your mouse to pan (drag) and zoom (scroll wheel)
   - Use the toolbar buttons for additional navigation tools

4. **Edit attributes**:
   - Click any cell in the table to edit
   - Use `Add Column` or `Delete Column` buttons
   - Apply filters to find specific features

5. **Save changes**:
   - Click `File → Save Shapefile As...` (or press `Ctrl+S`)
   - Choose a new location or overwrite the original

### Key Features Guide

#### 🗺️ Map Navigation
- **Mouse Wheel**: Zoom in/out centered on cursor
- **Pan Tool** (toolbar): Drag to move the map
- **Zoom Tool** (toolbar): Click and drag to zoom to rectangle
- **Arrow Buttons**: Pan in cardinal directions
- **Reset View**: Return to original extent
- **Zoom Slider**: Fine-tune zoom level
- **Transparency Slider**: Adjust overlay opacity

#### 🔄 Mass Update Operations
1. Click `Mass Update` button
2. Select columns to update
3. Choose operation: Add, Subtract, Multiply, or Divide
4. Enter value
5. Click OK to apply

#### 📊 Statistics Viewer
- Access via `Tools → Show Statistics` (or press `Ctrl+T`)
- **General Info**: Dataset overview
- **Spatial Info**: Bounding box and area calculations
- **Attributes**: Detailed column statistics
- **Charts**: Visual analysis with histograms and plots

#### ðŸ§­ Spatial Tools
- Access via `Tools â†’ Spatial Tools`
- **Buffer**: Create offset geometries
- **Dissolve**: Merge features by attribute
- **Clip/Intersect/Union**: Overlay with another layer
- **Area/Length**: Add measurement fields to attributes

#### ðŸ“¦ Exporting
- `File â†’ Export GeoJSON...`
- `File â†’ Export GeoPackage...`
- `File â†’ Export Attributes CSV...`
- `Map Viewer â†’ Export PNG/PDF`

#### ðŸ–¨ï¸ Layout Designer
- `Map Viewer â†’ Layout Designer`
- Add **title, legend, scale bar, and north arrow**
- Export layout to **PNG/PDF**

---

## 📁 Project Structure

```
Shapefile-Viewer-Editor-for-Agronomy/
│
├── main.py                    # Main application entry point
├── map_viewer.py              # Interactive map viewer module
├── statistics_viewer.py       # Enhanced statistics module
├── about_dialog.py            # Professional About dialog
├── spatial_tools.py           # Spatial tools dialog
├── layout_designer.py         # Map layout designer
├── pixi.toml                  # Pixi package configuration
├── pixi.lock                  # Locked dependency versions
├── README.md                  # This file
│
└── .pixi/                     # Pixi environment (auto-generated)
    └── envs/default/          # Virtual environment
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Shapefile |
| `Ctrl+S` | Save Shapefile As... |
| `Ctrl+T` | Show Statistics |
| `Ctrl+Q` | Exit Application |
| `F1` | About Dialog |

---

## 📄 Supported Formats

### Input
- **ESRI Shapefile** (.shp with associated .shx, .dbf, .prj files)
- All geometry types: Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon

### Output
- **ESRI Shapefile** (.shp format)

### Coordinate Systems
- Automatic detection of CRS from .prj file
- On-the-fly reprojection to Web Mercator (EPSG:3857) for basemap display
- Preserves original CRS when saving

---

## 💻 System Requirements

- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB+ recommended for large datasets)
- **Disk Space**: ~500MB for application and dependencies
- **Display**: 1280x720 minimum resolution
- **Internet**: Required for downloading basemap tiles

---

## ⚠️ Known Limitations

- Basemap tiles require internet connection
- Very large shapefiles (>100,000 features) may experience slow rendering
- Complex polygons may take time to draw on initial map load
- Area calculations only accurate for projected coordinate systems

---

## 🔧 Troubleshooting

### Application won't start
- Ensure pixi is installed: `pixi --version`
- Try reinstalling dependencies: `pixi install --force`
- Check Python version: `pixi run python --version`

### Basemap not loading
- Check internet connection
- Firewall may be blocking tile requests
- Try switching to a different basemap provider (code modification required)

### Shapefile won't open
- Ensure all required files are present (.shp, .shx, .dbf)
- Check file permissions
- Verify shapefile is not corrupted using QGIS or another GIS tool

### Performance issues
- Close other applications to free memory
- Try filtering data to show fewer features
- Consider simplifying complex geometries

---

## 📚 Who Is It For?

- **Agronomists** managing crop zones or soil regions
- **Researchers** analyzing field boundaries and agricultural zones
- **Farmers** needing a simple tool to adjust field maps
- **GIS enthusiasts** looking for an easy, free alternative to edit shapefiles
- **Students** learning about geospatial data analysis

---

## 📝 Version History

### Version 1.1 (January 25, 2026)
- ✨ Upgraded from PyQt5 to PySide6 (Qt6)
- 🗺️ Added Google Maps-like navigation with dynamic basemap loading
- 🖱️ Implemented mouse wheel zoom centered on cursor
- 📦 Created modular architecture with separate files
- 📊 Enhanced statistics viewer with tabbed interface and charts
- 🎨 Professional About dialog
- 💅 Improved UI with better styling
- ⌨️ Added keyboard shortcuts
- 🔧 Updated dependencies to latest stable versions

### Version 1.0 (Initial Release)
- Basic shapefile viewing and editing
- Simple map viewer
- Attribute table editor
- Mass update operations

---

## 🤝 Contributing

This is a specialized tool developed for agronomic applications. If you find bugs or have feature requests, please open an issue or contact the developer.

---

## 📜 License

This software is provided as-is for educational and professional use in agronomy and GIS analysis.

---

## 👨‍💻 Developer

**Bobby Azad**
Shapefile Editor for Agronomy
Version 1.1
Released: January 25, 2026

---

## 🙏 Acknowledgments

Built with:
- **Python** - Programming language
- **PySide6** - Qt6 Python bindings
- **GeoPandas** - Geospatial data processing
- **Matplotlib** - Data visualization
- **Contextily** - Basemap tile provider
- **Esri** - World Imagery basemap tiles

---

**Enjoy editing your shapefiles!** 🌾🗺️
