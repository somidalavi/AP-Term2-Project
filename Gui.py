from PySide2 import QtCore, QtWidgets

slider_range = [1,20000]
slider_page_step  = 2000;

class SlidersAndNameWidget(QtWidgets.QWidget):
    def __init__(self,model):
        super().__init__();
        self._model = model
        
        self._volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self._song_name_label = QtWidgets.QLabel("TestLabel");
       
        self._player_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal);
        self._player_slider.valueChanged.connect(self.value_change);
        self._player_slider.setRange(slider_range[0],slider_range[1]);
        self._player_slider.setPageStep(slider_page_step);

        temp_layout = QtWidgets.QVBoxLayout()
        temp_layout.addWidget(self._song_name_label);
        temp_layout.addWidget(self._player_slider);
    
        temp_widget = QtWidgets.QWidget();
        temp_widget.setLayout(temp_layout);
        self._layout = QtWidgets.QHBoxLayout();
        self._layout.addWidget(temp_widget);
        self._layout.addWidget(self._volume_slider);
        self.setLayout(self._layout);

    def value_change(self):
        print("Hello At " + str(self._player_slider.value()));
        self._model.seek(self._player_slider.value());
class MediaButtonsWidget(QtWidgets.QWidget):
    def __init__(self,model):
        super().__init__();
        self._model = model;
        button_captions = [ "left",'start','stop','reset','right',]
        self._buttons = []
        self._layout = QtWidgets.QHBoxLayout()
        for caption in button_captions:
            self._buttons.append(QtWidgets.QPushButton());
            self._layout.addWidget(self._buttons[-1]);
        self.setLayout(self._layout);

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
