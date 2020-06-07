from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Slot
from PySide2.QtMultimedia import QMediaPlayer
from Model import main_model
from functools import partial
import pathlib
import threading

file_path = pathlib.Path(__file__).parent.absolute();
print(type(file_path))

update_interval = 100
slider_range = [1,20000]
slider_page_step  = 2000;
slider_single_step = 700;

class SlidersAndNameWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__();
        
        self._model = main_model
        
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

        temp_layout = QtWidgets.QVBoxLayout()
        temp_layout.addWidget(self._song_name_label);
        temp_layout.addWidget(self._duration_label)
        temp_layout.addWidget(self._player_slider);
        temp_widget = QtWidgets.QWidget();
        temp_widget.setLayout(temp_layout);

        self._layout = QtWidgets.QHBoxLayout();
        self._layout.addWidget(temp_widget);
        self._layout.addWidget(self._volume_slider);
        
        self.setLayout(self._layout)
    def update_label(self):
        media = self._model.get_current_media_data();
        self._song_name_label.setText(media.title);
        self.update()
    def dragging(self):
        self._update_timer.stop()
    def released(self):
        self._update_timer.setInterval(update_interval)
        self._update_timer.start(update_interval)

    def update(self):
        pos = self._model.get_position()
        if pos is None : return 
        #update the sliders
        self.test = True;
        self._player_slider.setValue(int(pos*slider_range[1])+ 1 );
        self.test = False;
        # set the duration label correctoy
        mdata = self._model.get_current_media_data();
        passed = int(pos * mdata.duration);
        total = mdata.duration;
        self._duration_label.setText("%02d:%02d / %02d:%02d" % (passed // 60 ,passed % 60,
                                                       total // 60 , total % 60));
    def volume_change(self,value):
        self._model.set_volume(value)
    
    def value_change(self):
        if self.test: return 
        val = self._player_slider.value();
        self._model.seek(val / slider_range[1]);

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

    def rewind(self):
        pass
    def play(self):
        print("Playing")
        self._model.play()
    def pause(self):
        print("Pausing")
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
        index = main_model.add_file(fileName[0],current_playlist);
        print("Got it in Index " + str(index))
        main_model.open_file(index,current_playlist);
        pl_widget_h.add_song_to_cur_playlist(main_model.get_current_media_data())

class MenuBarWidget(QtWidgets.QMenuBar):
    def __init__(self,pl_widget_h):
        super().__init__();
        self._model = main_model
        self._file_menu = QtWidgets.QMenu(self);
        self._file_menu.setTitle("File");
        self._open_action = self._file_menu.addAction("Open File");
        self._open_action.setShortcuts(QtGui.QKeySequence.Open)
        self._open_action.triggered.connect(partial(GuiHelper.open_file,pl_widget_h));
        self.addMenu(self._file_menu)

class PlayListWidget(QtWidgets.QTabWidget):
    def __init__(self):
        super().__init__();
        self._model = main_model
        now_playing = QtWidgets.QListWidget();
        self.addTab(now_playing,"Now Playing");
        now_playing.currentRowChanged.connect(self.song_index_changed);
        self._model.add_playlist("Now Playing");
        
    def add_song_to_cur_playlist(self,media):
        print(type(media))
        self.currentWidget().addItem(QtWidgets.QListWidgetItem(media.title));
    def song_index_changed(self,index):
        print("In Index " + str(index))
        self._model.open_file(index,self.get_current_pl_name());

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
        self._status.showMessage("Stopped");
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
        self._status.showMessage("%s-%s-%s" % (media.title,media.artist,media.album))
