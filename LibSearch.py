import Model
from PySide2 import QtCore, QtWidgets,QtGui
from PySide2.QtWidgets import QListWidgetItem
from functools import partial
from Model import main_model
class LibSearchDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__();
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self._list = QtWidgets.QListWidget();
        self._list.addItem(QtWidgets.QListWidgetItem("Hello"));
        self._list.itemDoubleClicked.connect(self.add_songs);
        self._genres = QtWidgets.QCheckBox("genres");
        self._genres.setChecked(True)
        self._genres.toggled.connect(partial(self.toggle_hide,"Genre"));
        
        self._albums = QtWidgets.QCheckBox("albums")
        self._albums.setChecked(True)
        self._albums.toggled.connect(partial(self.toggle_hide,"Album"));
        
        self._artists = QtWidgets.QCheckBox("artists");
        self._artists.setChecked(True)
        self._artists.toggled.connect(partial(self.toggle_hide,"Artist"));
        self._layout.addWidget(self._list);

        temp_widget = QtWidgets.QWidget();
        temp_layout = QtWidgets.QHBoxLayout();
        temp_layout.addWidget(self._genres);
        temp_layout.addWidget(self._albums);
        temp_layout.addWidget(self._artists);
        temp_widget.setLayout(temp_layout)
        self._layout.addWidget(temp_widget)
        genres = main_model.get_genres()
        albums = main_model.get_albums()
        artists = main_model.get_artists()  
        for genre in genres : self._list.addItem(QListWidgetItem("Genre-"+genre))
        for album in albums : self._list.addItem(QListWidgetItem("Album-"+album))
        for artist in artists : self._list.addItem(QListWidgetItem("Artist-"+artist))
    def toggle_hide(self,name,flag):
        items = self._list.findItems(name,QtCore.Qt.MatchStartsWith)
        for item in items:
            item.setHidden(not flag);
    def get_songs(self,text):
        if text.startswith("Genre"): return main_model.get_genre_songs(text[6:])
        if text.startswith("Album"): return main_model.get_album_songs(text[6:])
        if text.startswith("Artist"): return main_model.get_artist_songs(text[7:])
    def add_songs(self,item):
        songs = self.get_songs(item.text())
        main_model.add_files(songs,"Now Playing");
        self.accept();
def show():
    dialog = LibSearchDialog();
    dialog.setModal(True)
    dialog.exec()


