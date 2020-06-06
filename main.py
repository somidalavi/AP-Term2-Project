import Gui
import sys
import Model
from PySide2 import QtCore, QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    model = Model.main_model;
    window = Gui.MainWindow(model)
    window.show()
    sys.exit(app.exec_());
