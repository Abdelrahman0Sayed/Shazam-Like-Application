from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout ,QFileDialog, QMessageBox
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.io import wavfile
from scipy import signal
import numpy as np
import librosa
import librosa.display
import imagehash
from PIL import Image
import hashlib

class UI_MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Song Fingerprint")
        self.setGeometry(100, 100, 1200, 800)
        self.setupUi()

    def setupUi(self):
        # Variables to store loaded file paths
        self.first_song_path = None
        self.second_song_path = None
        self.songs_features={}

        # Apply dark theme
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #5c5c5c;
                padding: 5px;
                width: 150px;
            }
            QPushButton:hover {
                background-color: #4c4f51;
            }
            QSlider::groove:horizontal {
                background: #3c3f41;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #5c5c5c;
                border: 1px solid #3c3f41;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QTableWidget {
                background-color: #3c3f41;
                gridline-color: #5c5c5c;
            }
            QHeaderView::section {
                background-color: #3c3f41;
                border: 1px solid #5c5c5c;
                padding: 4px;
            }
            QScrollBar:vertical {
                background: #2b2b2b;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #5c5c5c;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QLineEdit {
                border: none;
                background: transparent;
                color: #ffffff;
                text-align: center;
            }
            """
        )
        # Layout setup
        layout = QtWidgets.QVBoxLayout(self)

        # Top buttons and placeholders
        top_layout = QtWidgets.QHBoxLayout()

        
        self.load_1st_song_btn = QtWidgets.QPushButton("Load 1st Song")
        self.load_1st_song_btn.setFixedWidth(150)
        self.song_1_placeholder = QtWidgets.QLineEdit("group_XX_song_XX")
        self.song_1_placeholder.setReadOnly(True)
        self.song_1_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.remove_1st_song_btn = QtWidgets.QPushButton("Remove")
        self.remove_1st_song_btn.setFixedWidth(150)
        

        self.load_2nd_song_btn = QtWidgets.QPushButton("Load 2nd Song")
        self.load_2nd_song_btn.setFixedWidth(150)
        self.song_2_placeholder = QtWidgets.QLineEdit("group_XX_song_XX")
        self.song_2_placeholder.setReadOnly(True)
        self.song_2_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.remove_2nd_song_btn = QtWidgets.QPushButton("Remove")
        self.remove_2nd_song_btn.setFixedWidth(150)

        song_1_layout = QtWidgets.QVBoxLayout()
        song_1_layout.addWidget(self.load_1st_song_btn, alignment=QtCore.Qt.AlignCenter)
        song_1_layout.addWidget(self.song_1_placeholder)
        song_1_layout.addWidget(self.remove_1st_song_btn, alignment=QtCore.Qt.AlignCenter)

        song_2_layout = QtWidgets.QVBoxLayout()
        song_2_layout.addWidget(self.load_2nd_song_btn, alignment=QtCore.Qt.AlignCenter)
        song_2_layout.addWidget(self.song_2_placeholder)
        song_2_layout.addWidget(self.remove_2nd_song_btn, alignment=QtCore.Qt.AlignCenter)

        # Slider and search button
        slider_layout = QtWidgets.QVBoxLayout()
        self.slider_value_left = QtWidgets.QLineEdit("50%")
        self.slider_value_left.setReadOnly(True)
        self.slider_value_left.setAlignment(QtCore.Qt.AlignCenter)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider_value_right = QtWidgets.QLineEdit("50%")
        self.slider_value_right.setReadOnly(True)
        self.slider_value_right.setAlignment(QtCore.Qt.AlignCenter)
        self.search_btn = QtWidgets.QPushButton("Search")

        slider_control_layout = QtWidgets.QHBoxLayout()
        slider_control_layout.addWidget(self.slider_value_left)
        slider_control_layout.addWidget(self.slider)
        slider_control_layout.addWidget(self.slider_value_right)

        slider_layout.addLayout(slider_control_layout)
        slider_layout.addWidget(self.search_btn, alignment=QtCore.Qt.AlignCenter)

        top_layout.addLayout(song_1_layout)
        top_layout.addLayout(slider_layout)
        top_layout.addLayout(song_2_layout)

        layout.addLayout(top_layout)

        # Spectrogram placeholders
        spectrogram_layout = QtWidgets.QHBoxLayout()

        # First spectrogram setup
        self.firstSpectrogramFig = Figure(figsize=(6, 3), constrained_layout=True)
        self.firstSpectrogramFig.patch.set_facecolor('#2b2b2b')
        self.firstGraphCanvas = FigureCanvas(self.firstSpectrogramFig)
        self.firstGraphAxis = self.firstSpectrogramFig.add_subplot(111)
        self.firstGraphAxis.set_facecolor('#2b2b2b')
        self.firstGraphAxis.text(0.5, 0.5, 'Load a signal to view spectrogram',
            horizontalalignment='center', verticalalignment='center', color='#ffffff')

        # Second spectrogram setup
        self.secondSpectrogramFig = Figure(figsize=(6, 3), constrained_layout=True)
        self.secondSpectrogramFig.patch.set_facecolor('#2b2b2b')
        self.secondGraphCanvas = FigureCanvas(self.secondSpectrogramFig)
        self.secondGraphAxis = self.secondSpectrogramFig.add_subplot(111)
        self.secondGraphAxis.set_facecolor('#2b2b2b')
        self.secondGraphAxis.text(0.5, 0.5, 'Load a signal to view spectrogram',
            horizontalalignment='center', verticalalignment='center', color='#ffffff')

        # Add spectrogram canvases to layout
        spectrogram_layout.addWidget(self.firstGraphCanvas)
        spectrogram_layout.addWidget(self.secondGraphCanvas)

        layout.addLayout(spectrogram_layout)

        # Results label and table
        results_layout = QtWidgets.QVBoxLayout()
        self.results_label = QtWidgets.QLabel("Results")
        self.results_label.setAlignment(QtCore.Qt.AlignCenter)

        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setRowCount(51) # 17 song * 3   ( song , music , vocals )
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Matches", "Percentages"])
        self.results_table.verticalHeader().setVisible(True)
        self.results_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.results_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.results_table.setFixedHeight(500)

        results_layout.addWidget(self.results_label)
        results_layout.addWidget(self.results_table)

        layout.addLayout(results_layout)

        # Connect buttons to functions
        self.load_1st_song_btn.clicked.connect(self.load_first_song)
        self.load_2nd_song_btn.clicked.connect(self.load_second_song)
        self.remove_1st_song_btn.clicked.connect(self.remove_first_song)
        self.remove_2nd_song_btn.clicked.connect(self.remove_second_song)
        # Connect slider movement to the update function
        self.slider.valueChanged.connect(self.update_slider_percentages)


    def load_first_song(self):
            """
            Load the first song file and display its name in the placeholder.
            """
            file_path, _ = QFileDialog.getOpenFileName(self, "Load First Song", "", "Audio Files (*.wav)")
            if file_path:
                self.first_song_path = file_path
                self.song_1_placeholder.setText(os.path.basename(file_path))
                #QMessageBox.information(self, "Success", f"Loaded: {os.path.basename(file_path)}")
                signal_data, sampling_rate = librosa.load(file_path)
                self.first_song_data = signal_data
                self.first_sampling_rate = sampling_rate
                # Plot the spectrogram for the first song
                self.plotSpectrogram()
            # # except Exception as e:
            # #     QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load the first song:\n{str(e)}")
            # # Calculate the spectrogram and hash the features
            f, t, spectrogram = signal.spectrogram(signal_data, fs=sampling_rate, window='hann')
            features = self.Features(signal_data, sampling_rate, spectrogram)  # You can pass None for spectro here, librosa will handle it
            # Create song dictionary and store hashed features
            song_dict = self.create_song_dict(file_path)
            song_dict[file_path]["spectrogram_Hash"] = self.Hash(spectrogram)
            song_dict[file_path]['melspectrogram_Hash'] = self.Hash(features['melspectro'])
            song_dict[file_path]['mfcc_Hash'] = self.Hash(features['mfccs'])
            song_dict[file_path]['chroma_stft_Hash'] = self.Hash(features['chroma_stft'])
            song_dict[file_path]['spectral_centroid_Hash'] = self.Hash(features['spectral_centroid'])
            # Store the dictionary for the first song in a dictionary with 'first_song' key
            self.songs_features['first_song'] = song_dict

    def load_second_song(self):
        """
        Load the second song file and display its name in the placeholder.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Second Song", "", "Audio Files (*.wav)")
        if file_path:
            self.second_song_path = file_path
            self.song_2_placeholder.setText(os.path.basename(file_path))
            #QMessageBox.information(self, "Success", f"Loaded: {os.path.basename(file_path)}")
            signal_data, sampling_rate = librosa.load(file_path)
            self.second_song_data = signal_data
            self.second_sampling_rate = sampling_rate
            # Plot the spectrogram for the second song
            self.plotSpectrogram()
        # # except Exception as e:
        # #     QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load the second song:\n{str(e)}")
        # Calculate the spectrogram and hash the features
        f, t, spectrogram = signal.spectrogram(signal_data, fs=sampling_rate, window='hann')
        features = self.Features(signal_data, sampling_rate, spectrogram)  # You can pass None for spectro here, librosa will handle it
        # Create song dictionary and store hashed features
        song_dict = self.create_song_dict(file_path)
        song_dict[file_path]["spectrogram_Hash"] = self.Hash(spectrogram)
        song_dict[file_path]['melspectrogram_Hash'] = self.Hash(features['melspectro'])
        song_dict[file_path]['mfcc_Hash'] = self.Hash(features['mfccs'])
        song_dict[file_path]['chroma_stft_Hash'] = self.Hash(features['chroma_stft'])
        song_dict[file_path]['spectral_centroid_Hash'] = self.Hash(features['spectral_centroid'])
        # Store the dictionary for the second song in a dictionary with 'second_song' key
        self.songs_features['second_song'] = song_dict

    def remove_first_song(self):
        """
        Remove the first song selection.
        """
        if self.first_song_path:
            self.first_song_path = None
            self.song_1_placeholder.setText("group_XX_song_XX")
            self.first_song_data = None
            self.first_sampling_rate = None
            # Clear the song features from the dictionary
            if 'first_song' in self.songs_features:
                del self.songs_features['first_song']
            # Clear the spectrogram plot (reset the axes and redrawing empty text)
            self.firstGraphAxis.clear()
            self.firstGraphAxis.set_facecolor('#2b2b2b')  # Keep the background color
            self.firstGraphAxis.text(0.5, 0.5, 'No song loaded',
                horizontalalignment='center', verticalalignment='center', color='#ffffff')
            self.firstGraphCanvas.draw()  # Redraw the canvas
        #     QMessageBox.information(self, "Removed", "First song has been removed.")
        # else:
        #     QMessageBox.warning(self, "Warning", "No first song to remove.")

    def remove_second_song(self):
        """
        Remove the second song selection.
        """
        if self.second_song_path:
            self.second_song_path = None
            self.song_2_placeholder.setText("group_XX_song_XX")
            self.second_song_data = None
            self.second_sampling_rate = None
            # Clear the song features from the dictionary
            if 'second_song' in self.songs_features:
                del self.songs_features['second_song']
            # Clear the spectrogram plot (reset the axes and redrawing empty text)
            self.secondGraphAxis.clear()
            self.secondGraphAxis.set_facecolor('#2b2b2b')  # Keep the background color
            self.secondGraphAxis.text(0.5, 0.5, 'No song loaded',
                horizontalalignment='center', verticalalignment='center', color='#ffffff')
            self.secondGraphCanvas.draw()  # Redraw the canvas
        #     QMessageBox.information(self, "Removed", "Second song has been removed.")
        # else:
        #     QMessageBox.warning(self, "Warning", "No second song to remove.")

    def update_slider_percentages(self):
        """
        Update the percentages displayed on the left and right of the slider.
        """
        left_percentage = self.slider.value()
        right_percentage = 100 - left_percentage
        self.slider_value_left.setText(f"{left_percentage}%")
        self.slider_value_right.setText(f"{right_percentage}%")
        # Call the method to compute the weighted average whenever the slider value changes
        self.compute_weighted_average()

    def plotSpectrogram(self):
        """
        Plot spectrograms for the loaded songs with zero handling.
        """
        def plot_single_spectrogram(signal_data, sampling_rate, axis, canvas, title):
            if signal_data is None or len(signal_data) == 0:
                return False
                
            # Calculate spectrogram with validation
            f, t, Sxx = signal.spectrogram(signal_data, fs=sampling_rate, window='hann')
            
            # Add small constant to avoid log(0)
            eps = np.finfo(float).eps
            log_spec = np.log(Sxx + eps)
            
            # Plot spectrogram
            axis.clear()
            axis.set_title(title)
            axis.set_xlabel('Time (s)')
            axis.set_ylabel('Frequency (Hz)')
            img = librosa.display.specshow(
                log_spec, 
                x_axis='time', 
                y_axis='log', 
                sr=sampling_rate, 
                ax=axis
            )
            axis.set_facecolor('#2b2b2b')
            canvas.draw()
            return True

        # Plot first song
        if hasattr(self, 'first_song_data'):
            plot_single_spectrogram(
                self.first_song_data,
                self.first_sampling_rate,
                self.firstGraphAxis,
                self.firstGraphCanvas,
                'First Song Spectrogram'
            )

        # Plot second song
        if hasattr(self, 'second_song_data'):
            plot_single_spectrogram(
                self.second_song_data,
                self.second_sampling_rate,
                self.secondGraphAxis,
                self.secondGraphCanvas,
                'Second Song Spectrogram'
            )

    def Features(self, file_data, sr, spectro):
        features = {}
        
        # Spectrogram (magnitude spectrogram)  let librosa compute the spectrogram
        features['melspectro'] = librosa.feature.melspectrogram(y=file_data, sr=sr)
        
        # Chroma STFT (Chromagram from short-time Fourier transform)
        features['chroma_stft'] = librosa.feature.chroma_stft(y=file_data, sr=sr)
        
        # MFCCs (Mel-frequency cepstral coefficients)
        features['mfccs'] = librosa.feature.mfcc(y=file_data.astype('float64'), sr=sr)
        
        # Spectral Centroid (measure of brightness)
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=file_data, sr=sr)
        
        return features
    
    def Hash(self,feature):
        """
        Computes a perceptual hash of the given feature using a 16-bit hash size.
        """
        data = Image.fromarray(feature)
        return imagehash.phash(data, hash_size=16).__str__()

    def create_song_dict(self, file_name):
        """
        Creates a dictionary for storing song features and hashes.
        """
        song_dict = {
            file_name: {
                "spectrogram_Hash": None,
                "melspectrogram_Hash": None,
                "mfcc_Hash": None,
                "chroma_stft_Hash": None,
                "spectral_centroid_Hash": None
            }
        }
        return song_dict

    def compute_weighted_average(self):
        """
        Compute the weighted average of the first and second song data based on the slider value.
        """
        if hasattr(self, 'first_song_data') and hasattr(self, 'second_song_data'):
            slider_value = self.slider.value()  # Get the slider value (0-100)
            weight_first_song = slider_value / 100
            weight_second_song = 1 - weight_first_song
            # Make sure the two songs have the same length by trimming the longer one or padding the shorter one
            min_length = min(len(self.first_song_data), len(self.second_song_data))
            first_song_trimmed = self.first_song_data[:min_length]
            second_song_trimmed = self.second_song_data[:min_length]
            # Weighted sum
            weighted_signal = weight_first_song * first_song_trimmed + weight_second_song * second_song_trimmed
            # Store the new weighted signal and treat it as a new song
            self.new_song_data = weighted_signal
            self.new_sampling_rate = self.first_sampling_rate  # Assuming both songs have the same sampling rate
            # compute the features and store them as you did for the original songs
            f, t, spectrogram = signal.spectrogram(weighted_signal, fs=self.new_sampling_rate, window='hann')
            features = self.Features(weighted_signal, self.new_sampling_rate, spectrogram)
            song_dict = self.create_song_dict("weighted_song")
            song_dict["weighted_song"]["spectrogram_Hash"] = self.Hash(spectrogram)
            song_dict["weighted_song"]['melspectrogram_Hash'] = self.Hash(features['melspectro'])
            song_dict["weighted_song"]['mfcc_Hash'] = self.Hash(features['mfccs'])
            song_dict["weighted_song"]['chroma_stft_Hash'] = self.Hash(features['chroma_stft'])
            song_dict["weighted_song"]['spectral_centroid_Hash'] = self.Hash(features['spectral_centroid'])
            self.songs_features['weighted_song'] = song_dict



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UI_MainWindow()
    window.show()
    sys.exit(app.exec_())