from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout 
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Song Fingerprint")
        self.setGeometry(100, 100, 1200, 800)

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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())