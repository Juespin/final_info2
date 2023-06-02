from Modelo import Image_processing 
import Vista
import Modelo
import sys
from PyQt5.QtWidgets import QApplication

class Controller(object):
    def __init__(self, vista, model):
        self.__my_vista = vista
        self.__my_model = model

    def get_opcl_vs_clop_imgs(self, kernel, image, anonymize):
        data = self.__my_model.close_open_vs_open_close(kernel, image, anonymize)
        return data

def main():
    app = QApplication(sys.argv)
    mi_vista = Vista.MainMenu()
    mi_modelo = Modelo.Image_processing()
    mi_controlador = Controller(mi_vista, mi_modelo)
    mi_vista.set_controller(mi_controlador)
    mi_vista.show()
    sys.exit(app.exec_())    
    
if __name__ == "__main__":
    main()   