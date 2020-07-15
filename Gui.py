from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Slot
from PySide2.QtMultimedia import QMediaPlayer
from Model import main_model
from functools import partial
import LibSearch
import pathlib
import os
import os.path
import threading

file_path = pathlib.Path(__file__).parent.absolute();
print(type(file_path))
allowed_suffixes = ['.mp3','.wav','.m4a','.mp4']
update_interval = 100
slider_range = [1,20000]
slider_page_step  = 2000;
slider_single_step = 700;

class SlidersAndNameWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__();
        
        self._model = main_model
        

        self.should_update_position = True;
        self._update_timer = QtCore.QTimer();
        self._update_timer.setInterval(update_interval)
        self._update_timer.timeout.connect(self.update);
        self._update_timer.start(update_interval)

        self._volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self._volume_slider.valueChanged.connect(self.volume_change);
        self._volume_slider.setValue(50);

        self._song_name_label = QtWidgets.QLabel("No Song");
        self._model.player.currentMediaChanged.connect(self.update_label)

        self._duration_label = QtWidgets.QLabel("00:00 / 00:00");
        
        self._player_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal);
        self._player_slider.valueChanged.connect(self.value_change);
        self._player_slider.sliderPressed.connect(self.dragging);
        self._player_slider.sliderReleased.connect(self.released)
        self._player_slider.setRange(slider_range[0],slider_range[1]);
        self._player_slider.setPageStep(slider_page_step);
        self._player_slider.setSingleStep(slider_single_step)
        self._player_slider.setTracking(False);

        self._shuffle_button = QtWidgets.QCheckBox("Shuffle");
        self._shuffle_button.toggled.connect(self.shuffle_toggled);
        self._repeat_button = QtWidgets.QCheckBox("Repeat");
        self._repeat_button.toggled.connect(self.repeat_toggled);
        
        temp_layout = QtWidgets.QVBoxLayout()
        temp_layout.addWidget(self._song_name_label);
        temp_layout.addWidget(self._duration_label)
        temp_layout.addWidget(self._shuffle_button);
        temp_layout.addWidget(self._repeat_button);
        temp_layout.addWidget(self._player_slider);

        temp_widget = QtWidgets.QWidget();
        temp_widget.setLayout(temp_layout);
        
        self._layout = QtWidgets.QHBoxLayout();
        self._layout.addWidget(temp_widget);
        self._layout.addWidget(self._volume_slider);
        
        self.setLayout(self._layout)

    def repeat_toggled(self,checked):
        self._model.set_repeat(checked);
    def shuffle_toggled(self,checked):
        self._model.set_shuffled(checked);
    def update_label(self):
        media = self._model.get_current_media_data();
        self._song_name_label.setText(media.title);
    def dragging(self):
        self._update_timer.stop()
    def released(self):
        self._update_timer.setInterval(update_interval)
        self._update_timer.start(update_interval)

    def update(self):
        pos = self._model.get_position()
        if pos is None : return 
        #update the sliders
        #this probably has bugs too
        self.should_update_position = False;
        self._player_slider.setValue(int(pos*slider_range[1])+ 1 );
        self.should_update_position = True;
        # set the duration label correctoy
        mdata = self._model.get_current_media_data();
        passed = int(pos * mdata.duration);
        total = mdata.duration;
        self._duration_label.setText("%02d:%02d / %02d:%02d" % (passed // 60 ,passed % 60,
                                                       total // 60 , total % 60));
    
    def value_change(self):
        if not self.should_update_position: return 
        val = self._player_slider.value();
        self._model.seek(val / slider_range[1]);


    def volume_change(self,value):
        self._model.set_volume(value)
class MediaButtonsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__();
        self._model = main_model;
        icon_names = [ "rewind.png",'play.png','pause.png','stop.png','forwards.png',]
        button_clicked_funcs = [self.rewind,self.play,self.pause,self.stop,self.forwards];
        self._buttons = []
        self._layout = QtWidgets.QHBoxLayout()
        for icon_name,func in zip(icon_names,button_clicked_funcs):
            icon = QtGui.QIcon(str(file_path / 'icons' / icon_name));
            button = QtWidgets.QPushButton();
            button.clicked.connect(func)
            button.setIcon(icon);
            self._buttons.append(button);
            self._layout.addWidget(button);
        self.setLayout(self._layout);

    def play(self):
        self._model.play()
    def pause(self):
        self._model.pause()
    def stop(self):
        self._model.stop()
    def forwards(self):
        self._model.forwards()
    def rewind(self):
        self._model.rewind()


class MediaPlayerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__();
        self._model = main_model;
        self._layout = QtWidgets.QVBoxLayout()
        self._sliders_and_name = SlidersAndNameWidget();
        self._media_buttons = MediaButtonsWidget();
        self._layout.addWidget(self._sliders_and_name);
        self._layout.addWidget(self._media_buttons);
        self.setLayout(self._layout);

class GuiHelper:
    @staticmethod
    def open_file(pl_widget_h): 
        fileName = QtWidgets.QFileDialog.getOpenFileName(None,
        "Choose Song", "~", "Audio Files (*.mp3 *.wav *.m4a)")
        if len(fileName[0]) == 0 : return
        current_playlist = pl_widget_h.get_current_pl_name()
        print(current_playlist)
        main_model.add_files((fileName[0],),current_playlist);
    @staticmethod
    def add_playlist():
        text, ok = QtWidgets.QInputDialog.getText(None,'Enter a name',
        'Playlist Name: ',QtWidgets.QLineEdit.Normal, '~' )
        if ok and text:
            main_model.add_playlist(text);
    @staticmethod
    def playlist_dir():    
        directory = QtWidgets.QFileDialog.getExistingDirectory(None,
                                        "Open Directory",
                                       "/home",
                                       QtWidgets.QFileDialog.ShowDirsOnly
                                       | QtWidgets.QFileDialog.DontResolveSymlinks)
        playlist_name = os.path.basename(directory);
        ok = main_model.add_playlist(playlist_name)
        if ok == False:
            return 
        def path_generator():
            for root, dirs, files in os.walk(directory,topdown=True):
                path_directory = pathlib.Path(root);
                for file in files:
                    new_path = path_directory / file
                    if new_path.suffix in allowed_suffixes:
                        yield str(new_path)
        path_gen = path_generator()
        main_model.add_files(path_gen,playlist_name)

    @staticmethod
    def search_library():
        LibSearch.show();
        print("Here")

    
class MenuBarWidget(QtWidgets.QMenuBar):
    def __init__(self,pl_widget_h):
        super().__init__();
        self._model = main_model
        self._file_menu = QtWidgets.QMenu(self);
        self._file_menu.setTitle("File");
        self._open_action = self._file_menu.addAction("Open File");
        self._open_action.setShortcuts(QtGui.QKeySequence.Open)
        self._open_action.triggered.connect(partial(GuiHelper.open_file,pl_widget_h));
        self._newplaylist_action = self._file_menu.addAction("Add a Playlist");
        self._newplaylist_action.setShortcuts(QtGui.QKeySequence.AddTab);
        self._newplaylist_action.triggered.connect(GuiHelper.add_playlist);
        self._playlist_fromdir_action = self._file_menu.addAction("Playlist from a folder");
        self._playlist_fromdir_action.triggered.connect(GuiHelper.playlist_dir);
        
        self._playback_menu = QtWidgets.QMenu(self);
        self._playback_menu.setTitle("Playback")
        self._faster_playback_action = self._playback_menu.addAction("Faster Playback")
        self._faster_playback_action.triggered.connect(self._model.increase_playback)
        self._faster_playback_action.setShortcuts(QtGui.QKeySequence.Forward)
        self._slower_playback_action = self._playback_menu.addAction("Slower Playback")
        self._slower_playback_action.setShortcuts(QtGui.QKeySequence.Back)
        self._slower_playback_action.triggered.connect(self._model.slow_playback)
        
        self._library_menu = QtWidgets.QMenu(self)
        self._library_menu.setTitle("Library")
        self._search_library_action = self._library_menu.addAction("Search Library")
        self._search_library_action.setShortcuts(QtGui.QKeySequence.Find)
        self._search_library_action.triggered.connect(GuiHelper.search_library);

        self.addMenu(self._file_menu)
        self.addMenu(self._playback_menu);
        self.addMenu(self._library_menu);

class PlayListWidget(QtWidgets.QTabWidget):
    def __init__(self):
        print("Initintg Playlist IWdget")
        super().__init__();
        self._playlist_dict = {}
        self._model = main_model
        self._model.playlistAdded.connect(self.add_playlist)
        self._model.playlistUpdated.connect(self.update_playlist);

    
    @QtCore.Slot(str)
    def add_playlist(self,name):
        print("The Playlists data changed.")
        new_playlist = QtWidgets.QListWidget();
        new_playlist.itemDoubleClicked.connect(partial(self.song_changed,new_playlist));
        self.addTab(new_playlist,name);
        self._playlist_dict[name] = new_playlist

    @QtCore.Slot(str)
    def update_playlist(self,name):
        cur_list = self._playlist_dict[name];
        cur_list.clear();
        mdata_list = self._model.get_playlist_mdata(name)
        for mdata in mdata_list:
            cur_list.addItem(QtWidgets.QListWidgetItem(mdata.title))
    def song_changed(self,pl,item):
        print("Playing index ",pl)
        self._model.open_file(pl.indexFromItem(item).row(),self.get_current_pl_name());

    def get_current_pl_name(self):
        return self.tabText(self.currentIndex())

class MainWindow(QtWidgets.QWidget):
    def __init__(self):

        super().__init__();
        self.setWindowTitle("Music Player");
        self._model = main_model;
        
        self._playlist = PlayListWidget()
        
        #TODO: add a status bar and menu bar
        self._menu = MenuBarWidget(self._playlist);
        
        self._status = QtWidgets.QStatusBar();
        self._status.showMessage("No Song");
        def update_title(status):
            if status == QMediaPlayer.StoppedState: self.setWindowTitle("Music Player-Stopped")
            elif status == QMediaPlayer.PausedState : self.setWindowTitle("Music Player-Paused")
            else : self.setWindowTitle("Music Player-Playing")
        self._model.player.currentMediaChanged.connect(self.update_status)
        self._model.player.stateChanged.connect(update_title);
        
        self._player = MediaPlayerWidget()
        self._layout = QtWidgets.QVBoxLayout();
        self._layout.addWidget(self._menu);
        self._layout.addWidget(self._player);
        self._layout.addWidget(self._playlist);
        self._layout.addWidget(self._status);

        self.setLayout(self._layout);
    def update_status(self):
        media = self._model.get_current_media_data();
        self._status.showMessage("%s-%s-%s-%s" % (media.title,media.artist,media.album,media.genre))
