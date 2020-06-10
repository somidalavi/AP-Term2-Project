from PySide2 import QtMultimedia, QtCore
from tinytag import TinyTag
from PySide2.QtCore import Signal
import sqlite3
import pathlib
import os
from PySide2.QtMultimedia import QMediaContent , QMediaPlaylist

file_path = pathlib.Path(__file__).parent.absolute();
class AudioMetadata():
    def __init__(self,file_path):
        tag = TinyTag.get(file_path);
        self.album = tag.album
        self.artist = tag.artist
        self.title = tag.title
        #may need to change
        self.path = file_path
        self.genre = tag.genre
        self.duration = tag.duration
        #Used when the meta data is represented in a database
        self.dbase_id = -1;

def setup_database():
    exists = os.path.isfile(str(file_path / 'lib2.db')) 
    con = sqlite3.connect('lib2.db')
    cur = con.cursor()
    if exists:
        print("already exists!!");
        return (con,cur) 

    cur.execute('''CREATE TABLE  songs (
                song_id INTEGER PRIMARY KEY,
                path      TEXT NOT NULL UNIQUE,
                title     TEXT NOT NULL,
                genre_id  INTEGER NOT NULL,
                artist_id INTEGER NOT NULL,
                album_id  INTEGER NOT NULL,
                duration INTEGER NOT NULL
                );''')
    cur.execute('''
                CREATE UNIQUE INDEX idx_songs_path
                ON songs (path);
                ''')
    cur.execute('''CREATE TABLE  playlists(
                playlist_id INTEGER PRIMARY KEY,
                name    TEXT NOT NULL UNIQUE
                    );
                ''')
    cur.execute('''
                CREATE UNIQUE INDEX idx_playlist_name
                ON playlists (name);
                ''')
    cur.execute('''
                CREATE TABLE playlist_group(
                playlist_id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                PRIMARY KEY (playlist_id,song_id),
                FOREIGN KEY (playlist_id)
                    REFERENCES playlists (playlist_id)
                        ON DELETE NO ACTION
                        ON UPDATE NO ACTION,
                FOREIGN KEY (song_id)
                    REFERENCES songs (song_id)
                        ON DELETE NO ACTION
                        ON UPDATE NO ACTION
                );
                ''')
    con.commit()
    return (con,cur)
class Model(QtCore.QObject):

    playlistAdded = QtCore.Signal(str);
    #This will be Dumb But okay
    playlistUpdated = QtCore.Signal(str);
    def __init__(self):
        super().__init__(); 
    def init(self):
        self.database_con , self.database_cur = setup_database();
        self._playback_rate = 1.0
        self._repeating = False
        self._shuffled = False
        
        self._playlists_mdata = {} # mdata = meta data
        self._playlists = {}
        self._current_playlist = None;
        self._current_playlist_mdata = None;
        self._current_playlist_name = None;
        self._library = QtMultimedia.QMediaPlaylist();
        self._library_set = set()

        self._playlists["Library"] = self._library
        self._playlists_mdata["Library"] = []
        self._playlists["Now Playing"] = QtMultimedia.QMediaPlaylist()
        self._playlists_mdata["Now Playing"] = []
        #it's first signal will be emitted later in read_from_database
        
        self.player = QtMultimedia.QMediaPlayer(self)
        self.player.setVolume(50);
    def shut_down(self):
        self.database_con.close();
    def read_from_database(self):
        #TODO: acutally make a use of all the stuff we keep in the database 
        #rather than just the path
        self.playlistAdded.emit("Library")
        self.playlistAdded.emit("Now Playing")
        cursor = self.database_con.execute("select path from songs");
        path_generator = (row[0] for row in cursor )
        self.add_files(path_generator,"Library");
        #needs a big rethink but it's working for now
        t_cursor = self.database_con.execute('SELECT playlist_id,name FROM playlists;')
        tmp_ls = []
        for row in t_cursor:
            tmp_ls.append((row[0],row[1]));
        for row in tmp_ls:
            t_cursor2 = self.database_con.execute('''
                                     SELECT playlist_id,path,songs.song_id
                                     FROM playlist_group
                                     INNER JOIN songs
                                     on songs.song_id = playlist_group.song_id
                                     where playlist_id = ?;''',
                                                  (row[0],))
            self.add_playlist(row[1])
            path_generator = (nrow[1] for nrow in t_cursor2)
            self.add_files(path_generator,row[1])
        
        
    def set_current_playlist(self,playlist_name):
        self._current_playlist_name = playlist_name
        self._current_playlist = self._playlists[playlist_name];
        self._current_playlist_mdata = self._playlists_mdata[playlist_name];
        self.update_playback_mode();
        self.player.setPlaylist(self._current_playlist);
        
    def add_playlist(self,name):
        print('adding playlist',name);
        if name in self._playlists :
            print("can't add that playlist")
            return False
        self._playlists_mdata[name] = [];
        new_playlist = QtMultimedia.QMediaPlaylist()
        self._playlists[name] = new_playlist;
        new_playlist.dbase_id = self.add_playlist_to_database(name);
        print('added playlsit' , name);
        self.playlistAdded.emit(name);
    def add_files(self,paths,playlist_name):
        print("addint to ",playlist_name)
        paths = [path for path in paths];
        for path in paths:
            print(path, playlist_name)
        saving_playlist = True
        saving_to_library = False;
        
        if playlist_name == "Library":
            saving_playlist = False;
            saving_to_library  = True
        else : self.add_files(paths,"Library")

        if playlist_name == "Now Playing":
            saving_playlist = False;
        cur_playlist = self._playlists[playlist_name]
        cur_playlist_mdata = self._playlists_mdata[playlist_name]
        for path in paths:
            mdata = AudioMetadata(path)
            if not saving_to_library or path not in self._library_set:
                n_media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path));
                cur_playlist.addMedia(n_media)
                cur_playlist_mdata.append(mdata);
            if saving_to_library : self._library_set.add(path);
            mdata.dbase_id = self.add_song_to_database(mdata);
            if saving_playlist:
                self.add_song_to_database_playlist(mdata,cur_playlist);
        if saving_playlist:
            self.database_con.commit();
        print("finished adding to ",playlist_name)
        self.playlistUpdated.emit(playlist_name);

    def add_playlist_to_database(self,name):
        self.database_cur.execute('''
                                 INSERT OR IGNORE INTO playlists values
                                 (NULL,?);
                                    ''',(name,))

        #for playlists we commit right away
        self.database_con.commit();

        return self.database_cur.lastrowid
    def add_song_to_database_playlist(self,mdata,playlist):
        self.database_cur.execute('''
                                  INSERT OR IGNORE INTO playlist_group values
                                  (?,?);''',(playlist.dbase_id,mdata.dbase_id)) 
    def add_song_to_database(self,mdata):
        data_tuple =  (mdata.path,mdata.title,
                       mdata.genre,mdata.artist,mdata.album
                       ,mdata.duration)
        self.database_cur.execute('''
                                  INSERT OR IGNORE INTO songs values 
                                  (NULL,?,?,?,?,?,? );''',data_tuple)   
        return self.database_cur.lastrowid
    
    def open_file(self,index,playlist_name):
        if playlist_name != self._current_playlist_name:
            self.set_current_playlist(playlist_name);
        self._current_playlist.setCurrentIndex(index);
        self.player.play()
   
    def get_playlist_mdata(self,name):
        return self._playlists_mdata[name];
    
    def get_current_media_data(self):
        return self._current_playlist_mdata[self._current_playlist.currentIndex()];

    #isn't actually ever used
    '''def get_media_data(self,index,playlist_name):
        return  self._playlists_mdata[playlist_name][index]
    '''

    def update_playback_mode(self):
        if self._current_playlist == None : return 
        if self._repeating:
            self._current_playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop);
        elif self._shuffled:
            self._current_playlist.setPlaybackMode(QMediaPlaylist.Random)
        else:
            self._current_playlist.setPlaybackMode(QMediaPlaylist.Loop);
    def set_repeat(self,flag):
        self._repeating = flag
        self.update_playback_mode()
    
    def set_shuffled(self,flag):
        self._shuffled = flag;
        self.update_playback_mode()

    def slow_playback(self):
        self._playback_rate -= 0.25
        if self._playback_rate < 0.49: self._playback_rate = 0.5
        self.player.setPlaybackRate(self._playback_rate)
        #this needs to be added for some reason
        self.player.setPosition(self.player.position())
    def increase_playback(self):
        self._playback_rate += 0.25
        if self._playback_rate > 2.0 : self._playback_rate = 2.0
        self.player.setPlaybackRate(self._playback_rate);
        self.player.setPosition(self.player.position())
    
    def seek(self,p_percent): #position is normalised from 0 to 1
        self.player.setPosition(p_percent * self.player.duration());
    
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
