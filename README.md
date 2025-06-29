# Integrated Nighttime Light Modeling Plugin

## Description

This QGIS plugin facilitates the analysis and modeling of Nighttime Lights (NTL) trends through two main tools:

1. **Nighttime Light Annual Composer**

   * Downloads annual VIIRS-DNB composites (band `avg_rad`) from Google Earth Engine.
   * Clips each composite to the input polygon layer.
   * Exports the results as GeoTIFF files named `VIIRS_YYYY.tif`, packaged in a ZIP archive.

2. **Nighttime Light Regression Modeler**

   * Performs pixel-wise regression modeling of NTL intensity using Linear, Polynomial, Ridge, or Lasso methods.
   * Converts NoData values to 0 and calculates performance metrics (R² and RMSE).
   * Generates predicted NTL rasters for specified future years.
   * Produces a scatter plot comparing actual vs. predicted values.

## Plugin Structure

* `download_viirs_annual.py` – implementation of Nighttime Light Annual Composer fileciteturn1file0.
* `nighttimelight_modeller.py` – implementation of Regression Modeler fileciteturn1file1.
* `metadata.txt` – plugin metadata (name, version, author, dependencies) fileciteturn1file2.

## Installation and Setup

### 1. General Requirements

* QGIS **3.0** or newer.
* Copy the entire `integrated_ntl_modeling` folder to your QGIS plugins directory:

  * **Windows**: `%APPDATA%/QGIS/QGIS3/profiles/default/python/plugins/`
  * **macOS/Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
* Restart QGIS and enable the plugin via **Plugins → Manage and Install Plugins…**, then search for **Integrated Nighttime Light Modeling**.

### 2. Required Python Modules

Install the following libraries in the QGIS Python environment (e.g., via pip):

```bash
pip install earthengine-api numpy rasterio matplotlib scikit-learn
```

* **earthengine-api** – to access Google Earth Engine.
* **numpy** – for numerical array operations.
* **rasterio** – for reading and writing raster data.
* **matplotlib** – for scatter plot visualization.
* **scikit-learn** – for regression modeling and normalization.

### 3. Google Earth Engine Plugin for QGIS

To use Earth Engine data within QGIS:

1. Go to **Plugins → Manage and Install Plugins…**
2. Search for and install **Google Earth Engine**.
3. From the QGIS menu, select **EE Plugin → Authenticate…**
4. Follow the web-based authentication flow to obtain a token.
5. Once authenticated, click **Initialize** in the plugin toolbar if prompted.

## Usage Instructions

### Nighttime Light Annual Composer

1. Launch **Nighttime Light Annual Composer** from the Processing Toolbox.
2. Select the input polygon layer defining your study area.
3. Check the years you wish to download (e.g., 2014–2025).
4. Specify an output folder.
5. Click **Run**. The GeoTIFF files and corresponding ZIP archive will be saved and automatically loaded into QGIS.

### Nighttime Light Regression Modeler

1. Launch **Nighttime Light Regression Modeler**.
2. Select at least two input NTL raster layers (e.g., years 2013–2023).
3. Enter the future years for prediction (e.g., `2028,2033`).
4. Choose the regression model and normalization method.
5. Specify an output folder.
6. Click **Run**. Predicted rasters, performance metrics, and the scatter plot PNG will be saved and the predicted layers added to QGIS.

## Plugin Metadata

Refer to `metadata.txt` for detailed plugin metadata:

* **name**: Integrated Nighttime Light Modeling
* **version**: 1.0.0
* **author**: Firman Afrianto
* **qgisMinimumVersion**: 3.0
* **repository**, **tracker**, **homepage**: GitHub URLs
* **category**, **tags**, **changelog**: categorization and release notes

---

*This README provides all necessary steps to install, configure, and use the Integrated Nighttime Light Modeling plugin.*
# Integrated Nighttime Light Modeling Plugin

## Description

This QGIS plugin facilitates the analysis and modeling of Nighttime Lights (NTL) trends through two main tools:

1. **Nighttime Light Annual Composer**

   * Downloads annual VIIRS-DNB composites (band `avg_rad`) from Google Earth Engine.
   * Clips each composite to the input polygon layer.
   * Exports the results as GeoTIFF files named `VIIRS_YYYY.tif`, packaged in a ZIP archive.

2. **Nighttime Light Regression Modeler**

   * Performs pixel-wise regression modeling of NTL intensity using Linear, Polynomial, Ridge, or Lasso methods.
   * Converts NoData values to 0 and calculates performance metrics (R² and RMSE).
   * Generates predicted NTL rasters for specified future years.
   * Produces a scatter plot comparing actual vs. predicted values.

## Plugin Structure

* `download_viirs_annual.py` – implementation of Nighttime Light Annual Composer fileciteturn1file0.
* `nighttimelight_modeller.py` – implementation of Regression Modeler fileciteturn1file1.
* `metadata.txt` – plugin metadata (name, version, author, dependencies) fileciteturn1file2.

## Installation and Setup

### 1. General Requirements

* QGIS **3.0** or newer.
* Copy the entire `integrated_ntl_modeling` folder to your QGIS plugins directory:

  * **Windows**: `%APPDATA%/QGIS/QGIS3/profiles/default/python/plugins/`
  * **macOS/Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
* Restart QGIS and enable the plugin via **Plugins → Manage and Install Plugins…**, then search for **Integrated Nighttime Light Modeling**.

### 2. Required Python Modules

Install the following libraries in the QGIS Python environment (e.g., via pip):

```bash
pip install earthengine-api numpy rasterio matplotlib scikit-learn
```

* **earthengine-api** – to access Google Earth Engine.
* **numpy** – for numerical array operations.
* **rasterio** – for reading and writing raster data.
* **matplotlib** – for scatter plot visualization.
* **scikit-learn** – for regression modeling and normalization.

### 3. Google Earth Engine Plugin for QGIS

To use Earth Engine data within QGIS:

1. Go to **Plugins → Manage and Install Plugins…**
2. Search for and install **Google Earth Engine**.
3. From the QGIS menu, select **EE Plugin → Authenticate…**
4. Follow the web-based authentication flow to obtain a token.
5. Once authenticated, click **Initialize** in the plugin toolbar if prompted.

## Usage Instructions

### Nighttime Light Annual Composer

1. Launch **Nighttime Light Annual Composer** from the Processing Toolbox.
2. Select the input polygon layer defining your study area.
3. Check the years you wish to download (e.g., 2014–2025).
4. Specify an output folder.
5. Click **Run**. The GeoTIFF files and corresponding ZIP archive will be saved and automatically loaded into QGIS.

### Nighttime Light Regression Modeler

1. Launch **Nighttime Light Regression Modeler**.
2. Select at least two input NTL raster layers (e.g., years 2013–2023).
3. Enter the future years for prediction (e.g., `2028,2033`).
4. Choose the regression model and normalization method.
5. Specify an output folder.
6. Click **Run**. Predicted rasters, performance metrics, and the scatter plot PNG will be saved and the predicted layers added to QGIS.

## Plugin Metadata

Refer to `metadata.txt` for detailed plugin metadata:

* **name**: Integrated Nighttime Light Modeling
* **version**: 1.0.0
* **author**: Firman Afrianto
* **qgisMinimumVersion**: 3.0
* **repository**, **tracker**, **homepage**: GitHub URLs
* **category**, **tags**, **changelog**: categorization and release notes

---

