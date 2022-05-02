#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Template Python module generated based on 'app_template', 'phantasy-ui'
is required to make it executable as a PyQt5 app.

Created by: makeBasePyQtApp.

An example to create an app template:

>>> makeBasePyQtApp --app my_great_app --template AppWindow

Show the available templates:

>>> makeBasePyQtApp -l
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QMainWindow
from phantasy_ui import BaseAppForm
from phantasy_ui.widgets import DataAcquisitionThread as DAQT

import pandas as pd
import numpy as np
from numpy import ndarray
import time
import os

from spectcl.client import Client

from .ui.ui_app import Ui_MainWindow


class MyAppWindow(BaseAppForm, Ui_MainWindow):

    curve_updated = pyqtSignal(ndarray, ndarray)
    xlabel_updated1 = pyqtSignal('QString')
    ylabel_updated1 = pyqtSignal('QString')
    title_updated1 = pyqtSignal('QString')
    xlabel_updated2 = pyqtSignal('QString')
    ylabel_updated2 = pyqtSignal('QString')
    title_updated2 = pyqtSignal('QString')
    image_updated = pyqtSignal(ndarray, ndarray, ndarray)

    def __init__(self, version, **kws):
        super(self.__class__, self).__init__()

        # app version, title
        self.setAppVersion(version)
        self.setAppTitle("My App")

        # app info in about dialog
        # self.app_about_info = "About info of My App."

        # UI
        self.setupUi(self)
        self.postInitUi()

        #
        self._post_init()

    def _post_init(self):
        self.client = Client(
                base_url=os.environ.get('BASE_URL', 'http://127.0.0.1'),
                port=os.environ.get('PORT', 8000)
        )

        self.server_url_lineEdit.setText(self.client._data_client._base_uri)
        self.server_url_lineEdit.returnPressed.emit()

        self.daq_rate_lbl.setVisible(False)
        self.daq_freq_sbox.valueChanged.emit(self.daq_freq_sbox.value())
        #
        self.curve_updated.connect(self.matplotlibcurveWidget.update_curve)
        self.xlabel_updated1.connect(self.matplotlibcurveWidget.setFigureXlabel)
        self.ylabel_updated1.connect(self.matplotlibcurveWidget.setFigureYlabel)
        self.title_updated1.connect(self.matplotlibcurveWidget.setFigureTitle)
        self.xlabel_updated2.connect(self.matplotlibimageWidget.setFigureXlabel)
        self.ylabel_updated2.connect(self.matplotlibimageWidget.setFigureYlabel)
        self.title_updated2.connect(self.matplotlibimageWidget.setFigureTitle)

        #
        self.image_updated.connect(self.on_image_updated)

    def on_image_updated(self, x, y, z):
        # image updated
        print(x.shape, y.shape, z.shape)
        o = self.matplotlibimageWidget
        o.setXData(x)
        o.setYData(y)
        o.update_image(z)

    @pyqtSlot()
    def on_update_data(self):
        """Fetch data and update plot.
        """
        x, y, z = self.fetch_data()
        xylabels = ["Channels", "Channels"]
        if len(self.sparam) == 1:
            xylabels[1] = self.sparam[0]
        elif len(self.sparam) == 2:
            xylabels = self.sparam
        if z is None:
            self.curve_updated.emit(x, y)
            self.xlabel_updated1.emit(xylabels[0])
            self.ylabel_updated1.emit(xylabels[1])
            self.title_updated1.emit(self.title)
        else:
            self.image_updated.emit(x, y, z)
            self.xlabel_updated2.emit(xylabels[0])
            self.ylabel_updated2.emit(xylabels[1])
            self.title_updated2.emit(self.title)

    def fetch_data(self):
        name = self.spectrum_cbb.currentText()
        spec = self.client.get_spectrum(name)
        # spectrum params
        self.sparam = spec.parameters
        self.title = name
        df = spec.data
        if spec.stype == '2D':
            self.tabWidget.setCurrentIndex(1)
            x, y, z = spec.to_image_tuple()
            return x, y, z
        elif spec.stype == '1D':
            self.tabWidget.setCurrentIndex(0)
            x = df.x.to_numpy()
            y = df.v.to_numpy()
            return x, y, None
        else:
            return None, None, None

    @pyqtSlot()
    def on_update_url(self):
        """Update REST URL, update spectrum name list.
        """
        from urllib.parse import urlparse
        url = urlparse(self.server_url_lineEdit.text())
        self.client.base_url = url.scheme + '://' + url.hostname
        self.client.port = url.port

        #
        spectra_list = list(self.client.list('spectrum').index)
        self.spectrum_cbb.clear()
        self.spectrum_cbb.addItems(spectra_list)

    @pyqtSlot(bool)
    def on_toggle_auto_update(self, enabled):
        print("Auto updating is enabled? ", enabled)

        self._daq_stop = not enabled
        self.on_daq_start()

    def on_daq_start(self):
        if self._daq_stop:
            return
        self.daq_th = DAQT(daq_func=self.daq_single, daq_seq=range(1))
        #self.daq_th.started.connect(partial(self.set_widgets_status, "START"))
        #self.daq_th.progressUpdated.connect(self.on_update_daq_status)
        self.daq_th.resultsReady.connect(self.on_daq_results_ready)
        self.daq_th.finished.connect(self.on_daq_start)
        self.daq_th.start()

    def daq_single(self, iiter):
        t0 = time.time()
        x, y, z = self.fetch_data()
        dt = time.time() - t0
        if self._delt - dt >= 0:
            time.sleep(self._delt - dt)
            rate = self._daqfreq
        else:
            print("{} msec is passed.".format(dt * 1000))
            rate = 1.0 / dt
        return x, y, z, rate

    def on_daq_results_ready(self, res):
        x, y, z, rate = res[0]
        if z is None:
            self.curve_updated.emit(x, y)
        else:
            self.image_updated.emit(x, y, z)
        self.daq_rate_lbl.setText("{0:.1f}".format(rate))

    @pyqtSlot(float)
    def on_update_daqrate(self, x):
        self._daqfreq = x
        self._delt = 1.0 / self._daqfreq

def interp_data(x, y, z, method='cubic', nx=100, ny=100):
    from scipy.interpolate import griddata
    x_arr = np.linspace(min(x), max(x), nx)
    y_arr = np.linspace(min(y), max(y), ny)
    xx, yy = np.meshgrid(x_arr, y_arr)
    zz = griddata((x, y), z, (xx, yy), method=method)
    return xx, yy, zz


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    version = 0.1
    app = QApplication(sys.argv)
    w = MyAppWindow(version)
    w.show()
    w.setWindowTitle("This is an app from template")
    sys.exit(app.exec_())
