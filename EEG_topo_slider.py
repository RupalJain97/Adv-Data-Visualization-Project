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

        cwd = os.getcwd()
        data_path = os.path.join(cwd, "data/XDF/tiger_eeg_fnirs_pupil.xdf")
        data_xdf, header = pyxdf.load_xdf(data_path)

        # Load the EEG data into a NumPy array
        EEG_data = None
        for stream in data_xdf:
            if stream['info']['type'][0] == 'EEG':
                EEG_data = np.array(stream['time_series']).T
                break

        # List of channels to ignore
        ignore_channels = ['AUX_GSR', 'AUX_EKG']

        # Create a list of channel names
        EEG_channels = []
        for channel_dict in stream['info']['desc'][0]['channels'][0]['channel']:
            EEG_channels.append(channel_dict['label'][0])

        self.channels_used = [
                    "AFF1h",
                    "F7",
                    "FC5",
                    "C3",
                    "T7",
                    "TP9",
                    "Pz",
                    "P3",
                    "P7",
                    "O1",
                    "O2",
                    "P8",
                    "P4",
                    "TP10",
                    "Cz",
                    "C4",
                    "T8",
                    "FC6",
                    "FCz",
                    "F8",
                    "AFF2h",
                    "GSR",
                    "EKG",
                ]

        exclude_channels = [(i, ch) for i, ch in enumerate(EEG_channels) if ch not in self.channels_used]

        exclude_indices = [index for index, _ in exclude_channels]

        filtered_EEG_data = np.delete(EEG_data, exclude_indices, axis=0)

        filtered_EEG_channels = [ch for i, ch in enumerate(EEG_channels) if i not in exclude_indices]
        channel_types = ['eeg' if ch not in ignore_channels else 'misc' for ch in EEG_channels]
        filtered_channel_types = [ch_type for i, ch_type in enumerate(channel_types) if i not in exclude_indices]

        self.info = mne.create_info(ch_names=filtered_EEG_channels, sfreq=stream['info']['nominal_srate'][0], ch_types=filtered_channel_types)
        montage = mne.channels.make_standard_montage('standard_1005')
        self.info.set_montage(montage)
        raw = mne.io.RawArray(filtered_EEG_data, self.info)
        filtered_raw = raw.copy().filter(l_freq=1, h_freq=30, skip_by_annotation='edge', picks=['eeg'])

        data_time_point =  filtered_raw.get_data(picks=['eeg', 'misc'])[:,:]

        self.frequency_bands = {
            'delta': (1, 4),
            'theta': (4, 8),
            'alpha': (8, 14),
            'beta': (14, 31),
            'gamma': (31, 50)
        }


        self.filtered_band_data_dict = {}

        for band_name, (l_freq, h_freq) in self.frequency_bands.items():
            filtered_band_data = filtered_raw.copy().filter(l_freq=l_freq, h_freq=h_freq, skip_by_annotation='edge', picks=['eeg'])
            self.filtered_band_data_dict[band_name] = filtered_band_data     
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
        # Create initial figure and canvas
        self.figure = plt.figure(figsize=(5, 12))
        self.canvas = FigureCanvas(self.figure)
        self.graphWidgetLayout.addWidget(self.canvas)

        # Filter the data for each frequency band and store it in the dictionary
        for band_name, (l_freq, h_freq) in self.frequency_bands.items():
            filtered_band_data = filtered_raw.copy().filter(l_freq=l_freq, h_freq=h_freq, skip_by_annotation='edge', picks=['eeg'])
            self.filtered_band_data_dict[band_name] = filtered_band_data.get_data(picks=['eeg', 'misc'])

        self.plot_topomap(0, 100, self.frequency_bands, self.filtered_band_data_dict, self.info, self.channels_used)

    def plot_topomap(self, start_sample, num_samples, frequency_bands, filtered_band_data_dict, info, channels_used):
        self.canvas.figure.clear()
        self.canvas.figure.subplots_adjust(left=0.1)

        start_idx = start_sample
        end_idx = start_sample + num_samples

        axes = self.figure.subplots(nrows=5, ncols=1, gridspec_kw={'hspace': 0.5, 'wspace': 0.3})

        for (band_name, (l_freq, h_freq)), ax in zip(frequency_bands.items(), axes.flatten()[:5]):
            data_time_window = filtered_band_data_dict[band_name][:, start_idx:end_idx]
            data_avg = np.mean(data_time_window, axis=1)

            img, _ = mne.viz.plot_topomap(data_avg[:21], info, axes=ax, extrapolate='head', sensors=True, outlines='head', names=channels_used[:21], show=False)
            ax.set_title(f'{band_name.capitalize()} ({l_freq}-{h_freq} Hz)')

            # Get the min and max values from the data
            vmin = data_avg[:21].min()
            vmax = data_avg[:21].max()

            # Create a colorbar for the topomap plot
            cbar = self.figure.colorbar(img, ax=ax, boundaries=np.linspace(vmin, vmax, 256), pad=0.15)

            # Set a label for the colorbar
            cbar.set_label('(T/m)²/Hz')

        self.canvas.figure.tight_layout()
        self.canvas.draw()


    def update_topomap(self, value):
        self.slider_value = value

        # Call plot_topomap to update the plot
        window_size = 2500  # For example, 2500 samples

        self.plot_topomap(self.slider_value, window_size, self.frequency_bands, self.filtered_band_data_dict, self.info, self.channels_used)

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
