import sys
import requests
from io import BytesIO
from zipfile import ZipFile
from PySide2 import QtWidgets, QtGui, QtCore
import pygame

class SongPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Song Player")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color: #263238; color: #FFFFFF; font-size: 14px;")

        pygame.init()
        pygame.mixer.init()

        self.song_dict = {}
        self.current_song = None
        self.song_name = None 

        self.snd_loop = False

        self.init_ui()
        self.fetch_songs()

    def set_icon_from_github(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            icon_data = response.content
            icon_pixmap = QtGui.QPixmap()
            icon_pixmap.loadFromData(icon_data)
            icon = QtGui.QIcon(icon_pixmap)
            self.setWindowIcon(icon)
        else:
            print("Failed to download icon from GitHub.")

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.set_icon_from_github("https://github.com/boyratata/profile/raw/main/yo.PNG")

        owner_image_url = "https://github.com/boyratata/profile/raw/main/yo.PNG"
        owner_image_data = requests.get(owner_image_url).content
        owner_pixmap = QtGui.QPixmap()
        owner_pixmap.loadFromData(owner_image_data)
        owner_label = QtWidgets.QLabel()
        owner_label.setPixmap(owner_pixmap.scaled(100, 100, aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                                                  transformMode=QtCore.Qt.SmoothTransformation))
        owner_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(owner_label)

        owner_name_label = QtWidgets.QLabel("Owner: boyratata")
        owner_name_label.setAlignment(QtCore.Qt.AlignCenter)
        owner_name_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        layout.addWidget(owner_name_label)

        self.song_list = QtWidgets.QListWidget()
        self.song_list.setStyleSheet("color: #FFFFFF; background-color: #37474F; border-radius: 10px; padding: 10px;")
        self.song_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  
        self.song_list.itemClicked.connect(self.toggle_play_pause)  
        layout.addWidget(self.song_list)

        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.change_volume)

        slider_stylesheet = """
            QSlider::groove:horizontal {
                background-color: #546E7A;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #FFFFFF;
                width: 10px; /* Width of the handle */
                margin: -5px 0; /* Centers the handle vertically */
                border-radius: 5px; /* Makes the handle circular */
           }
        """
        self.volume_slider.setStyleSheet(slider_stylesheet)
        layout.addWidget(self.volume_slider)
         
        self.loop_checkbox = QtWidgets.QCheckBox("Loop")
        self.loop_checkbox.stateChanged.connect(self.set_loop)
        layout.addWidget(self.loop_checkbox)

        self.setLayout(layout)

    def fetch_songs(self):
        urls = [
            "https://github.com/boyratata/song-list/raw/main/ayo.zip",
            "https://github.com/boyratata/song-list/raw/main/hey.zip",
            "https://github.com/boyratata/song-list/raw/main/nah.zip",
            "https://github.com/boyratata/song-list/raw/main/wow.zip",
            "https://github.com/boyratata/song-list/raw/main/ay.zip",
            "https://github.com/boyratata/song-list/raw/main/u.zip",
            "https://github.com/boyratata/song-list/raw/main/sup.zip"
            
        ]
        for url in urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with ZipFile(BytesIO(response.content)) as z:
                        for filename in z.namelist():
                            if filename.endswith('.mp3'):
                                song_name = filename.split('/')[-1].split('.')[0]
                                song_data = z.read(filename)
                                self.song_dict[song_name] = song_data
                                self.song_list.addItem(song_name)
                else:
                    print(f"Failed to fetch songs from {url}.")
            except Exception as e:
                print(f"Error fetching songs: {e}")

    def toggle_play_pause(self, item):
    song_name = item.text()
    song_data = self.song_dict.get(song_name)
    if song_data:
        if song_name == self.current_song:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(BytesIO(song_data))
            pygame.mixer.music.set_volume(self.volume_slider.value() / 100)
            pygame.mixer.music.play(-1)
            self.current_song = song_name
            QtCore.QTimer.singleShot(100, self.check_song_finished)
    else:
        print(f"Failed to play song: {song_name}")

    def set_loop(self, value):
        self.snd_loop = bool(value)

    def change_volume(self, value):
        volume = value / 100
        pygame.mixer.music.set_volume(volume)

    def check_song_finished(self):
        if not pygame.mixer.music.get_busy():
            self.current_song = None

    def closeEvent(self, event):
        pygame.mixer.music.stop()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    player = SongPlayer()
    player.show()

    sys.exit(app.exec_())
