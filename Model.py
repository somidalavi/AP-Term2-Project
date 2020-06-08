from PySide2 import QtMultimedia, QtCore
from tinytag import TinyTag
from PySide2.QtMultimedia import QMediaContent , QMediaPlaylist
class AudioMetadata():
    def __init__(self,file_path):
        tag = TinyTag.get(file_path);
        self.album = tag.album
        self.artist = tag.artist
        self.title = tag.title
        #may need to change
        self.path = file_path
        self.duration = tag.duration

class Model(QtCore.QObject):
    def __init__(self):
        super().__init__();
    
    def init(self):
        self._repeating = False
        self._shuffled = False
        self._playlists_mdata = {} # mdata = meta data
        self._playlists = {}
        self._current_playlist = None;
        self._current_playlist_mdata = None;
        self._current_playlist_name = None;
        self.player = QtMultimedia.QMediaPlayer(self)
        self.player.setVolume(50);
        print(self.player.isSeekable());
    def update_playback_mode(self):
        if self._current_playlist == None : return 
        if self._repeating:
            self._current_playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop);
        elif self._shuffled:
            self._current_playlist.setPlaybackMode(QMediaPlaylist.Random)
        else:
            self._current_playlist.setPlaybackMode(QMediaPlaylist.Loop);
    def set_current_playlist(self,playlist_name):
        self._current_playlist_name = playlist_name
        self._current_playlist = self._playlists[playlist_name];
        self._current_playlist_mdata = self._playlists_mdata[playlist_name];
        self.update_playback_mode();
        self.player.setPlaylist(self._current_playlist);
        
    def set_repeat(self,flag):
        self._repeating = flag
        self.update_playback_mode()
    def set_shuffled(self,flag):
        self._shuffled = flag;
        self.update_playback_mode()
    def add_playlist(self,name):
        if name in self._playlists :
            print("can't add that playlist")
            return False
        self._playlists_mdata[name] = [];
        new_playlist = QtMultimedia.QMediaPlaylist()
        self._playlists[name] = new_playlist;

    def seek(self,p_percent): #position is normalised from 0 to 1
        self.player.setPosition(p_percent * self.player.duration());

    def add_file(self,path,playlist_name):
        n_media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path));
        self._playlists[playlist_name].addMedia(n_media)
        self._playlists_mdata[playlist_name].append(AudioMetadata(path));
        return self._playlists[playlist_name].mediaCount() - 1;

    def open_file(self,index,playlist_name):
        if playlist_name != self._current_playlist_name:
            self.set_current_playlist(playlist_name);
        self._current_playlist.setCurrentIndex(index);
        self.player.play()

    def get_current_media_data(self):
        return self._current_playlist_mdata[self._current_playlist.currentIndex()];
    def get_media_data(self,index,playlist_name):
        a = self._playlists_mdata[playlist_name][index]
        return a
    def set_volume(self,vol):
        self.player.setVolume(vol);
    def pause(self):
        self.player.pause()
    def play(self):
        self.player.play()
    def stop(self):
        self.player.stop()
    def forwards(self):
        self._current_playlist.next()
    def rewind(self):
        self._current_playlist.previous()
    def get_position(self):
        if (self.player.duration() == 0) : return None;
        return self.player.position() / self.player.duration();

main_model = Model();
