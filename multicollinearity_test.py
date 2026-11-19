# -*- coding: utf-8 -*-
import os.path
import csv
import numpy as np

from qgis.PyQt.QtCore import QLocale, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon, QCursor
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QApplication
from qgis.core import (
    QgsSettings, 
    QgsRasterLayer, 
    QgsMessageLog,
    Qgis
)
from qgis.gui import QgsFileWidget 

import processing

from .multicollinearity_test_dialog import multicollinearity_testDialog


class multicollinearity_test:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QgsSettings().value('locale/userLocale', QLocale().name())[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Multicollinearity Test')
        self.first_start = None

    def tr(self, message):
        return QCoreApplication.translate('multicollinearity_test', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Multicollinearity Test (Pearson)'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Multicollinearity Test'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        # PERBAIKAN FLAKE8: Menggunakan "is True"
        if self.first_start is True:
            self.first_start = False
            self.dlg = multicollinearity_testDialog()

        self.dlg.show()
        result = self.dlg.exec()
        
        if result:
            raw_paths = self.dlg.rasterInput.filePath()
            raster_files = QgsFileWidget.splitFilePaths(raw_paths)
            r_threshold = self.dlg.rThreshold.value()
            reproject_crs = self.dlg.chkReproject.isChecked()
            output_csv = self.dlg.csvOutput.filePath()
            
            if len(raster_files) < 2:
                QMessageBox.warning(self.iface.mainWindow(), "Warning", "Please select at least 2 raster files!")
                return
            if not output_csv:
                QMessageBox.warning(self.iface.mainWindow(), "Warning", "Please specify the output CSV file location!")
                return

            # PERBAIKAN Qt6: Menggunakan Qt.CursorShape.WaitCursor
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
            
            try:
                layers = []
                base_layer = None
                
                # --- LOGIKA 1: ALIGNMENT EXTENT, RESOLUSI, DAN CRS ---
                for path in raster_files:
                    layer = QgsRasterLayer(path, os.path.basename(path))
                    if not layer.isValid():
                        # PERBAIKAN Qt6: Menggunakan Qgis.MessageLevel.Warning
                        QgsMessageLog.logMessage(f"Invalid raster layer: {path}", "Multicollinearity Test", Qgis.MessageLevel.Warning)
                        continue
                        
                    if base_layer is None:
                        # Jadikan raster pertama sebagai patokan ukuran dan koordinat
                        base_layer = layer
                        layers.append(layer)
                        continue
                    
                    # Ekstrak informasi dari base_layer
                    base_crs = base_layer.crs()
                    b_ext = base_layer.extent()
                    extent_str = f"{b_ext.xMinimum()},{b_ext.xMaximum()},{b_ext.yMinimum()},{b_ext.yMaximum()}"
                    target_res = base_layer.rasterUnitsPerPixelX()

                    # Gunakan GDAL Warp untuk memaksa extent dan resolusi agar sama persis
                    target_crs = base_crs if reproject_crs else layer.crs()
                    params = {
                        'INPUT': layer,
                        'TARGET_CRS': target_crs,
                        'TARGET_EXTENT': extent_str,
                        'TARGET_RESOLUTION': target_res,
                        'OUTPUT': 'TEMPORARY_OUTPUT'
                    }
                    
                    aligned = processing.run("gdal:warpreproject", params)
                    aligned_layer = QgsRasterLayer(aligned['OUTPUT'], layer.name() + "_aligned")
                    layers.append(aligned_layer)

                # --- LOGIKA 2: EKSTRAKSI ARRAY ---
                arrays = []
                layer_names = []
                nodata_values = []
                
                for layer in layers:
                    provider = layer.dataProvider()
                    extent = layer.extent()
                    cols = layer.width()
                    rows = layer.height()
                    
                    block = provider.block(1, extent, cols, rows)
                    
                    # Konversi ke dtype float agar np.isnan() bisa bekerja dengan aman pada TIF
                    arr = np.array([block.value(row, col) for row in range(rows) for col in range(cols)], dtype=float)
                    nodata = provider.sourceNoDataValue(1)
                    
                    arrays.append(arr)
                    nodata_values.append(nodata)
                    layer_names.append(layer.name())

                # Karena sudah di-align oleh GDAL, ukuran array pasti 100% sama. 
                # Tidak perlu lagi dipotong menggunakan min_len.
                data_matrix = np.vstack(arrays)
                
                # --- LOGIKA 3: MASKING NaN DAN NoData SERENTAK ---
                valid_pixels_mask = np.ones(data_matrix.shape[1], dtype=bool)
                for i, nodata in enumerate(nodata_values):
                    # Filter 1: Buang nilai NaN bawaan file (biasanya dari format TIF)
                    valid_pixels_mask &= ~np.isnan(data_matrix[i])
                    
                    # Filter 2: Buang nilai metadata NoData (misal: -9999)
                    if nodata is not None:
                        valid_pixels_mask &= (data_matrix[i] != nodata)
                
                clean_data_matrix = data_matrix[:, valid_pixels_mask]
                
                if clean_data_matrix.shape[1] == 0:
                    raise ValueError("All pixels resulted in NoData/NaN after alignment. Check your raster extents and overlaps.")

                # Kalkulasi Pearson r
                corr_matrix = np.corrcoef(clean_data_matrix)

                # Ekspor ke CSV
                with open(output_csv, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Variable'] + layer_names)
                    
                    for i in range(len(layer_names)):
                        row = [layer_names[i]]
                        for j in range(len(layer_names)):
                            val = corr_matrix[i, j]
                            if abs(val) >= r_threshold and i != j:
                                row.append(f"{val:.4f} *")
                            else:
                                row.append(f"{val:.4f}")
                        writer.writerow(row)
                
                QMessageBox.information(self.iface.mainWindow(), "Success", f"Analysis complete! CSV saved at:\n{output_csv}")

            except Exception as e:
                import traceback
                # PERBAIKAN Qt6: Menggunakan Qgis.MessageLevel.Critical
                QgsMessageLog.logMessage(traceback.format_exc(), "Multicollinearity Test", Qgis.MessageLevel.Critical)
                QMessageBox.critical(self.iface.mainWindow(), "Error", f"A computational error occurred. See QGIS Message Log for details.\n\nError: {str(e)}")
            
            finally:
                QApplication.restoreOverrideCursor()