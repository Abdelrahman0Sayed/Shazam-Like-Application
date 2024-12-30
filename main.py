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


class MainWindow(UI_MainWindow):
    
    def __init__(self):
        super().__init__()
        # Attributes
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

        # Controls Attributes
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

        # Lets Create Our Connections
        self.load_1st_song_btn.clicked.connect(lambda: self.apply_data_recognition(1))
        self.load_2nd_song_btn.clicked.connect(lambda: self.apply_data_recognition(2))
        self.remove_1st_song_btn.clicked.connect(lambda: self.clear_audio_data(1))
        self.remove_2nd_song_btn.clicked.connect(lambda: self.clear_audio_data(2))
        self.firstGraphplayButton.clicked.connect(lambda: self.play_audio(1))
        self.secondGraphPlayButton.clicked.connect(lambda: self.play_audio(2))
        self.firstGraphreplayButton.clicked.connect(lambda: self.replay_audio(1))
        self.secondGraphReplayButton.clicked.connect(lambda: self.replay_audio(2))

    
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
                    
                    # Update only the vertical line position
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
        if fileNumber == 1:
            if self.firstGraphPlaying:
                self.firstGraphplayButton.setIcon(QIcon("icons/pause.png"))
            else:
                self.firstGraphplayButton.setIcon(QIcon("icons/play.png"))
        else:
            if self.secondGraphPlaying:
                self.secondGraphPlayButton.setIcon(QIcon("icons/pause.png"))
            else:
                self.secondGraphPlayButton.setIcon(QIcon("icons/play.png"))

    def apply_data_recognition(self, fileNumber):
        try:             
            song_name , filePath, audioData, samplingRate = self.load_song_file()
            if fileNumber == 1:
                url = QUrl.fromLocalFile(filePath)
                self.firstFileData = audioData
                self.first_media_content = QMediaContent(url)
                self.firstMediaPlayer.setMedia(self.first_media_content)
                self.first_file_path = filePath
                self.firstAudioGraph.plot(audioData, pen=(0,0,255))
                self.song_1_placeholder.setText(song_name)
            else:
                url = QUrl.fromLocalFile(filePath)
                self.secondFileData = audioData
                self.second_media_content = QMediaContent(url)
                self.secondMediaPlayer.setMedia(self.second_media_content)
                self.second_file_path = filePath
                self.secondAudioGraph.plot(audioData, pen=(0,0,255))
                self.song_2_placeholder.setText(song_name)
            
            print("Audio Data Loaded Sucessfully")
            self.extract_features(fileNumber)
            print("Data Extracted Sucessfully")

            hashing_dict= self.data_hashing(fileNumber)
            print("Hashing Completed")
            similarity_result = self.compare_hashes(hashing_dict)
            print("Hashes Compared")
            self.rearrange_songs(similarity_result)

        except Exception as e:
            print("Recognition Failed: ", e)
            QMessageBox.critical(self, "Error", "Failed to Recognize Sound")



    def load_song_file(self, ):
        filePath, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Sound Files (*.wav , *.mp3)")
        if filePath:
            try:
                # Import Audio Data using Librosa
                audioData, samplingRate = librosa.load(path=filePath, sr=None)
                song_name = filePath.split("/")[-1]
                return song_name, filePath , audioData, samplingRate


            except Exception as e:
                print("Failed to Load Audio File: ", e)
                return None


    def extract_features(self, fileNumber): 
        try:
            if fileNumber == 1:
                data = self.firstFileData
            else:
                data = self.secondFileData

            chroma_stft = librosa.feature.chroma_stft(y=data, sr=22050)
            MFCC = librosa.feature.mfcc(y=data, sr=22050)
            melspectrogram = librosa.feature.melspectrogram(y=data, sr=22050)

            if fileNumber == 1:
                self.firstSpectroFeatures.append(chroma_stft)
                self.firstSpectroFeatures.append(MFCC)
                self.firstSpectroFeatures.append(melspectrogram)
            else:
                self.secondSpectroFeatures.append(chroma_stft)
                self.secondSpectroFeatures.append(MFCC)
                self.secondSpectroFeatures.append(melspectrogram)

        except Exception as e:
            print(f"Error extracting features: {e}")
            QMessageBox.critical(self, "Error", "Failed to extract features")
            

    def clear_audio_data(self, FileNumber):
        try:
            print("Clearing Audio Data")
            if FileNumber == 1:
                # Stop and clear first player
                self.firstMediaPlayer.stop()
                empty_content = QMediaContent()  # Create empty media content
                self.firstMediaPlayer.setMedia(empty_content)
                self.firstMediaPlayer.setPlaybackRate(1)
                
                # Clear data
                self.firstFileData = None
                self.firstFileSpectro = None
                self.firstSpectroFeatures = []
                self.firstGraphPlaying = False
                self.firstGraphTimer.stop()
                self.first_media_content = None
                self.first_file_path = None
                
                # Clear graph
                self.firstAudioGraph.clear()
                self.song_1_placeholder.setText("group_XX_song_XX")
                self.togglePlayingIcon(1)
            else:
                # Stop and clear second player
                self.secondMediaPlayer.stop()
                empty_content = QMediaContent()  # Create empty media content
                self.secondMediaPlayer.setMedia(empty_content)
                self.secondMediaPlayer.setPlaybackRate(1)
                
                # Clear data
                self.secondFileData = None
                self.secondFileSpectro = None
                self.secondSpectroFeatures = []
                self.secondGraphPlaying = False
                self.secondGraphTimer.stop()
                self.second_media_content = None
                self.second_file_path = None
                
                # Clear graph
                self.secondAudioGraph.clear()
                self.song_2_placeholder.setText("group_XX_song_XX")
                self.togglePlayingIcon(2)
                
        except Exception as e:
            print(f"Error clearing audio: {e}")




    
    def data_hashing(self, fileNumber):
        def hash_feature(feature):
            hashed_feature = imagehash.phash((Image.fromarray(feature)), hash_size=16).__str__()
            return hashed_feature
        
        # ------------------------------------------- Edit The Following and make applied on the mixed music between the two songs --------------------- #
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
        # Read CSV File of Database to Compare it with the all songs
        csv_data = pd.read_csv("Database/Songs_database.csv")

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
        # Sort the List for the Heighest 10 Similarity values
        similarity_list.sort(key=lambda x: x[1], reverse=True)
        print("Sorted List: ", similarity_list)
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        for i in range(10):
            self.results_table.insertRow(i)
            self.results_table.setItem(i, 0, QTableWidgetItem(similarity_list[i][0]))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(f"{similarity_list[i][1]:.2f}") + "%"))
            self.results_table.resizeColumnsToContents()
            self.results_table.resizeRowsToContents()
            self.results_table.horizontalHeader().setStretchLastSection(True)
            self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.results_table.verticalHeader().setStretchLastSection(True)
            self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())