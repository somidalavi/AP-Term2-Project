from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Slot
from PySide2.QtMultimedia import QMediaPlayer
from Model import main_model
import threading
import pathlib

file_path = str(pathlib.Path(__file__).parent.absolute());
print("current path is " + file_path)

update_interval = 500
slider_range = [1,20000]
slider_page_step  = 2000;
slider_single_step = 700;

class SlidersAndNameWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__();
        
        self._model = main_model
        
        self._update_timer = QtCore.QTimer();
        self._update_timer.setInterval(update_interval)
        self._update_timer.timeout.connect(self.update_slider);
        self._update_timer.start(update_interval)

        self._volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self._volume_slider.valueChanged.connect(self.volume_change);
        self._volume_slider.setValue(50);

        self._song_name_label = QtWidgets.QLabel("No Song");
        
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
        temp_layout.addWidget(self._player_slider);
        temp_widget = QtWidgets.QWidget();
        temp_widget.setLayout(temp_layout);

        self._layout = QtWidgets.QHBoxLayout();
        self._layout.addWidget(temp_widget);
        self._layout.addWidget(self._volume_slider);
        
        self.setLayout(self._layout)
        
    def dragging(self):
        self._update_timer.stop()
    def released(self):
        self._update_timer.setInterval(update_interval)
        self._update_timer.start(update_interval)

    def update_slider(self):

        print(threading.activeCount())
        self.test = True;
        self._player_slider.setValue(int(self._model.get_position()*  slider_range[1])+ 1 );
        self.test = False;
    
    def volume_change(self,value):
        self._model.set_volume(value)
    
    def value_change(self):
        print("dfsd " + threading.current_thread().getName())
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
            icon = QtGui.QIcon(file_path + '/icons/' + icon_name);
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
        pass
    def forwards(self):
        pass


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

class PlayListWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__();

class GuiHelper:
    @staticmethod
    def open_file(): 
        print(threading.activeCount())
        fileName = QtWidgets.QFileDialog.getOpenFileName(None,
        "Open Song", "~", "Audio Files (*.mp3 *.wav)")
        print("HRe")
        if len(fileName) == 0 : return
        main_model.open_file(fileName[0]);

class MenuBarWidget(QtWidgets.QMenuBar):
    def __init__(self):
        super().__init__();
        self._model = main_model
        self._file_menu = QtWidgets.QMenu(self);
        self._file_menu.setTitle("File");
        self._open_action = self._file_menu.addAction("Open File");
        self._open_action.setShortcuts(QtGui.QKeySequence.Open)
        self._open_action.triggered.connect(GuiHelper.open_file);
        self.addMenu(self._file_menu)
class MainWindow(QtWidgets.QWidget):
    def __init__(self):

        super().__init__();
        self.setWindowTitle("Music Player");
        self._model = main_model;
        
        #TODO: add a status bar and menu bar
        self._menu = MenuBarWidget();
        

        self._status = QtWidgets.QStatusBar();
        self._status.showMessage("Stopped");
        def update_status(status):
            if status == QMediaPlayer.StoppedState: self._status.showMessage("Stopped")
            elif status == QMediaPlayer.PausedState : self._status.showMessage("Paused")
            else : self._status.showMessage("Playing")

        self._model.player.stateChanged.connect(update_status);
        
        self._player = MediaPlayerWidget()
        self._playlist = PlayListWidget()
        
        self._layout = QtWidgets.QVBoxLayout();
        self._layout.addWidget(self._menu);
        self._layout.addWidget(self._player);
        self._layout.addWidget(self._playlist);
        self._layout.addWidget(self._status);

        self.setLayout(self._layout);
