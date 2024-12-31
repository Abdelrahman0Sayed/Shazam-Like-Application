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
import pyqtgraph as pg

class UI_MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Song Fingerprint")
        self.setGeometry(100, 100, 1200, 800)
        self.colors = {
            'background': '#0A0E17',  # Darker background
            'primary': '#00C6FF',     # Brighter blue
            'secondary': '#1ED760',   # Spotify green
            'text': '#FFFFFF',        # White text
            'surface': '#1A1E2E',     # Darker surface color
            'gradient_start': '#060B18', # Darker gradient
            'gradient_end': '#1A1E2E',   # Matching surface color
            'accent': '#FF0266',      # Hot pink accent
            'success': '#2EBD59',     # Success color
            'error': '#FF3B3B',       # Error color
            'warning': '#FFBE0B',     # Warning color
            'muted': '#6C7693'        # Muted text color
        }

        
        self.setupUi()

    def setupUi(self):

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # Create a widget to hold all content
        content_widget = QtWidgets.QWidget()
        scroll.setWidget(content_widget)
        
        # Main layout for the content widget
        layout = QtWidgets.QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Variables to store loaded file paths
        self.first_song_path = None
        self.second_song_path = None
        self.songs_features={}

        # --------------------- Icons --------------------- #
        self.icon_paths = {
            'play': os.path.join(os.path.dirname(__file__), 'icons', 'play.png'),
            'pause': os.path.join(os.path.dirname(__file__), 'icons', 'pause.png'),
            'replay': os.path.join(os.path.dirname(__file__), 'icons', 'replay.png'),
            'mix': os.path.join(os.path.dirname(__file__), 'icons', 'mix.png')  # Add mix icon path
        }

        self.playIcon = QtGui.QIcon(self.icon_paths['play'])
        self.replayIcon = QtGui.QIcon(self.icon_paths['replay'])
        self.stopButton = QtGui.QIcon(self.icon_paths['pause'])


        # Apply dark theme
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.colors['gradient_start']},
                    stop: 1 {self.colors['gradient_end']}
                );
                color: {self.colors['text']};
            }}
            QPushButton {{
                background-color: {self.colors['secondary']};
                border: none;
                border-radius: 25px;
                padding: 15px;
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary']};
            }}
            QSlider::groove:horizontal {{
                background: {self.colors['secondary']};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.colors['primary']};
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)

        self.slider_style = f"""
            QSlider::groove:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['primary']},
                    stop:1 {self.colors['secondary']}
                );
                height: 6px;
                border-radius: 3px;
                margin: 0 -4px;
            }}

            QSlider::handle:horizontal {{
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                    stop:0 {self.colors['text']},
                    stop:1 {self.colors['primary']}
                );
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
                border: 2px solid {self.colors['primary']};
                box-shadow: 0 0 5px {self.colors['primary']};
            }}

            QSlider::handle:horizontal:hover {{
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                    stop:0 {self.colors['text']},
                    stop:1 {self.colors['secondary']}
                );
                border: 2px solid {self.colors['secondary']};
                box-shadow: 0 0 10px {self.colors['secondary']};
                transform: scale(1.1);
            }}

            QSlider::sub-page:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['primary']},
                    stop:1 {self.colors['secondary']}
                );
                border-radius: 3px;
            }}

            QSlider::add-page:horizontal {{
                background: {self.colors['surface']};
                border-radius: 3px;
            }}
        """

        # Graph style
        self.graph_style = f"""
            PlotWidget {{
                background: {self.colors['surface']};
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 10px;
            }}
        """

        # Update the table style
        self.table_style = f"""
            QTableWidget {{
                background: {self.colors['surface']};
                border-radius: 15px;
                gridline-color: rgba(255, 255, 255, 0.05);
                border: none;
                padding: 15px;
                selection-background-color: {self.colors['primary']};
                color: {self.colors['text']};  /* Set text color */
                font-size: 14px;
                font-weight: normal;
            }}

            
            
            QTableWidget::item {{
                padding: 15px;  /* Increased padding */
                border-radius: 8px;
                color: {self.colors['text']};
                margin: 5px;
                border: none;
                min-height: 50px;  /* Minimum height for cells */
                font-size: 14px;
            }}
            
            QTableWidget::item:hover {{
                background: rgba(255, 255, 255, 0.1);
                color: {self.colors['text']};  /* Keep text visible on hover */
            }}
            
            QTableWidget::item:selected {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.colors['primary']},
                    stop:1 {self.colors['secondary']}
                );
                color: {self.colors['background']};  /* Text color when selected */
                font-weight: bold;
            }}
            
            QHeaderView::section {{
                padding: 15px;
                border: none;
                background: rgba(255, 255, 255, 0.1);
                color: {self.colors['text']};  /* Keep text visible on hover */
                font-weight: bold;
                font-size: 14px;
                border-radius: 0px;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {self.colors['surface']};
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {self.colors['primary']};
                border-radius: 5px;
                min-height: 20px;
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {self.colors['surface']};
                height: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {self.colors['primary']};
                border-radius: 5px;
                min-width: 20px;
            }}
        """

        # Button style
        self.button_style = f"""
            QPushButton {{
                background: {self.colors['surface']};
                border-radius: 10px;
                padding: 8px 30px;
                color: {self.colors['text']};
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            QPushButton:hover {{
                background: {self.colors['primary']};
                color: {self.colors['background']};
            }}
        """

        self.mix_button_style = f"""
            QPushButton {{
            background: qradialgradient(
                cx: 0.5, cy: 0.5, radius: 1,
                fx: 0.5, fy: 0.5,
                stop: 0 {self.colors['primary']},
                stop: 1 {self.colors['secondary']}
            );
            border-radius: 75px;
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

        

        # Central layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(20)

        # Mix button (left side)
        self.mix_button = QtWidgets.QPushButton()
        mix_icon = QtGui.QIcon(self.icon_paths['mix'])
        self.mix_button.setIcon(mix_icon)
        self.mix_button.setIconSize(QtCore.QSize(50, 50))  # Set icon size to half of button size
        self.mix_button.setFixedSize(200, 200)  # Slightly smaller size
        self.mix_button.setStyleSheet(f"""
            QPushButton {{
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 1,
                    fx: 0.5, fy: 0.5,
                    stop: 0 {self.colors['primary']},
                    stop: 1 {self.colors['secondary']}
                );
                border-radius: 75px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                image: url({self.icon_paths['mix']});  # Use full path from icon_paths
            }}
            QPushButton:hover {{
                background-color: {self.colors['secondary']};
            }}
        """)

        # Song controls container (right side)
        songs_container = QtWidgets.QWidget()
        songs_container.setStyleSheet(f"""
            QWidget {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 20px;
            }}
        """)

        songs_container.setFixedHeight(200)

        songs_layout = QtWidgets.QVBoxLayout(songs_container)
        songs_layout.setSpacing(15)

        # First song row
        first_song_layout = QtWidgets.QHBoxLayout()
        self.load_1st_song_btn = self.create_song_button("Select First Song")
        self.load_1st_song_btn.setFixedWidth(200)
        self.first_song_label = QtWidgets.QLabel("No song selected")
        self.first_song_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background: {self.colors['surface']};
                border-radius: 10px;
                padding: 8px 15px;
                font-weight: medium;
            }}
        """)
        self.remove_1st_song_btn = QtWidgets.QPushButton("Remove")
        self.remove_1st_song_btn.setStyleSheet(self.button_style)
        self.remove_1st_song_btn.setFixedWidth(200)

        first_song_layout.addWidget(self.load_1st_song_btn)
        first_song_layout.addWidget(self.first_song_label, stretch=1)
        first_song_layout.addWidget(self.remove_1st_song_btn)

        # Second song row
        second_song_layout = QtWidgets.QHBoxLayout()
        self.load_2nd_song_btn = self.create_song_button("Select Second Song")
        self.load_2nd_song_btn.setFixedWidth(200)
        self.second_song_label = QtWidgets.QLabel("No song selected")
        self.second_song_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background: {self.colors['surface']};
                border-radius: 10px;
                padding: 8px 15px;
                font-weight: medium;
            }}
        """)
        self.remove_2nd_song_btn = QtWidgets.QPushButton("Remove")
        self.remove_2nd_song_btn.setStyleSheet(self.button_style)
        self.remove_2nd_song_btn.setFixedWidth(200)

        second_song_layout.addWidget(self.load_2nd_song_btn)
        second_song_layout.addWidget(self.second_song_label, stretch=1)
        second_song_layout.addWidget(self.remove_2nd_song_btn)

        # Add all layouts
        songs_layout.addLayout(first_song_layout)
        songs_layout.addLayout(second_song_layout)

        
        # Mixing slider
        slider_container = QtWidgets.QWidget()
        slider_layout = QtWidgets.QHBoxLayout(slider_container)
        slider_layout.setSpacing(15)
        slider_container.setFixedHeight(60)
        
        # Create labels and slider in same row
        self.slider_value_left = QtWidgets.QLabel("50%")
        self.slider_value_left.setMinimumWidth(60)  # Ensure enough width for text
        self.slider_value_left.setAlignment(QtCore.Qt.AlignCenter)  # Center the text
        self.slider_value_left.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background: {self.colors['surface']};
                border-radius: 10px;
                padding: 5px;
                font-weight: bold;
            }}
        """)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.setFixedHeight(40)
        self.slider_value_right = QtWidgets.QLabel("50%")
        self.slider_value_right.setFixedHeight(40)
        self.slider_value_right.setMinimumWidth(60)
        self.slider_value_right.setAlignment(QtCore.Qt.AlignCenter)
        self.slider_value_right.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                background: {self.colors['surface']};
                border-radius: 10px;
                padding: 5px;
                font-weight: bold;
            }}
        """)
        
        # Add widgets to horizontal layout
        slider_layout.addWidget(self.slider_value_left)
        slider_layout.addWidget(self.slider, stretch=1)
        slider_layout.addWidget(self.slider_value_right)
        
        
        # Add components to main layout

        songs_layout.addWidget(slider_container)

        # Add mix button and songs container to top layout
        top_layout.addWidget(self.mix_button, alignment=QtCore.Qt.AlignLeft)
        top_layout.addWidget(songs_container, stretch=1)


        # Add top layout to main layout
        layout.addLayout(top_layout)
        


        # # Top buttons and placeholders
        # top_layout = QtWidgets.QHBoxLayout()

        
        # self.load_1st_song_btn = QtWidgets.QPushButton("Load 1st Song")
        # self.load_1st_song_btn.setFixedWidth(150)
        # self.song_1_placeholder = QtWidgets.QLineEdit("group_XX_song_XX")
        # self.song_1_placeholder.setReadOnly(True)
        # self.song_1_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        # self.remove_1st_song_btn = QtWidgets.QPushButton("Remove")
        # self.remove_1st_song_btn.setFixedWidth(150)
        

        # self.load_2nd_song_btn = QtWidgets.QPushButton("Load 2nd Song")
        # self.load_2nd_song_btn.setFixedWidth(150)
        # self.song_2_placeholder = QtWidgets.QLineEdit("group_XX_song_XX")
        # self.song_2_placeholder.setReadOnly(True)
        # self.song_2_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        # self.remove_2nd_song_btn = QtWidgets.QPushButton("Remove")
        # self.remove_2nd_song_btn.setFixedWidth(150)

        # song_1_layout = QtWidgets.QVBoxLayout()
        # song_1_layout.addWidget(self.load_1st_song_btn, alignment=QtCore.Qt.AlignCenter)
        # song_1_layout.addWidget(self.song_1_placeholder)
        # song_1_layout.addWidget(self.remove_1st_song_btn, alignment=QtCore.Qt.AlignCenter)

        # song_2_layout = QtWidgets.QVBoxLayout()
        # song_2_layout.addWidget(self.load_2nd_song_btn, alignment=QtCore.Qt.AlignCenter)
        # song_2_layout.addWidget(self.song_2_placeholder)
        # song_2_layout.addWidget(self.remove_2nd_song_btn, alignment=QtCore.Qt.AlignCenter)

        # # Slider and search button
        # slider_layout = QtWidgets.QVBoxLayout()
        # self.slider_value_left = QtWidgets.QLineEdit("50%")
        # self.slider_value_left.setReadOnly(True)
        # self.slider_value_left.setAlignment(QtCore.Qt.AlignCenter)
        # self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # self.slider.setRange(0, 100)
        # self.slider.setValue(50)
        # self.slider_value_right = QtWidgets.QLineEdit("50%")
        # self.slider_value_right.setReadOnly(True)
        # self.slider_value_right.setAlignment(QtCore.Qt.AlignCenter)
        # self.search_btn = QtWidgets.QPushButton("Search")

        # slider_control_layout = QtWidgets.QHBoxLayout()
        # slider_control_layout.addWidget(self.slider_value_left)
        # slider_control_layout.addWidget(self.slider)
        # slider_control_layout.addWidget(self.slider_value_right)

        # slider_layout.addLayout(slider_control_layout)
        # slider_layout.addWidget(self.search_btn, alignment=QtCore.Qt.AlignCenter)

        # top_layout.addLayout(song_1_layout)
        # top_layout.addLayout(slider_layout)
        # top_layout.addLayout(song_2_layout)
        

        # layout.addLayout(top_layout)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a2e;
                border: none;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        self.progress_bar.hide()
        
        # Add progress bar to layout
        layout.addWidget(self.progress_bar)

        # Spectrogram placeholders


        self.firstGraphplayButton = QPushButton()
        self.firstGraphplayButton.setIcon(self.playIcon)
        self.firstGraphplayButton.iconSize = QtCore.QSize(50, 50)


        self.firstGraphreplayButton = QPushButton()
        self.firstGraphreplayButton.setStyleSheet(self.button_style)
        self.firstGraphreplayButton.setIcon(self.replayIcon)
        self.firstGraphreplayButton.iconSize = QtCore.QSize(50, 50)


        # Spectrogram placeholders
        # Main layout for spectrograms
        spectrogram_layout = QtWidgets.QHBoxLayout()
        
        # First graph container
        graph1_container = QtWidgets.QWidget()
        graph1_layout = QtWidgets.QVBoxLayout(graph1_container)
        
        # Setup first graph
        self.firstAudioGraph = pg.PlotWidget()
        self.firstAudioGraph.showGrid(x=True, y=True)
        self.firstAudioGraph.setBackground('#2b2b2b')
        self.firstAudioGraph.setMinimumHeight(300)  # Set minimum height
        self.firstAudioGraph.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        graph1_layout.addWidget(self.firstAudioGraph)
        
        # Controls layout
        graph1_controls = QtWidgets.QHBoxLayout()
        graph1_controls.addWidget(self.firstGraphplayButton)
        graph1_controls.addWidget(self.firstGraphreplayButton)
        graph1_layout.addLayout(graph1_controls)
        
        # Add to main spectrogram layout
        spectrogram_layout.addWidget(graph1_container)
        

        graph2_container = QtWidgets.QWidget(self)
        graph2_layout = QtWidgets.QVBoxLayout(graph2_container)

        # Second graph setup
        self.secondAudioGraph = pg.PlotWidget()
        self.secondAudioGraph.showGrid(x=True, y=True)
        self.secondAudioGraph.setBackground('#2b2b2b')
        self.secondAudioGraph.setMinimumHeight(300)
        self.secondAudioGraph.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        graph2_layout.addWidget(self.secondAudioGraph)


        self.secondGraphPlayButton = QPushButton()
        self.secondGraphPlayButton.setIcon(self.playIcon)
        self.secondGraphPlayButton.iconSize = QtCore.QSize(50, 50)

        self.secondGraphReplayButton = QPushButton()
        self.secondGraphReplayButton.setStyleSheet(self.button_style)
        self.secondGraphReplayButton.setIcon(self.replayIcon)
        self.secondGraphReplayButton.iconSize = QtCore.QSize(50, 50)

        graph2_controls = QtWidgets.QHBoxLayout()
        graph2_controls.addWidget(self.secondGraphPlayButton)
        graph2_controls.addWidget(self.secondGraphReplayButton)
        graph2_layout.addLayout(graph2_controls)


        spectrogram_layout.addWidget(graph2_container)

        self.graph1_container = graph1_container
        self.graph2_container = graph2_container

        self.graph1_container.setMinimumHeight(200)
        self.graph2_container.setMinimumHeight(200)

        self.graph1_container.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )
        self.graph2_container.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )
        
        # Add spectrogram layout to main layout
        layout.addLayout(spectrogram_layout)

        # Results label and table
        results_layout = QtWidgets.QVBoxLayout()
        self.results_label = QtWidgets.QLabel("Results")
        self.results_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text']};
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        self.results_label.setAlignment(QtCore.Qt.AlignCenter)

        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setRowCount(10) # 17 song * 3   ( song , music , vocals )
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Matches", "Similarity %"])
        self.results_table.verticalHeader().setVisible(True)
        self.results_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.results_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.results_table.setFixedHeight(500)
        self.results_table.setStyleSheet( self.table_style)
        self.results_table.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )
        self.results_table.setMinimumHeight(200)  # Set minimum instead of fixed height
        

        results_layout.addWidget(self.results_label)
        results_layout.addWidget(self.results_table)

        layout.addLayout(results_layout)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)

        # Set window minimum size
        self.setMinimumSize(1200, 800)

        # Connect buttons to functions
        #self.load_1st_song_btn.clicked.connect(self.load_first_song)
        #self.load_2nd_song_btn.clicked.connect(self.load_second_song)
        #self.remove_1st_song_btn.clicked.connect(self.remove_first_song)
        #self.remove_2nd_song_btn.clicked.connect(self.remove_second_song)
        # Connect slider movement to the update function
        self.slider.valueChanged.connect(self.update_slider_percentages)


        # new styles

        self.mix_button.setStyleSheet(self.mix_button_style)
        self.slider.setStyleSheet(self.slider_style)
        self.firstAudioGraph.setStyleSheet(self.graph_style)
        self.secondAudioGraph.setStyleSheet(self.graph_style)
        self.results_table.setStyleSheet(self.table_style)
        
        for btn in [self.load_1st_song_btn, self.load_2nd_song_btn, self.remove_1st_song_btn, self.remove_2nd_song_btn]:
            btn.setStyleSheet(self.button_style)


    def create_song_button(self, text):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(50)
        return btn

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
