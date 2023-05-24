from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import pandas as pd
import pyxdf
import numpy as np
import matplotlib.pyplot as plt
import mne
import os

class TopoMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(TopoMainWindow, self).__init__()
        self.slider_value = 0

        # Replace 'your_xdf_file.xdf' with your XDF file path
        cwd = os.getcwd()
        data_path = os.path.join(cwd, "data/XDF/tiger_eeg_fnirs_pupil.xdf")
        data_xdf, header = pyxdf.load_xdf(data_path)

        self.fnirs_data = None
        for stream in data_xdf:
            if stream['info']['type'][0] == 'NIRS':
                # Extract fNIRS data
                self.fnirs_data = np.array(stream['time_series'][902:,:]).T

                # Extract NIRS frequency
                self.sfreq = int(float(stream['info']['desc'][0]['montage'][0]['sampling_rate'][0]))

                # Dictionary containing source and detector locations
                sources_data = stream['info']['desc'][0]['montage'][0]['optodes'][0]['sources'][0]['source']
                detectors_data = stream['info']['desc'][0]['montage'][0]['optodes'][0]['detectors'][0]['detector']

                # Extract source and detector locations
                sources = {f"S{i+1}": (float(s['location'][0]['x'][0]),
                                    float(s['location'][0]['y'][0]),
                                    float(s['location'][0]['z'][0]))
                        for i, s in enumerate(sources_data)}

                detectors = {f"D{i+1}": (float(d['location'][0]['x'][0]),
                                        float(d['location'][0]['y'][0]),
                                        float(d['location'][0]['z'][0]))
                            for i, d in enumerate(detectors_data)}
                break

        if self.fnirs_data is None:
            raise ValueError('fNIRS data not found in the XDF file.')

        # Create source-detector pairs
        pairs = [
            ('S1', 'D1'),
            ('S1', 'D2'),
            ('S2', 'D1'),
            ('S2', 'D3'),
            ('S3', 'D1'),
            ('S3', 'D3'),
            ('S3', 'D4'),
            ('S4', 'D2'),
            ('S4', 'D4'),
            ('S4', 'D5'),
            ('S5', 'D3'),
            ('S5', 'D4'),
            ('S5', 'D6'),
            ('S6', 'D4'),
            ('S6', 'D6'),
            ('S6', 'D7'),
            ('S7', 'D5'),
            ('S7', 'D7'),
            ('S8', 'D6'),
            ('S8', 'D7'),
        ]

        # Create channel positions
        self.channel_positions = []
        for pair in pairs:
            src, det = pair
            midpoint = (np.array(sources[src]) + np.array(detectors[det])) / 2
            self.channel_positions.append(midpoint)
        self.channel_positions = np.array(self.channel_positions)

        # Create channel positions list
        ch_pos = []
        for s in sources:
            ch_pos.append(sources[s])
        for d in detectors:
            ch_pos.append(detectors[d])

        # Create montage object
        ch_names = [f'S{i+1}' for i in range(len(sources))] + [f'D{i+1}' for i in range(len(detectors))]
        # ch_pos_dict = {ch_names[i]: ch_pos[i] for i in range(len(ch_names))}


        # Define the averaging window (in seconds)
        self.window_size = 5

        self.channel_positions = self.channel_positions[:, :2]

        ch_names = [
                    "S1-D1",
                    "S1-D2",
                    "S2-D1",
                    "S2-D3",
                    "S3-D1",
                    "S3-D3",
                    "S3-D4",
                    "S4-D2",
                    "S4-D4",
                    "S4-D5",
                    "S5-D3",
                    "S5-D4",
                    "S5-D6",
                    "S6-D4",
                    "S6-D6",
                    "S6-D7",
                    "S7-D5",
                    "S7-D7",
                    "S8-D6",
                    "S8-D7",
                ]
        self.actual_ch_names = {
            'F3-F5',
            'F3-F1',
            'Af4-F5',
            'Af7-F5',
            'Af3-F5',
            'Af3-Fp1',
            'Af3-Afz',
            'Fz-f1',
            'Fz-Afz',
            'Fz-F2',
            'Fpz-Fp1',
            'Fpz-Afz',
            'Fpz-Fp2',
            'Af4-Afz', 
            'Af4-Fp2',
            'Af4-F6',
            'F4-F2',
            'F4-F6',
            'Af8-Fp2',
            'Af8-F6',
        }
        # Create main layout
        self.mainLayout = QVBoxLayout()

        # Create and configure the plots layout
        self.graphWidgetLayout = QVBoxLayout()

        # Create and configure the slider layout
        # self.sliderLayout = QHBoxLayout()
        # self.slider = QSlider(Qt.Horizontal, self)
        # self.slider.setTickInterval(1)
        # self.slider.setMinimum(0)
        # self.slider.setMaximum(1000)
        # self.slider.valueChanged.connect(self.slider_moved)
        # self.slider.setTickPosition(QSlider.TicksBelow)
        # self.sliderLayout.addWidget(self.slider)

        # Add the plots and slider layouts to the main layout
        self.mainLayout.addLayout(self.graphWidgetLayout)
        # self.mainLayout.addWidget(self.slider)  # Change this line

        # Set the main layout as the central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        # Create initial figure and canvas
        self.figure = plt.figure(figsize=(5, 12))
        self.canvas = FigureCanvas(self.figure)
        self.graphWidgetLayout.addWidget(self.canvas)

        self.plot_topomap()

    def plot_topomap(self):
        self.canvas.figure.clear()
        self.canvas.figure.subplots_adjust(left=0.1)

        hbo_data = self.fnirs_data[41:61, self.slider_value:self.slider_value+100]
        hbr_data = self.fnirs_data[61:81, self.slider_value:self.slider_value+100]

        n_samples = hbo_data.shape[1]

        window_starts = np.arange(0, n_samples, int(self.window_size * self.sfreq))
        window_ends = window_starts + int(self.window_size * self.sfreq)
        window_starts = window_starts[:len(window_ends)]

        # Calculate the mean HbO and HbR data for each window
        mean_hbo = []
        mean_hbr = []
        for start, end in zip(window_starts, window_ends):
            mean_hbo.append(np.mean(hbo_data[:, start:end], axis=1))
            mean_hbr.append(np.mean(hbr_data[:, start:end], axis=1))
        mean_hbo = np.array(mean_hbo).T
        mean_hbr = np.array(mean_hbr).T

        self.channel_positions = self.channel_positions
        self.mean_hbo_timeavg = np.mean(mean_hbo, axis=1)
        self.mean_hbr_timeavg = np.mean(mean_hbr, axis=1)

        # Create a (2, 1) grid of subplots for HbO and HbR topomaps
        axes = self.canvas.figure.subplots(nrows=2, ncols=1)

        # Plot HbO topomap
        img_hbo, _ = mne.viz.plot_topomap(self.mean_hbo_timeavg, self.channel_positions/1000, cmap='bwr', sensors=True, show=False, outlines='head', extrapolate='local', res=128, image_interp='cubic', names=self.actual_ch_names, sphere=(0, 0, 0, 0.095), axes=axes[0], contours=0)
        axes[0].set_title('HbO')

        # Create a colorbar for the HbO topomap
        cbar_hbo = self.canvas.figure.colorbar(img_hbo, ax=axes[0], boundaries=np.linspace(self.mean_hbo_timeavg.min(), self.mean_hbo_timeavg.max(), 256))
        cbar_hbo.set_label('HbO μM')

        # Plot HbR topomap
        img_hbr, _ = mne.viz.plot_topomap(self.mean_hbr_timeavg, self.channel_positions/1000, cmap='bwr', sensors=True, show=False, outlines='head', extrapolate='local', res=128, image_interp='cubic', names=self.actual_ch_names, sphere=(0, 0, 0, 0.095), axes=axes[1], contours=0)
        axes[1].set_title('HbR')

        # Create a colorbar for the HbR topomap
        cbar_hbr = self.canvas.figure.colorbar(img_hbr, ax=axes[1], boundaries=np.linspace(self.mean_hbr_timeavg.min(), self.mean_hbr_timeavg.max(), 256))
        cbar_hbr.set_label('HbR μM')

        self.canvas.figure.tight_layout()
        self.canvas.draw()


    def update_topomap(self, value):
        self.slider_value = value

        # Call plot_topomap to update the plot
        self.plot_topomap()

        # Redraw the canvas
        self.canvas.draw()

        # # Remove the previous plot
        # for i in reversed(range(self.graphWidgetLayout.count())):
        #     widgetToRemove = self.graphWidgetLayout.itemAt(i).widget()
        #     self.graphWidgetLayout.removeWidget(widgetToRemove)
        #     widgetToRemove.setParent(None)

        # # Update the topomap plot based on the slider_value
        # self.plot_topomap()

    def slider_moved(self, value):
        self.slider_value = value
        self.update_topomap(self.slider_value)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TopoMainWindow()
    w.show()
    sys.exit(app.exec_())
