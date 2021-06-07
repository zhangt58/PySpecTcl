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

from spectcl.client import DataClient

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
        self.client = DataClient()
        self.server_url_lineEdit.setText(self.client._base_uri)
        #self.server_url_lineEdit.returnPressed.emit()

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

        self.cb = None

    def on_image_updated(self, x, y, z):
        # image updated
        o = self.matplotlibimageWidget
        o.setXData(x)
        o.setYData(y)
        o.update_image(z)
        
        if self.cb is not None:
            self.cb.remove()
            self.cb = None

        self.cb = o.figure.colorbar(o._spath, aspect=20, shrink=0.95, pad=0.08, fraction=0.05)
        self.cb.ax.zorder = -1


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
        data = self.client.get('contents', name=name)
        df = pd.DataFrame.from_dict(data['channels'])
        # spectrum type
        stype = self.spectra_dict[name][0]
        # spectrum params
        self.sparam = self.spectra_dict[name][1]
        self.title = name
        if stype in ('1', 'S',):
            self.tabWidget.setCurrentIndex(0)
            x = df.x.to_numpy()
            y = df.v.to_numpy()
            return x, y, None
        elif stype == '2':
            self.tabWidget.setCurrentIndex(1)
            x = df.x.to_numpy()
            y = df.y.to_numpy()
            z = df.v.to_numpy()
            return x, y, z

    @pyqtSlot()
    def on_update_url(self):
        """Update REST URL, update spectrum name list.
        """
        from urllib.parse import urlparse
        url = urlparse(self.server_url_lineEdit.text())
        self.client._base_url = url.scheme + '://' + url.hostname
        self.client._port = url.port
        self.client.update_base_uri()

        #
        self.spectra_dict = {i['name']: (i['type'], i['parameters']) for i in self.client.get('list')}
        self.spectrum_cbb.clear()
        self.spectrum_cbb.addItems(self.spectra_dict.keys())

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
