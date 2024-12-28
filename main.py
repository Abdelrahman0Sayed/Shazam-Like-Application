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

class MainWindow(UI_MainWindow):
    
    def __init__(self):
        super().__init__()
        # Attributes
        self.firstFileData = None
        self.firstFileSpectro = None
        self.firstSpectroFeatures = []
        self.first_colorbar = None

        self.secondFileData = None
        self.secondFileSpectro = None
        self.secondSpectroFeatures = []
        self.second_colorbar = None

        # Lets Create Our Connections
        self.load_1st_song_btn.clicked.connect(lambda: self.apply_data_recognition(1))
        self.load_2nd_song_btn.clicked.connect(lambda: self.apply_data_recognition(2))
        self.remove_1st_song_btn.clicked.connect(lambda: self.clear_audio_data(1))
        self.remove_2nd_song_btn.clicked.connect(lambda: self.clear_audio_data(2))


    def apply_data_recognition(self, fileNumber):
        try: 
            # First we need to get the load the fileData.
            
            audioData , samplingRate = self.load_song_file()
            if fileNumber == 1:
                self.firstFileData = audioData
            else:
                self.secondFileData = audioData


            # Convert it to Spectrogram and Display it.
            self.convert_to_spectrogram(audioData, FileNumber=fileNumber)

            # Extract the Features from the Spectrogram.
            self.extract_features(fileNumber)
            print("Data Extracted Sucessfully")

            #---------------------------- We can Move the Following if we want to calculate for the mixed one (which also can be just one of the two audio files) ---------------------------------------------#
            # Hashing the Features (Preceptual Hashing).
            data_hash = self.data_hashing(fileNumber)
            print(data_hash)
            # Apply Searching on the dataset.

        except Exception as e:
            print("Recognition Failed: ", e)
            QMessageBox.critical(self, "Error", "Failed to Recognize Sound")



    def load_song_file(self):
        filePath, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Sound Files (*.wav , *.mp3)")
        if filePath:
            try:
                # Import Audio Data using Librosa
                audioData, samplingRate = librosa.load(path=filePath, sr=None)
                print("Audio Loaded Successfully")
                print(f"Sampling Rate : {samplingRate}")
                return audioData, samplingRate


            except Exception as e:
                print("Failed to Load Audio File: ", e)
                return None


    def convert_to_spectrogram(self, audioData, FileNumber):
        # Convert the data into Spectrogram + Log Scale and save it in a variable according to the FileNumber
        try:
            stft = librosa.stft(audioData)
            spectrogram = np.abs(stft)
            # Convert it Log Scale
            spectrogram_db  = librosa.amplitude_to_db(spectrogram, ref= np.max)
            if FileNumber == 1:
                self.firstGraphAxis.clear()
                audioImg = librosa.display.specshow(spectrogram_db, 
                                        sr=22050, 
                                        x_axis='time', 
                                        y_axis='hz',
                                        ax=self.firstGraphAxis, 
                                        cmap='magma')  # sr will be changed to a constant value depending on the dataset
                
                if self.first_colorbar is None:
                    self.first_colorbar = self.firstSpectrogramFig.colorbar(audioImg, ax=self.firstGraphAxis)
                self.firstFileSpectro = spectrogram_db
                self.firstGraphCanvas.draw()
            else:
                self.secondGraphAxis.clear()
                audioImg = librosa.display.specshow(spectrogram_db, 
                                         sr=22050, 
                                         x_axis='time', 
                                         y_axis='hz',
                                         ax=self.secondGraphAxis, 
                                         cmap='magma')  # sr will be changed to a constant value depending on the dataset
                if self.second_colorbar is None:
                    self.second_colorbar = self.secondSpectrogramFig.colorbar(audioImg, ax=self.secondGraphAxis)
                self.secondGraphCanvas.draw()
                self.secondFileSpectro = spectrogram_db
        except Exception as e:
            print("Spectrogram Converting Failed: ", e)
            QMessageBox.critical(self, "Error", "Failed to create spectrogram")
            return None


    def extract_features(self, fileNumber):
        # We need to Focus On the Main Features on Audio Identification like: Spectral_Centroid, Chroma_stft, MFCC, melspectrogram
        # Then we need to store it in list to pass it to the Perceptual Hashing Function 
        data = self.firstFileData if fileNumber == 1 else self.secondFileData

        
        # All we will use is Built-In functions that computes this features to use
        spectral_centroid = librosa.feature.spectral_centroid(y=data, sr=22050) # Change sr depending on the data
        chroma_stft = librosa.feature.chroma_stft(y=data, sr=22050)
        MFCC = librosa.feature.mfcc(y=data, sr=22050)
        melspectrogram = librosa.feature.melspectrogram(y=data, sr=22050)
        #melspectrogram = librosa.power_to_db(melspectrogram, ref=np.max)

        if fileNumber == 1:
            self.firstSpectroFeatures.append(spectral_centroid)
            self.firstSpectroFeatures.append(chroma_stft)
            self.firstSpectroFeatures.append(MFCC)
            self.firstSpectroFeatures.append(melspectrogram)
        else:
            self.secondSpectroFeatures.append(spectral_centroid)
            self.secondSpectroFeatures.append(chroma_stft)
            self.secondSpectroFeatures.append(MFCC)
            self.secondSpectroFeatures.append(melspectrogram)


        

    def clear_audio_data(self, FileNumber):
        try:
            print("Lets Remove Audio Data")
            if FileNumber == 1:
                # Clear All the Data of First File
                print("We need to remove First Audio File")
                self.firstGraphAxis.clear()
                self.firstGraphAxis.set_facecolor('#2b2b2b')
                self.firstGraphAxis.text(0.5, 0.5, 'Load a signal to view spectrogram',
                horizontalalignment='center', verticalalignment='center', color='#ffffff')
                self.firstGraphCanvas.draw()
                self.firstFileData = None
                self.firstFileSpectro = None
                self.firstSpectroFeatures = []
            else:
                # Clear All the Data of First File
                print("We need to remove second audio File")
                self.secondGraphAxis.clear()
                self.secondGraphAxis.clear()
                self.secondGraphAxis.set_facecolor('#2b2b2b')
                self.secondGraphAxis.text(0.5, 0.5, 'Load a signal to view spectrogram',
                horizontalalignment='center', verticalalignment='center', color='#ffffff')
                self.secondGraphCanvas.draw()
                self.secondFileData = None
                self.secondFileSpectro = None
                self.secondSpectroFeatures= []
                
        
        except Exception as e:
            print(f"Error clearing audio data: {e}")


    def data_hashing(self, fileNumber):
        #  Normalize The Features value
        normalized_features= []
        def normalize_feature(feature):
            return (feature - np.min(feature)) / (np.max(feature) - np.min(feature) + 1e-10)
        
        if fileNumber == 1:
            for feature in self.firstSpectroFeatures:
                normalized_features.append(normalize_feature(feature))
        else:
            for feature in self.secondSpectroFeatures:
                normalized_features.append(normalize_feature(feature))

        #  Combine All Features into one vector
        combined_features = np.hstack([
            normalized_features[0].flatten(), 
            normalized_features[1].flatten(), 
            normalized_features[2].flatten(), 
            normalized_features[3].flatten() 
        ])
        
        #  Digitize / Discretize the data
        binary_features = (combined_features > 0.5).astype(int)
        
        #  Convert it to a short sequence (Perceptual Hash)
        # Convert binary features to a string
        binary_string = ''.join(map(str, binary_features))

        # Generate a hash
        perceptual_hash = hashlib.sha512(binary_string.encode()).hexdigest()
        #perceptual_hash = hashlib.md5(binary_string.encode()).hexdigest()
        
        return perceptual_hash


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())