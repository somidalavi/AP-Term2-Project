#! /bin/python3
   
import Model
import Gui
import sqlite3
import sys
from PySide2 import QtCore, QtWidgets
import pathlib
import os

if __name__ == "__main__":
    os.chdir(pathlib.Path(__file__).parent.absolute())
    app = QtWidgets.QApplication()
    """dialog = QtWidgets.QFileDialog(None);
    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile);
    dialog.exec_();""" 
    Model.main_model.init();
    window = Gui.MainWindow()
    Model.main_model.read_from_database();
    window.show()
    sys.exit(app.exec_());
    Model.main_model.shut_down()
