import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QDialog, QFileDialog, QCheckBox, QMessageBox, QGraphicsScene 
from PyQt5.uic import loadUi
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import numpy as np

class MyGraphCanvas(FigureCanvas):
    def __init__(self, layout=None, parent=None, width=20, height=100, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = self.fig.add_subplot(111)       
        FigureCanvas.__init__(self, self.fig)
        self.scene = QGraphicsScene()
        layout.setScene(self.scene)
        self.scene.addWidget(self)
    
    def graphicate(self, images, columns):
        i=1
        for image in images:
            self.axes = self.fig.add_subplot(len(images), columns, i)
            self.axes.clear()
            self.axes.imshow(image)
            self.axes.figure.canvas.draw()
            i+=1

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("padre_prueba.ui", self)
        self.setup()
    
    def set_controller(self, controller):
        self.__my_controller = controller

    def open_openclose_window(self):
        openclose_window = OpenClosevsCloseOpenWindow(self.__my_controller, self)
        self.hide()
        openclose_window.show()
      
    def setup(self):
        self.boton_prueba.clicked.connect(self.open_openclose_window)
    
    
class OpenClosevsCloseOpenWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super(OpenClosevsCloseOpenWindow, self).__init__(parent)
        loadUi("opcl_vs_clop.ui", self)
        self.__my_main_window = parent
        self.__my_controller = controller
        self.__anonymizer = False
        self.setup()
    
    def setup(self):
        self.sc = MyGraphCanvas(self.graph_area, width=20, height=100, dpi=100)
        self.cargar_imagenes.clicked.connect(self.load_image)
        self.anonimizar.stateChanged.connect(self.checkbox_state_changed)
    
    def checkbox_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.__anonymizer = True
        
        else:
            self.__anonymizer = False
    
    def load_image(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        
        if folder != '':
            kernel = np.ones((3,3))
            data = self.__my_controller.get_opcl_vs_clop_imgs(kernel, folder, self.__anonymizer)
            images = [image["image"] for image in data]
            self.sc.graphicate(images, 3)

#TODO: Cambiar esa cochinada de forma en que se muestran las imágenes, quizas con flechas.
#TODO: Añadir el resto de vistas para el resto de funciones.
#TODO: Añadir la función de anonimizar y de guardar imágenes.
