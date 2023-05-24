from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
import pandas as pd
import os
import mne
import pyxdf
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):

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

        # data = pd.read_csv(data_path,sep = '\t')
        # # Get the index of channel that are being used.
        # self.channel_indices = [data.columns.get_loc(channel) for channel in self.channels_used]

        self.data1 = pd.DataFrame(filtered_raw.get_data().T, columns=filtered_EEG_channels)

        # initialize plots
        super(MainWindow, self).__init__()

        # Create main layout
        self.mainLayout = QVBoxLayout()

        # Create and configure the plots layout
        self.graphWidgetLayout = pg.GraphicsLayoutWidget()
        self.graphWidgetLayout.resize(1000, 2500)

        # Create and configure the slider layout
        # self.sliderLayout = QHBoxLayout()
        # self.slider = QSlider(Qt.Horizontal, self)
        # self.slider.setTickInterval(1)
        # self.slider.setMinimum(0)
        # self.slider.setMaximum(1000)
        # self.slider.valueChanged.connect(self.update_plot_data)
        # self.slider.setTickPosition(QSlider.TicksBelow)
        # self.sliderLayout.addWidget(self.slider)

        # Add the plots and slider layouts to the main layout
        self.mainLayout.addWidget(self.graphWidgetLayout)
        # self.mainLayout.addLayout(self.sliderLayout)

        # Set the main layout as the central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        # Enable antialiasing for prettier plots

        pg.setConfigOptions(antialias=True)

        self.graphWidgetLayout.setBackground("w")

        self.pen = pg.mkPen(color=(0,0,0), width=2)  # black

        self.ch = []
        # self.ch1 = []

        label_style = {"color": (255, 0, 0), "font-size": "10pt"}

        # self.srate = 10  # 10.2Hz for NIRS data
        # self.timer = QtCore.QTimer()
        # # why? https://stackoverflow.com/questions/59094207/how-to-set-pyqt5-qtimer-to-update-in-specified-interval
        # self.timer.setInterval(round(1000 / self.srate))

        n_channels = len(filtered_EEG_channels)

        self.x = [0]
        self.y = [[0] for _ in range(n_channels)]  # HbO
        # self.y1 = [[0] for _ in range(n_channels)]  # HbR

        self.dataLine = [[] for _ in range(n_channels)]
        # self.dataLine1 = [[] for _ in range(n_channels)]

        for self.idx, ch_name in enumerate(filtered_EEG_channels):
            # create subplots

            self.channel = self.graphWidgetLayout.addPlot(row=self.idx, col=0)
            # self.channel.showAxes('left', showValues=False)

            if self.idx < n_channels - 1:
                self.channel.hideAxis("bottom")

            self.channel.setLabel("left", ch_name, **label_style)

            self.ch.append(self.channel)
            # self.ch1.append(self.channel)

        self.plots()

    def plots(self):
        # draw

        for self.idx, self.ch in enumerate(self.ch):
            self.ch = self.ch.plot(x=self.x, y=self.y[self.idx], pen=self.pen)
            # self.ch1 = self.ch1.plot(x=self.x, y=self.y1[self.idx], pen=self.pen1)

            self.dataLine[self.idx].append(self.ch)
            # self.dataLine1[self.idx].append(self.ch1)

        # self.timer.timeout.connect(self.update_plot_data)
        # self.timer.start()

    def update_slider_value(self, value):
        self.slider_value = value
        
    def update_plot_data(self, value):
        self.slider_value = value

        # window_size = 1000
        # start = max(0, int(len(self.data1) * (self.slider_value / 1000) - window_size // 2))
        # end = min(len(self.data1), start + window_size)

        start = 0
        end = min (len (self.data1), value)

        self.x = list(range(start, end))

        for i in range(len(self.channels_used[:21])):
            self.y[i] = self.data1.iloc[start:end, i].tolist()
            # self.y1[i] = self.data2.iloc[start:end, i].tolist()

        for i in range(0, len(self.channels_used[:21])):
            self.dataLine[i][0].setData(self.x, self.y[i])
            # self.dataLine1[i][0].setData(self.x, self.y1[i])

    # def update_plot_data(self, value):
    #     self.slider_value = value
    #     # update data

    #     if len(self.x) >= 100:
    #         self.x = self.x[1:]  # Remove the first x element.

    #         for i in range(len(self.channel_list)):
    #             self.y[i] = self.y[i][1:]  # Remove the first
    #             self.y1[i] = self.y1[i][1:]  # Remove the first

    #     # Get the next chunk of samples from LSL.
    #     # They were accumulated while we were plotting the previous chunk
    #     # sample, time = self.inlet.pull_chunk()

    #     if len(self.data1) > 0:
    #         # Plot the most recent sample of this chunk. Discard the rest

    #         # Update the x value according to the number of samples we skipped
    #         self.x.append(self.x[-1] + len(self.data1.iloc[-1].values))

    #         # Append the last sample
    #         for i in range(len(self.channel_list)):
    #             # print(self.data1[-1][i], self.data2[-1][i])
    #             if self.slider_value == 0:
    #                 print('Im less than 0')
    #                 self.y[i].append(self.data1.iloc[-1][i])
    #                 self.y1[i].append(self.data2.iloc[-1][i])
    #             else:
    #                 print('Im greater than 0')
    #                 start = int(len(self.data1) * (self.slider_value / 1000))
    #                 end = int(len(self.data1) * ((self.slider_value + 1) / 1000))
    #                 self.y[i].append(self.data1.iloc[start:end, i].mean())
    #                 self.y1[i].append(self.data2.iloc[start:end, i].mean())
    #                 print(self.data1.iloc[start:end, i], self.data2.iloc[start:end, i])

    #         for i in range(0, len(self.channel_list)):
    #             self.dataLine[i][0].setData(self.x, self.y[i])
    #             self.dataLine1[i][0].setData(self.x, self.y1[i])

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
