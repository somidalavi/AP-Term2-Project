from PySide2 import QtMultimedia, QtCore
class Model(QtCore.QObject):
    def __init__(self):
        super().__init__();
    
    def init(self):
        self.player = QtMultimedia.QMediaPlayer(self)
        print(self.player.isSeekable());
    def seek(self,p_percent): #position is normalised from 0 to 1
        self.player.setPosition(p_percent * self.player.duration());

    def open_file(self,path):
        self.player.setMedia(QtCore.QUrl.fromLocalFile(path))
        self.player.setVolume(50);
        self.player.play()
        print(self.player.errorString())
    def set_volume(self,vol):
        self.player.setVolume(vol);
    def pause(self):
        self.player.pause()
    def play(self):
        self.player.play()
    def get_position(self):
        if (self.player.duration() == 0) : return 0;
        return self.player.position() / self.player.duration();
main_model = Model();
