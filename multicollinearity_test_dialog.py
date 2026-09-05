# -*- coding: utf-8 -*-
import os
from qgis.PyQt import uic, QtWidgets

# Memuat file .ui secara dinamis
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'multicollinearity_test_dialog_base.ui'),
    from_imports=True,
    import_from='multicollinearity_test')


class multicollinearity_testDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        # Penulisan super() khas Python 3 modern (tanpa menyebutkan nama class secara manual)
        super().__init__(parent)
        self.setupUi(self)