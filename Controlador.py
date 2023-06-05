from Modelo import Image_processing 
import Vista
import Modelo
import sys
from PyQt5.QtWidgets import QApplication

class Controller(object):   
    def __init__(self, vista, model):
        self.__my_vista = vista
        self.__my_model = model
    
    def save_user(self, user, password):
        return self.__my_model.crear_usuario(user, password)

    def login(self, user, password):
        return self.__my_model.validar_credenciales(user, password)

    def get_imgs(self, images, anonymize=False):
        data = self.__my_model.load_folder(images, anonymize)
        return data

    def get_opcl_vs_clop_imgs(self, kernel, images, anonymize):
        data = self.__my_model.close_open_vs_open_close(kernel, images, anonymize)
        return data

    def get_cutresized_imgs(self, images, x, y, anonymize):
        data = self.__my_model.cut_and_resized(images, x, y, anonymize)
        return data
    
    def get_softened_imgs(self, images, anonymize):
        data = self.__my_model.suavizado(images, anonymize)
        return data

    def atlas_save(self, images, anonymize):
        self.__my_model.pymongo_save(images, anonymize)
    
def main():
    app = QApplication(sys.argv)
    mi_vista = Vista.LoginWindow()
    mi_modelo = Modelo.Image_processing()
    mi_controlador = Controller(mi_vista, mi_modelo)
    mi_vista.set_controller(mi_controlador)
    mi_vista.show()
    sys.exit(app.exec_())    
    
if __name__ == "__main__":
    main()   