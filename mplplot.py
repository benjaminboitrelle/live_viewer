import numpy as np

import matplotlib
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.colorbar import make_axes, Colorbar

class MplPlotCanvas(FigureCanvas):
 
    matplotlib.rcParams.update({'font.size': 8})
    cbar_numticks = 9

    def __init__(self, parent=None, dpi=100):

        self.figure = Figure(dpi=dpi)
        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xticks([])
        self.axes.set_yticks([])

        self.img_range = ()
        self.img_shape = None
        self.img_obj = None
        self.colorbar = None

        self.render_frame(np.zeros((10, 10), dtype=np.uint16), min_val=0, max_val=4096)
        self.figure.tight_layout()

    def render_frame(self, img_data, min_val=None, max_val=None):

        # If the minimum and/or maximum values are not defined, determine from the 
        # incoming image data
        if min_val is None:
            min_val = np.amin(img_data)
        if max_val is None:
            max_val = np.amax(img_data)

        # If the shape of the incoming data has changed, delete the image object to force
        # a redraw
        if self.img_shape != img_data.shape:
            self.img_shape = img_data.shape
            self.img_obj = None

        # If no image object exists, draw one and add a colorbar
        if self.img_obj is None:
            self.img_obj = self.axes.imshow(
                img_data, interpolation='nearest', vmin=min_val, vmax=max_val, cmap='jet')

            if self.colorbar is None:
                cbar_ticks = np.linspace(
                    min_val, max_val, self.cbar_numticks, dtype=np.uint).tolist()
                self.colorbar = self.figure.colorbar(
                    self.img_obj, ax=self.axes, orientation='vertical', ticks=cbar_ticks)

        # Otherwise just update the image data for speed
        else:
            self.img_obj.set_data(img_data)
            self.axes.draw_artist(self.img_obj)

        # If the range of the data changed, update the colorbar accordingly
        if self.img_range != (min_val, max_val):
            self.img_range = (min_val, max_val)
            cbar_ticks = np.linspace(min_val, max_val, self.cbar_numticks, dtype=np.uint).tolist()
            self.colorbar.set_clim(min_val, max_val)
            self.colorbar.set_ticks(cbar_ticks)
            self.colorbar.draw_all()

        # Draw the frame
        self.draw()

class MplNavigationToolbar(NavigationToolbar):

    def __init__(self, canvas, parent, coordinates=True):

        super(MplNavigationToolbar, self).__init__(canvas, parent, coordinates)