from PySide2 import QtMultimedia, QtCore
class Model(QtCore.QObject):
    def __init__(self):
        super().__init__();
    
    def init(self):
        self._player = QtMultimedia.QMediaPlayer(self)
        print(self._player.isSeekable());
    def seek(self,p_percent): #position is normalised from 0 to 1
        self._player.setPosition(p_percent * self._player.duration());
    def open_file(self,path):
        self._player.setMedia(QtCore.QUrl.fromLocalFile(path))
        self._player.setVolume(50);
        self._player.play()
        print(self._player.errorString())
    def set_volume(self,vol):
        self._player.setVolume(vol);
    def pause(self):
        self._player.pause()
    def play(self):
        self._player.play()
main_model = Model();
