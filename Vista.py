import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QDialog, QFileDialog, QCheckBox, QMessageBox, QGraphicsScene, QInputDialog
from PyQt5.uic import loadUi
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import cv2

class MyGraphCanvas(FigureCanvas):
    """Clase para realizar gráficos en un layout dado."""
    def __init__(self, layout=None, parent=None, width=20, height=20, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        layout.addWidget(self)

    def graphicate(self, images, columns, titles):
        self.fig.clf()
        i=1
        for image in images:
            self.axes = self.fig.add_subplot(len(images), columns, i)
            self.axes.clear()
            self.axes.imshow(image)
            self.axes.set_title("")
            self.axes.set_title(titles[i-1])
            i+=1

        self.axes.figure.tight_layout()
        self.axes.figure.canvas.draw()
            
class MainMenu(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("mainmenu.ui", self)
        self.setup()
    
    def setup(self):
        self.images_button.clicked.connect(self.openImagesSubMenu)
    
    def set_controller(self, controller):
        self.__my_controller = controller
    
    def openImagesSubMenu(self):
        imagesSubmenu_window = ImagesSubMenu(self)
        imagesSubmenu_window.set_controller(self.__my_controller)
        self.hide()
        imagesSubmenu_window.show()

class ImagesSubMenu(QMainWindow):
    """ Submenu que contiene todas las opciones de procesamiento de imágenes """
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("submenu_imagenes.ui", self)
        self.__my_main_window = parent
        self.setup()
    
    def setup(self):
        self.openclose_button.clicked.connect(self.open_openclose_window)
        self.cutresized_button.clicked.connect(self.open_cutresized_window)
        self.softener_button.clicked.connect(self.open_softener_window)
        self.database_button.clicked.connect(self.open_database_window)
        self.return_button.clicked.connect(self.return_window)
    
    def return_window(self):
        self.hide()
        self.__my_main_window.show()

    def set_controller(self, controller):
        self.__my_controller = controller

    def open_openclose_window(self):
        openclose_window = OpenClosevsCloseOpenWindow(self.__my_controller, self)
        self.hide()
        openclose_window.show()
      
    def open_cutresized_window(self):
        cutresized_window = CutResizedWindow(self.__my_controller, self)
        self.hide()
        cutresized_window.show()

    def open_softener_window(self):
        softener_window = SoftenerWindow(self.__my_controller, self)
        self.hide()
        softener_window.show()

    def open_database_window(self):
        database_window = DatabaseWindow(self.__my_controller, self)
        self.hide()
        database_window.show()

class OpenClosevsCloseOpenWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super(OpenClosevsCloseOpenWindow, self).__init__(parent)
        loadUi("image_processing.ui", self)
        self.setWindowTitle("Apertura - Cierre vs Cierre - Apertura")
        self.__my_main_window = parent
        self.__my_controller = controller
        self.__anonymizer = False
        self.setup()
    
    def setup(self):
        self.sc = MyGraphCanvas(self.graph_area)
        self.cargar_imagenes.clicked.connect(self.load_images)
        self.guardar_imagenes.clicked.connect(self.save_images)
        self.return_button.clicked.connect(self.return_window)
        self.anonimizar.stateChanged.connect(self.checkbox_state_changed)
    
    def return_window(self):
        self.hide()
        self.__my_main_window.show()

    def save_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de destino")

        i = 0
        for file in self.__files:
            if file != None:
                file.save_as(folder + "/" + self.__names[i])
            
            else:
                save_path = folder + "/" + self.__names[i]
                # cv2 no reconoce caracteres especiales, toca hacer esto:
                is_success, array = cv2.imencode(".jpg", self.__images[i])
                array.tofile(save_path)

            i+=1
        
        QMessageBox.information(self, "¡Exito! 😀", f"Imágenes almacenadas correctamente en {folder}.")

        
    def move_image(self, value):
        i = value * 3
        self.sc.graphicate(self.__images[i:i+3], 3, titles=self.__names[i:i+3])
        
    
    def checkbox_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.__anonymizer = True
        
        else:
            self.__anonymizer = False
    
    def load_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        
        if folder != '':
            self.scrollBar.valueChanged.connect(self.move_image)
            self.scrollBar.setSingleStep(1)
            kernel = np.ones((3,3))
            data = self.__my_controller.get_opcl_vs_clop_imgs(kernel, folder, self.__anonymizer)
            self.__images = [image["image"] for image in data]
            self.__names = [image["name"] for image in data]
            self.__files = [image["file"] for image in data]
            self.scrollBar.setMaximum(int(len(self.__images)/3) - 1)
            self.sc.graphicate(self.__images[0:3], 3, titles=self.__names[0:3])

class CutResizedWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super(CutResizedWindow, self).__init__(parent)
        loadUi("image_processing.ui", self)
        self.setWindowTitle("Recorte y Escalado")
        self.__my_main_window = parent
        self.__my_controller = controller
        self.__anonymizer = False
        self.setup()

    def setup(self):
        self.sc = MyGraphCanvas(self.graph_area)
        self.cargar_imagenes.clicked.connect(self.load_images)
        self.guardar_imagenes.clicked.connect(self.save_images)
        self.return_button.clicked.connect(self.return_window)
        self.anonimizar.stateChanged.connect(self.checkbox_state_changed)
    
    def return_window(self):
        self.hide()
        self.__my_main_window.show()

    def save_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de destino")
        i = 0
        for file in self.__files:
            if file != None:
                file.save_as(folder + "/" + self.__names[i])
            
            else:
                save_path = folder + "/" + self.__names[i]
                # cv2 no reconoce caracteres especiales, toca hacer esto:
                is_success, array = cv2.imencode(".jpg", self.__images[i])
                array.tofile(save_path)

            i+=1
        
        QMessageBox.information(self, "¡Exito! 😀", f"Imágenes almacenadas correctamente en {folder}.")

    def move_image(self, value):
        i = value * 3
        self.sc.graphicate(self.__images[i:i+3], 3, titles=self.__names[i:i+3])
        
    
    def checkbox_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.__anonymizer = True
        
        else:
            self.__anonymizer = False
    
    def load_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")

        if folder != '':
            self.scrollBar.valueChanged.connect(self.move_image)
            data = self.__my_controller.get_imgs(folder)
            self.__images = [image["image"] for image in data]

            self.sc.graphicate([self.__images[0]], 1, ["Imágen de ejemplo:"])
            x, ok = QInputDialog.getInt(self, "Rango de corte", "Ingresa una coordenada en X: ")
            y, ok2 = QInputDialog.getInt(self, "Rango de corte", "Ingresa una coordenada en Y: ")
            if ok and ok2:
                x_coord = x
                y_coord = y
                print(type(x_coord))
                print(x_coord)
            else:
                QMessageBox.information(self, "Información", "Ingreso cancelado.")

            data = self.__my_controller.get_cutresized_imgs(folder, x_coord, y_coord, self.__anonymizer)
            self.__images = [image["image"] for image in data]
            self.__names = [image["name"] for image in data]
            self.__files = [image["file"] for image in data]
            self.scrollBar.setMaximum(int(len(self.__images)/3) - 1)
            self.sc.graphicate(self.__images[0:3], 3, titles=self.__names[0:3])

class SoftenerWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super(SoftenerWindow, self).__init__(parent)
        loadUi("image_processing.ui", self)
        self.setWindowTitle("Suavizado")
        self.__my_main_window = parent
        self.__my_controller = controller
        self.__anonymizer = False
        self.setup()
    
    def setup(self):
        self.sc = MyGraphCanvas(self.graph_area)
        self.cargar_imagenes.clicked.connect(self.load_images)
        self.guardar_imagenes.clicked.connect(self.save_images)
        self.return_button.clicked.connect(self.return_window)
        self.anonimizar.stateChanged.connect(self.checkbox_state_changed)
    
    def return_window(self):
        self.hide()
        self.__my_main_window.show()

    def save_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de destino")
        i = 0
        for file in self.__files:
            if file != None:
                file.save_as(folder + "/" + self.__names[i])
            
            else:
                save_path = folder + "/" + self.__names[i]
                # cv2 no reconoce caracteres especiales, toca hacer esto:
                is_success, array = cv2.imencode(".jpg", self.__images[i])
                array.tofile(save_path)

            i+=1
        
        QMessageBox.information(self, "¡Exito! 😀", f"Imágenes almacenadas correctamente en {folder}.")
        
    def move_image(self, value):
        i = value * 4
        self.sc.graphicate(self.__images[i:i+4], 4, titles=self.__names[i:i+4])
        
    
    def checkbox_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.__anonymizer = True
        
        else:
            self.__anonymizer = False
    
    def load_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")

        if folder != '':
            self.scrollBar.valueChanged.connect(self.move_image)
            data = self.__my_controller.get_softened_imgs(folder, self.__anonymizer)
            self.__images = [image["image"] for image in data]
            self.__names = [image["name"] for image in data]
            self.__files = [image["file"] for image in data]
            self.scrollBar.setMaximum(int(len(self.__images)/4) - 1)
            self.sc.graphicate(self.__images[0:4], 4, titles=self.__names[0:4])

class DatabaseWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super(DatabaseWindow, self).__init__(parent)
        loadUi("data_base.ui", self)
        self.__my_main_window = parent
        self.__my_controller = controller
        self.__anonymizer = False
        self.setup()

    def setup(self):
        self.return_button.clicked.connect(self.return_window)
        self.save_button.clicked.connect(self.save_data)
        self.anonimizar.stateChanged.connect(self.checkbox_state_changed)

    def return_window(self):
        self.hide()
        self.__my_main_window.show()
    
    def checkbox_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.__anonymizer = True
        
        else:
            self.__anonymizer = False
    
    def save_data(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")

        button = QMessageBox.question(self, "Almacenamiento", f"A punto de almacenar los datos en {folder}, esto puede tardar unos minutos. Asegurese de tener buena conexión a internet. ¿Continuar?", QMessageBox.Ok | QMessageBox.Cancel)

        if button == QMessageBox.Ok and folder != "":
            self.__my_controller.atlas_save(folder, self.__anonymizer)
            QMessageBox.information(self, "¡Exito! 😀", "Información almacenada correctamente.")

   
    