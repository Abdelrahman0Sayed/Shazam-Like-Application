import hashlib
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from shazam_ui import UI_MainWindow  # Change import to use Ui_MainWindow
import librosa
import scipy
import sounddevice as sd
import numpy as np
import imagehash
from PIL import Image
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import pandas as pd
from imagehash import hex_to_hash
import os
from PyQt5 import QtCore, QtWidgets

class MainWindow(UI_MainWindow):
    def __init__(self):
        super().__init__()
        self.CHUNK_SIZE = 2048 * 4  
        self.UPDATE_INTERVAL = 100  
        self.MAX_POINTS = 1000 
        self.firstMediaPlayer = QMediaPlayer()
        self.secondMediaPlayer = QMediaPlayer()
        self.first_file_path = None
        self.second_file_path = None
        self.firstFileData = None
        self.firstFileSpectro = None
        self.firstSpectroFeatures = []
        self.first_colorbar = None
        self.secondFileData = None
        self.secondFileSpectro = None
        self.secondSpectroFeatures = []
        self.second_colorbar = None
        self.firstGraphPlaying = False
        self.secondGraphPlaying = False
        self.firstGraphTimer= QTimer()
        self.secondGraphTimer = QTimer()
        self.firstGraphTimer.timeout.connect(lambda: self.updatePosition(1))
        self.secondGraphTimer.timeout.connect(lambda: self.updatePosition(2))
        self.first_plot_item = None
        self.second_plot_item = None
        self.first_line_item = None
        self.second_line_item = None
        self.load_1st_song_btn.clicked.connect(lambda: self.apply_data_recognition(1))
        self.load_2nd_song_btn.clicked.connect(lambda: self.apply_data_recognition(2))
        self.remove_1st_song_btn.clicked.connect(lambda: self.clear_audio_data(1))
        self.remove_2nd_song_btn.clicked.connect(lambda: self.clear_audio_data(2))
        self.firstGraphplayButton.clicked.connect(lambda: self.play_audio(1))
        self.secondGraphPlayButton.clicked.connect(lambda: self.play_audio(2))
        self.firstGraphreplayButton.clicked.connect(lambda: self.replay_audio(1))
        self.secondGraphReplayButton.clicked.connect(lambda: self.replay_audio(2))
        self.mix_button.clicked.connect(self.search_songs)
        self.slider.valueChanged.connect(self.update_mix_ratio)
        self.apply_modern_style()
        self.icon_paths = {
            'play': os.path.join(os.path.dirname(__file__), 'icons', 'play.png'),
            'pause': os.path.join(os.path.dirname(__file__), 'icons', 'pause.png'),
            'mix': os.path.join(os.path.dirname(__file__), 'icons', 'mix.png')
        }
        self.default_mix_button_style = f"""
            QPushButton {{
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 100,
                    fx: 0.5, fy: 0.5,
                    stop: 0 {self.colors['primary']},
                    stop: 1 {self.colors['secondary']}
                );
                border-radius: 100px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                image: url({self.icon_paths['mix']});  # Use full path from icon_paths
            }}
            QPushButton:hover {{
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 1, 
                    fx: 0.5, fy: 0.5,
                    stop: 0 {self.colors['secondary']},
                    stop: 1 {self.colors['primary']}
                );
            }}
        """
        self.loading_mix_button_style = f"""
            QPushButton {{
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 100,
                    fx: 0.5, fy: 0.5,
                    stop: 0 {self.colors['primary']},
                    stop: 1 {self.colors['secondary']}
                );
                border-radius: 100px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }}
        """        
        self.mix_button.setStyleSheet(self.default_mix_button_style)

    def update_mix_ratio(self):
        ratio = self.slider.value()
        inverse_ratio = 100 - ratio        
        self.slider_value_left.setText(f"{ratio}%")
        self.slider_value_right.setText(f"{inverse_ratio}%")        
        if self.first_file_path or self.second_file_path:
            self.perform_search(ratio/100.0)  # Convert to decimal

    def perform_search(self, mix_ratio):
        try:
            print("Slider Ratios: ", mix_ratio)
            if self.firstFileData is None and self.secondFileData is None:
                raise Exception("No songs loaded")
            if self.firstFileData is None or mix_ratio == 0:
                data_to_analyze = self.secondFileData
            elif self.secondFileData is None or mix_ratio == 1:
                data_to_analyze = self.firstFileData
            else:
                min_length = min(len(self.firstFileData), len(self.secondFileData))
                first_data = self.firstFileData[:min_length]
                second_data = self.secondFileData[:min_length]
                data_to_analyze = (mix_ratio * first_data) + ((1 - mix_ratio) * second_data)
            
            chroma_stft = librosa.feature.chroma_stft(y=data_to_analyze)
            MFCC = librosa.feature.mfcc(y=data_to_analyze)
            melspectrogram = librosa.feature.melspectrogram(y=data_to_analyze)            
            mixed_hashes = {
                "mfcc": self.hash_feature(MFCC),
                "chroma": self.hash_feature(chroma_stft),
                "mel": self.hash_feature(melspectrogram)
            }            
            similarity_result = self.compare_hashes(mixed_hashes)            
            self.rearrange_songs(similarity_result)

        except Exception as e:
            print(f"Mix and search error: {e}")

    def search_songs(self):
        try:
            # Check if both songs are loaded
            if not (self.first_file_path or self.second_file_path):
                QMessageBox.warning(self, "Warning", "Please load both songs first")
                return
            self.mix_button.setEnabled(False)            
            mix_ratio = self.slider.value() / 100.0
            self.perform_search(mix_ratio)
            self.mix_button.setEnabled(True)

        except Exception as e:
            print(f"Mix and search error: {e}")
            QMessageBox.critical(self, "Error", "Failed to mix and compare songs")
            self.mix_button.setEnabled(True)
        
    def apply_modern_style(self):
        dark_palette = """
        QMainWindow {
            background: #1a1a2e;
        }
        QWidget#centralwidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #1a1a2e, stop:1 #16213e);
        }
        QPushButton {
            background-color: #1a1a2e;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            color: #e9ecef;
            font-weight: bold;
            box-shadow: 5px 5px 10px #131324, -5px -5px 10px #212138;
        }
        QPushButton:hover {
            background-color: #212138;
        }
        QPushButton:pressed {
            background-color: #1a1a2e;
            box-shadow: inset 3px 3px 6px #131324, inset -3px -3px 6px #212138;
        }
        QTableWidget {
            background-color: #1a1a2e;
            border: none;
            border-radius: 15px;
            padding: 10px;
            box-shadow: inset 3px 3px 6px #131324, inset -3px -3px 6px #212138;
        }
        QLabel {
            background-color: #1a1a2e;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 3px 3px 6px #131324, -3px -3px 6px #212138;
            margin: 5px;
        }
        PlotWidget {
            background: #1a1a2e;
            border: none;
            border-radius: 15px;
            padding: 10px;
            box-shadow: inset 3px 3px 6px #131324, inset -3px -3px 6px #212138;
        }
        """
        self.setStyleSheet(dark_palette)
        for graph in [self.firstAudioGraph, self.secondAudioGraph]:
            graph.setBackground('#1a1a2e')
            graph.setForegroundBrush(QBrush(QColor(233, 236, 239, 30)))
            graph.showGrid(x=True, y=True, alpha=0.1)
            graph.setContentsMargins(20, 20, 20, 20)        
        for btn in [self.firstGraphplayButton, self.secondGraphPlayButton]:
            btn.setMinimumSize(50, 50)
            btn.setMaximumSize(50, 50)
            btn.setIconSize(QSize(24, 24))
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 25px;
                    background-color: #2d3436;
                    box-shadow: 5px 5px 10px #131324, -5px -5px 10px #212138;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:pressed {
                    background-color: #2d3436;
                    box-shadow: inset 3px 3px 6px #131324, inset -3px -3px 6px #212138;
                }
            """)        
        self.results_table.setShowGrid(False)
        self.results_table.horizontalHeader().setFixedHeight(50)  # Set header height
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.results_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
    

    def hash_feature(self, feature):
        return imagehash.phash((Image.fromarray(feature)), hash_size=16).__str__()
            
    def play_audio(self, fileNumber):
        try:
            if fileNumber == 1:
                if self.firstGraphPlaying:
                    self.stopAudio(1)
                    self.firstGraphPlaying = False
                    self.firstGraphTimer.stop()
                else:
                    self.firstMediaPlayer.play()
                    self.firstGraphPlaying = True
                    self.firstGraphTimer.start(100)  # Update every 100ms
            else:
                if self.secondGraphPlaying:
                    self.stopAudio(2)   
                    self.secondGraphPlaying = False
                    self.firstGraphTimer.stop()
                else:
                    self.secondMediaPlayer.play()
                    self.secondGraphPlaying = True
                    self.secondGraphTimer.start(100)
            
            self.togglePlayingIcon(fileNumber)

        except Exception as e:
            print(f"Error playing audio: {e}")
            QMessageBox.critical(self, "Error", "Failed to play audio file")

    def updatePosition(self, fileNumber):
        try:
            if fileNumber == 1:
                position = self.firstMediaPlayer.position()
                duration = self.firstMediaPlayer.duration()
                if duration > 0:
                    # Create plot only once if not exists
                    if self.first_plot_item is None:
                        self.first_plot_item = self.firstAudioGraph.plot(self.firstFileData, pen=(0,0,255))
                    normalized_pos = position / duration
                    x_pos = normalized_pos * len(self.firstFileData)
                    if self.first_line_item is not None:
                        self.firstAudioGraph.removeItem(self.first_line_item)
                    self.first_line_item = self.firstAudioGraph.addLine(x=x_pos, pen='r')
            else:
                position = self.secondMediaPlayer.position()
                duration = self.secondMediaPlayer.duration()
                if duration > 0:
                    if self.second_plot_item is None:
                        self.second_plot_item = self.secondAudioGraph.plot(self.secondFileData, pen=(0,0,255))
                    normalized_pos = position / duration
                    x_pos = normalized_pos * len(self.secondFileData)
                    if self.second_line_item is not None:
                        self.secondAudioGraph.removeItem(self.second_line_item)
                    self.second_line_item = self.secondAudioGraph.addLine(x=x_pos, pen='r')
                    
        except Exception as e:
            print(f"Error updating position: {e}")


    def stopAudio(self, fileNumber):
        if fileNumber == 1:
            self.firstMediaPlayer.pause()
            self.firstGraphPlaying = False
        else:
            self.secondMediaPlayer.pause()
            self.secondGraphPlaying = False

    def replay_audio(self, fileNumber):
        if fileNumber == 1:
            self.firstMediaPlayer.stop()
            self.firstMediaPlayer.play()
            self.firstGraphPlaying = True
        else:
            self.secondMediaPlayer.stop()
            self.secondMediaPlayer.play()
            self.secondGraphPlaying = True
        
        self.togglePlayingIcon(fileNumber)

    def togglePlayingIcon(self, fileNumber):
        try:
            if fileNumber == 1:
                icon_path = self.icon_paths['pause'] if self.firstGraphPlaying else self.icon_paths['play']
                self.firstGraphplayButton.setIcon(QIcon(icon_path))
            else:
                icon_path = self.icon_paths['pause'] if self.secondGraphPlaying else self.icon_paths['play']
                self.secondGraphPlayButton.setIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Error loading icon: {e}")

    def apply_data_recognition(self, fileNumber):
        try:
            self.mix_button.setEnabled(False)
            self.progress_bar.show()            
            song_name, filePath, audioData, samplingRate = self.load_song_file()
            if not filePath:
                raise Exception("No file selected")
                
            if fileNumber == 1:
                self.first_song_label.setText(os.path.basename(filePath))
                url = QUrl.fromLocalFile(filePath)
                self.firstFileData = audioData
                self.first_media_content = QMediaContent(url)
                self.firstMediaPlayer.setMedia(self.first_media_content)
                self.first_file_path = filePath
                self.firstAudioGraph.clear()
                self.plot_downsampled_waveform(audioData, self.firstAudioGraph)
                QTimer.singleShot(0, lambda: self.extract_features(1))
                
            else:
                # Update label with song name
                self.second_song_label.setText(os.path.basename(filePath))
                url = QUrl.fromLocalFile(filePath)
                self.secondFileData = audioData
                self.second_media_content = QMediaContent(url)
                self.secondMediaPlayer.setMedia(self.second_media_content)
                self.second_file_path = filePath
                self.secondAudioGraph.clear()
                self.plot_downsampled_waveform(audioData, self.secondAudioGraph)
                QTimer.singleShot(0, lambda: self.extract_features(2))

            self.mix_button.setEnabled(True)
            self.mix_button.setStyleSheet(self.default_mix_button_style)
            self.progress_bar.hide()
            
            if self.first_file_path and self.second_file_path:
                self.slider.setEnabled(True)

        except Exception as e:
            print(f"Recognition error: {e}")
            self.mix_button.setEnabled(True)
            self.mix_button.setStyleSheet(self.default_mix_button_style)
            if fileNumber == 1:
                self.firstAudioGraph.clear()
                self.first_song_label.setText("No song selected")
            else:
                self.secondAudioGraph.clear() 
                self.second_song_label.setText("No song selected")
            QMessageBox.critical(self, "Error", f"Failed to load audio: {str(e)}")

    def load_song_file(self, ):
        filePath, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Sound Files (*.wav , *.mp3)")
        if filePath:
            try:
                audioData, samplingRate = librosa.load(path=filePath, sr=None)
                song_name = filePath.split("/")[-1]
                return song_name, filePath , audioData, samplingRate
            except Exception as e:
                print("Failed to Load Audio File: ", e)
                return None


    def plot_downsampled_waveform(self, data, graph):
        if len(data) > self.MAX_POINTS:
            # Downsample the data
            downsample_factor = len(data) // self.MAX_POINTS
            downsampled_data = data[::downsample_factor]
            graph.plot(downsampled_data, pen=QPen(QColor("#1ED760"), 2))
        else:
            graph.plot(data, pen=QPen(QColor("#1ED760"), 2))

    def updatePosition(self, fileNumber):
        try:
            if fileNumber == 1:
                position = self.firstMediaPlayer.position()
                duration = self.firstMediaPlayer.duration()
                if duration > 0:
                    # Update position line only
                    normalized_pos = position / duration
                    x_pos = normalized_pos * self.MAX_POINTS
                    
                    if self.first_line_item is not None:
                        self.firstAudioGraph.removeItem(self.first_line_item)
                    self.first_line_item = self.firstAudioGraph.addLine(x=x_pos, pen='r')
            else:
                position = self.secondMediaPlayer.position()
                duration = self.secondMediaPlayer.duration()
                if duration > 0:
                    # Update position line only
                    normalized_pos = position / duration
                    x_pos = normalized_pos * self.MAX_POINTS
                    
                    if self.second_line_item is not None:
                        self.secondAudioGraph.removeItem(self.second_line_item)
                    self.second_line_item = self.secondAudioGraph.addLine(x=x_pos, pen='r')
                
                    
        except Exception as e:
            print(f"Error updating position: {e}")

    def extract_features(self, fileNumber):
        try:
            data = self.firstFileData if fileNumber == 1 else self.secondFileData
            features = []
            chunk_size = len(data) // 10  # Process in 10 chunks
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]                
                progress = (i / len(data)) * 100
                self.progress_bar.setValue(int(progress))                
                chroma = librosa.feature.chroma_stft(y=chunk)
                mfcc = librosa.feature.mfcc(y=chunk)
                mel = librosa.feature.melspectrogram(y=chunk)
                features.extend([chroma, mfcc, mel])                
                QApplication.processEvents()

            if fileNumber == 1:
                self.firstSpectroFeatures = features
            else:
                self.secondSpectroFeatures = features
            self.progress_bar.hide()
        except Exception as e:
            print(f"Error extracting features: {e}")
            self.progress_bar.hide()
            

    def clear_audio_data(self, FileNumber):
        try:
            print("Clearing Audio Data")
            if FileNumber == 1:
                self.firstMediaPlayer.stop()
                empty_content = QMediaContent()
                self.firstMediaPlayer.setMedia(empty_content)
                self.firstMediaPlayer.setPlaybackRate(1)
                self.firstFileData = None
                self.firstFileSpectro = None
                self.firstSpectroFeatures = []
                self.firstGraphPlaying = False
                self.firstGraphTimer.stop()
                self.first_media_content = None
                self.first_file_path = None
                self.firstAudioGraph.clear()
                self.first_song_label.setText("No song selected")
                self.togglePlayingIcon(1)
            else:
                self.secondMediaPlayer.stop()
                empty_content = QMediaContent()
                self.secondMediaPlayer.setMedia(empty_content)
                self.secondMediaPlayer.setPlaybackRate(1)
                self.secondFileData = None
                self.secondFileSpectro = None
                self.secondSpectroFeatures = []
                self.secondGraphPlaying = False
                self.secondGraphTimer.stop()
                self.second_media_content = None
                self.second_file_path = None                
                self.secondAudioGraph.clear()
                self.second_song_label.setText("No song selected")
                self.togglePlayingIcon(2)
        except Exception as e:
            print(f"Error clearing audio: {e}")
    
    def data_hashing(self, fileNumber):
        def hash_feature(feature):
            hashed_feature = imagehash.phash((Image.fromarray(feature)), hash_size=16).__str__()
            return hashed_feature
        if fileNumber == 1:
            hashed_mfcc = hash_feature(self.firstSpectroFeatures[1])
            hashed_chroma = hash_feature(self.firstSpectroFeatures[0])
            hashed_mel = hash_feature(self.firstSpectroFeatures[2])
        else:
            hashed_mfcc = hash_feature(self.secondSpectroFeatures[1])
            hashed_chroma = hash_feature(self.secondSpectroFeatures[0])
            hashed_mel = hash_feature(self.secondSpectroFeatures[2])
        print(f"{hashed_mel},{hashed_mfcc},{hashed_chroma}")
        hashing_dict = {
            "mfcc": hashed_mfcc,
            "chroma": hashed_chroma,
            "mel": hashed_mel
        }
        return hashing_dict

    def compare_hashes(self, hashing_list):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Database", "Songs_database.csv")
        csv_data = pd.read_csv(db_path)
        songs_names = csv_data.iloc[:, 0].tolist()
        mel_hashes = csv_data.iloc[:, 1].tolist()
        chroma_hashes = csv_data.iloc[:, 3].tolist()
        mfcc_hashes = csv_data.iloc[:, 2].tolist()
        file_chroma_hash = hashing_list["chroma"]
        file_mel_hash = hashing_list["mel"]
        file_mfcc_hash = hashing_list["mfcc"]
        similarity_list = []
        for i in range(len(mel_hashes)):
            song_mel = mel_hashes[i]
            song_chroma = chroma_hashes[i]
            song_mfcc = mfcc_hashes[i]
            mel_difference = hex_to_hash(file_mel_hash) - hex_to_hash(song_mel)
            chroma_difference = hex_to_hash(file_chroma_hash) - hex_to_hash(song_chroma)
            mfcc_difference = hex_to_hash(file_mfcc_hash) - hex_to_hash(song_mfcc)
            difference_average = (mel_difference + chroma_difference + mfcc_difference ) / 3
            similarity = (1 - difference_average / 255) * 100
            similarity_list.append((songs_names[i] , similarity))
        return similarity_list
    
    def rearrange_songs(self, similarity_list):
        similarity_list.sort(key=lambda x: x[1], reverse=True)
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        self.results_table.verticalHeader().setDefaultSectionSize(50)
        self.results_table.verticalHeader().setMinimumSectionSize(50)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setStretchLastSection(True)
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i in range(10):
            self.results_table.insertRow(i)
            self.results_table.setItem(i, 0, QTableWidgetItem(similarity_list[i][0]))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(f"{similarity_list[i][1]:.2f}") + "%"))
  
    def remove_song(self, song_number):
        if song_number == 1:
            self.first_song_label.setText("No song selected")
            self.first_song_path = None
            self.firstAudioGraph.clear()
        else:
            self.second_song_label.setText("No song selected")
            self.second_song_path = None
            self.secondAudioGraph.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())