from PySide2 import QtMultimedia, QtCore

class Model:
    def __init__(self):
        self._player = QtMultimedia.QMediaPlayer()
        pass
    def seek(self,i):
        print("seeking to there " + str(i));
    def open_file(self,path):
        self._player.setMedia(QtCore.QUrl.fromLocalFile(path));
        self._player.setVolume(50);
        self._player.play();
main_model = Model();
