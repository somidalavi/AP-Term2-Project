import Gui
import sys
import Model
from PySide2 import QtCore, QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    """dialog = QtWidgets.QFileDialog(None);
    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile);
    dialog.exec_();"""
    fileName = QtWidgets.QFileDialog.getOpenFileName(None,
    "Open Song", "~", "Audio Files (*.mp3 *.wav)")
    print("Got File " ,fileName);
    model = Model.main_model;
    model.open_file(fileName[0]);
    window = Gui.MainWindow(model)
    window.show()
    sys.exit(app.exec_());
