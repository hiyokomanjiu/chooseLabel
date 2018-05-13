# -*- coding:utf-8 -*-

import os
import sys
from PyQt5 import QtWidgets
from mainWindow import Ui_MainWindow

# matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
from skimage import io
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops

class Application(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(Application, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # enable drag and drop
        self.setAcceptDrops(True)

        # set matplotlib FigureCanvas
        self.fig = Figure()
        self.FigureCanvas = FigureCanvas(self.fig)
        self.ax1 = self.fig.add_subplot(1,1,1)
        self.ax1.set_axis_off()
        self.ui.imageLayout.addWidget(self.FigureCanvas)

        # button
        self.ui.pushButton_save.clicked.connect(self.onClick_save)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/uri-list'):
            e.accept()
        else:
            e.ignore()
    
    def dropEvent(self, e):
        # ファイルパスを取得する
        urls = e.mimeData().text().split("\n")
        self.filepath = urls[0][8:]

        # display image
        self.image = io.imread(self.filepath)
        self.binimage = self.image > threshold_otsu(self.image)

        # labeling
        self.label = label(self.binimage)
        for l in regionprops(self.label):
            # add item
            item = QtWidgets.QListWidgetItem(str(l.label))
            self.ui.listWidget.addItem(item)
        
        self.plotImage()

        self.ui.listWidget.itemSelectionChanged.connect(self.onItemSelectionChanged)

    def plotImage(self):
        # image
        self.viewImage = np.zeros(self.image.shape)
        for item in self.ui.listWidget.selectedItems():
            l = int(item.text())
            self.viewImage[self.label == l] = 1

        self.ax1.clear()
        self.ax1.imshow(self.viewImage, cmap='gray')
        self.ax1.set_axis_off()

        # redraw
        self.FigureCanvas.draw()
    
    def onClick_save(self):
        # show file chooser
        savename = QtWidgets.QFileDialog.getSaveFileName(self, 'save file', os.path.dirname(self.filepath), "PNG Image (*.png)")
        if savename[0]:
            print(savename[0])
            io.imsave(savename[0], self.viewImage * 255)
    
    def onItemSelectionChanged(self):
        self.plotImage()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())
