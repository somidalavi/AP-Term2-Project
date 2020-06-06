from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Slot
import pathlib
file_path = str(pathlib.Path(__file__).parent.absolute());
print("current path is " + file_path)
slider_range = [1,20000]
slider_page_step  = 2000;
slider_single_step = 400;

class SlidersAndNameWidget(QtWidgets.QWidget):
    def __init__(self,model):
        super().__init__();
        self._model = model
        
        self._volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self._volume_slider.valueChanged.connect(self.volume_change);
        self._volume_slider.setValue(50);
        self._song_name_label = QtWidgets.QLabel("TestLabel");
       
        self._player_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal);
        self._player_slider.valueChanged.connect(self.value_change);
        self._player_slider.setRange(slider_range[0],slider_range[1]);
        self._player_slider.setPageStep(slider_page_step);
        self._player_slider.setSingleStep(slider_single_step)

        temp_layout = QtWidgets.QVBoxLayout()
        temp_layout.addWidget(self._song_name_label);
        temp_layout.addWidget(self._player_slider);
    
        temp_widget = QtWidgets.QWidget();
        temp_widget.setLayout(temp_layout);
        self._layout = QtWidgets.QHBoxLayout();
        self._layout.addWidget(temp_widget);
        self._layout.addWidget(self._volume_slider);
        self.setLayout(self._layout)
    def volume_change(self,value):
        self._model.set_volume(value)
    def value_change(self):
        self._model.seek(self._player_slider.value() / slider_range[1] );


class MediaButtonsWidget(QtWidgets.QWidget):
    def __init__(self,model):
        super().__init__();
        self._model = model;
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
    def __init__(self,model):
        super().__init__();
        self._model = model;
        self._layout = QtWidgets.QVBoxLayout()
        self._sliders_and_name = SlidersAndNameWidget(model);
        self._media_buttons = MediaButtonsWidget(model);
        self._layout.addWidget(self._sliders_and_name);
        self._layout.addWidget(self._media_buttons);
        self.setLayout(self._layout);

class PlayListWidget(QtWidgets.QWidget):
    def __init__(self,model):
        super().__init__();
class MainWindow(QtWidgets.QWidget):
    def __init__(self,model):
        super().__init__();
        self._model = model;
        #TODO: add a status bar and menu bar
        self._player = MediaPlayerWidget(self._model)
        self._playlist = PlayListWidget(self._model)
        self._layout = QtWidgets.QVBoxLayout();
        self._layout.addWidget(self._player);
        self._layout.addWidget(self._playlist);
        self.setLayout(self._layout);
