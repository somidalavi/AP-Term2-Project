import Gui
import sys
import Model
from PySide2 import QtCore, QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    """dialog = QtWidgets.QFileDialog(None);
    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile);
    dialog.exec_();"""
    
    Model.main_model.init();
    window = Gui.MainWindow()
    window.show()
    sys.exit(app.exec_());
