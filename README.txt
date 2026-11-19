================================================================================
MULTICOLLINEARITY TEST - RASTER PEARSON CORRELATION ANALYZER (QGIS PLUGIN)
================================================================================

Multicollinearity Test (multicollinearity_test) is a Python-based QGIS plugin
(QGIS 3.0+) designed to evaluate multicollinearity among spatial predictor
variables in raster format. By computing pairwise Pearson correlation
coefficients (r) across multiple raster layers and flagging pairs exceeding a
user-defined |r| threshold, this tool helps researchers and GIS analysts
screen environmental covariates prior to statistical, ecological, or machine
learning modeling.

--------------------------------------------------------------------------------
KEY FEATURES
--------------------------------------------------------------------------------
1. Multi-Raster Pearson Correlation Matrix
   - Accepts two or more raster layers of any GDAL-supported format (e.g.,
     GeoTIFF, ASCII, IMG).
   - Computes an N x N symmetric Pearson correlation matrix (r) across all
     selected raster variables.

2. Automatic CRS Harmonization (Optional)
   - Automatically detects Coordinate Reference System (CRS) mismatches against
     the first input raster and reprojects differing layers on-the-fly using
     gdal:warpreproject.

3. Simultaneous Pixel-Wise NoData Masking
   - Extracts raster band values and applies a unified boolean mask so that
     NoData pixels in ANY input raster are excluded simultaneously across all
     layers, preventing skewed or invalid correlation coefficients.

4. Threshold-Based Collinearity Flagging & CSV Export
   - Evaluates absolute correlation values against a user-specified threshold
     (|r| >= r_threshold) for off-diagonal pairs (i != j).
   - Exports a formatted CSV table with 4-decimal precision and marks
     collinear variable pairs with an asterisk (*).

5. PyQt6 Ready & Robust Error Diagnostics
   - Fully compatible with modern QGIS builds (PyQt5 and PyQt6), featuring
     wait-cursor processing feedback and detailed traceback logging in the
     QGIS Message Log.

--------------------------------------------------------------------------------
METHODOLOGY
--------------------------------------------------------------------------------
For two raster variables X and Y evaluated over n mutually valid (non-NoData)
pixels, the Pearson correlation coefficient r_XY is computed as:

  r_XY = sum((X_k - mean(X)) * (Y_k - mean(Y))) /
         (sqrt(sum((X_k - mean(X))^2)) * sqrt(sum((Y_k - mean(Y))^2)))

Any pair of distinct variables (i != j) satisfying |r_ij| >= r_threshold is
flagged with an asterisk (*) in the output CSV matrix (common modeling
thresholds are |r| >= 0.70 or |r| >= 0.80).

--------------------------------------------------------------------------------
INSTALLATION
--------------------------------------------------------------------------------
Method 1: Install from ZIP in QGIS
  1. Compress the "multicollinearity_test" plugin folder into a .zip archive
     (ensure "multicollinearity_test/" is the single root folder inside).
  2. Open QGIS (version 3.0 or higher) and go to Plugins -> Manage and Install
     Plugins... -> Install from ZIP.
  3. Browse to the .zip file and click Install Plugin.

Method 2: Manual Installation
  1. Copy the "multicollinearity_test" folder into your active QGIS user
     profile plugins directory:
     - Windows : C:\Users\<Username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
     - Linux   : ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
     - macOS   : ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
  2. Restart QGIS and enable "Multicollinearity Test" under Installed plugins.

--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------
1. Prepare Raster Layers:
   Ensure your predictor rasters cover the same spatial extent and grid
   resolution (if CRS differs, enable the reprojection checkbox in the dialog).

2. Launch Plugin:
   Click the "Multicollinearity Test (Pearson)" icon on the toolbar or open
   Plugins -> Multicollinearity Test.

3. Configure Inputs:
   - Select at least 2 raster files in the raster input selector.
   - Set the Correlation Threshold (r) (e.g., 0.70 or 0.80).
   - Check Reproject CRS if your input rasters use different coordinate systems.
   - Specify the Output CSV file path.

4. Run Analysis:
   Click OK. Once complete, open the exported .csv file to inspect the
   correlation matrix and review any variable pairs marked with (*).

--------------------------------------------------------------------------------
CHANGELOG
--------------------------------------------------------------------------------
Version 1.0.0
- Added PyQt6 compatibility (updated dialog execution and cursor handling).
- Implemented simultaneous pixel-wise NoData masking across all input rasters
  for accurate correlation computation.
- Added optional automatic CRS reprojection to align rasters with the base
  layer.
- Added full traceback logging to QGIS Message Log and wait-cursor progress
  feedback.

Version 0.0.1
- Initial release of Multicollinearity Test plugin.

--------------------------------------------------------------------------------
AUTHOR & CONTACT
--------------------------------------------------------------------------------
Author : Muhammad Parif (IPB University)
Email  : payip28muhammad@apps.ipb.ac.id
GitHub : https://github.com/muhammad-parif
================================================================================