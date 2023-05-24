import matplotlib.pyplot as plt
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QLabel, QVBoxLayout
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
from utils import read_screenshots, read_pupil_data
import time
import cv2
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os


class ImageLoader(QThread):
    loaded = pyqtSignal(int, str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        png_files = [f for f in os.listdir(
            self.folder_path) if f.endswith('.png')]
        png_files.sort()
        for i, f in enumerate(png_files):
            image_path = os.path.join(self.folder_path, f)
            self.loaded.emit(i, image_path)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "ToMCAT offline viz"
        self.top = 10
        self.left = 10
        # self.width = 1100
        # self.height = 800
        self.InitWindow()

    def InitWindow(self):
        # hbox = QHBoxLayout()

        min, max, self.screenshots, self.screenshot_paths = read_screenshots()
        # print(min, max)
        self.x, self.y, point_scale, id_labels = read_pupil_data()

        # Create a vertical layout for the button
        vbox = QVBoxLayout()

        # self.slider = QSlider(Qt.Horizontal, self)
        # self.slider.setTickInterval(1)

        # self.slider.setMinimum(0)
        # self.slider.setMaximum(50)
        # self.slider.setGeometry(200, 2000, 100, 20)
        # self.slider.sliderMoved[int].connect(self.changedValue)
        # self.slider.setTickPosition(QSlider.TicksBelow)

        # Create the list of image paths
        # self.csv_data = []

        # Load the images in the background
        # cwd = os.getcwd()
        # data_path = os.path.join(cwd, "data/Screenshots/Screenshots/")
        # self.image_loader = ImageLoader(data_path)
        # self.image_loader.loaded.connect(self.add_image_path_to_list)
        # self.image_loader.start()

        # self.ScreenShot = QLabel(self)
        # # self.ScreenShot.setPixmap(QPixmap(self.screenshots[0]))
        # self.ScreenShot.setGeometry(100, 100, 640, 720)

        # Set font properties
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        font.setBold(True)
        alignment = Qt.AlignCenter

        self.label_name = QLabel(self)
        # self.label_name.setGeometry(50, 50, 640, 10)
        screen_resolution = QApplication.desktop().screenGeometry()
        width_label = int(screen_resolution.width() * 0.4)
        height_label = int(screen_resolution.height() * 0.9)
        self.label_name.setFixedSize(width_label, 35)
        self.label_name.setFont(font)
        self.label_name.setAlignment(alignment)
        self.label_name.setStyleSheet("background-color: rgba(102, 102, 255, 100); padding: 1px;")
        self.label_name.setText(self.screenshot_paths[0])
        vbox.addWidget(self.label_name)

        self.slider_text = QLabel(self)
        screen_resolution = QApplication.desktop().screenGeometry()
        # self.slider_text.setGeometry(200, 1590, width_slider_text, 50)
        self.slider_text.setFixedSize(width_label, 35)
        self.slider_text.setFont(font)
        self.slider_text.setAlignment(alignment)
        self.slider_text.setStyleSheet("background-color: rgba(102, 102, 255, 100); padding: 2px;")
        self.slider_text.setText("Slider value: {}".format(str(0)))
        vbox.addWidget(self.slider_text)

        self.ScreenShot = QLabel(self)
        self.ScreenShot.setPixmap(QPixmap(QImage(self.screenshots[0].data, self.screenshots[0].shape[1], self.screenshots[0].shape[0], QImage.Format_RGB888)))
        # Calculate the width and height for the adjusted image
        widget_width = self.ScreenShot.width()
        widget_height = self.ScreenShot.height()
        adjusted_width = int(widget_width * 1)
        adjusted_height = int(widget_height * 0.5)
        self.ScreenShot.setGeometry(100, 100, adjusted_width, adjusted_height)

        # Add the screenshot to the vertical layout
        vbox.addWidget(self.ScreenShot)
        # Add the slider to the vertical layout
        # vbox.addWidget(self.slider)
        # Add the vertical layout to the horizontal layout
        # hbox.addLayout(vbox)

        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, width_label, height_label)
        self.setFixedSize(width_label, height_label)

        self.setLayout(vbox)
        # self.setGeometry(self.left, self.top, width_label, height_label)
        # self.setFixedSize(width_label, height_label)

        # self.ScreenShot = QLabel(self)
        # self.ScreenShot.setGeometry(100, 100, 1280, 720)

        self.show()

    def changedValue(self, value):
        self.label_name.setText(self.screenshot_paths[value])

        # change value of the slider when you move the slider and switch to the next img
        start = time.process_time()

        rgb_image = cv2.cvtColor(self.screenshots[value], cv2.COLOR_BGR2RGB)
        # print(self.x[value], self.y[value])
        x_value = self.x.get(value, None)
        y_value = self.y.get(value, None)

        if x_value is not None and y_value is not None:
            cv2.circle(rgb_image, (int(x_value), int(y_value)),
                       15, (0, 255, 0), 5)

        # Calculate the width and height for the adjusted image
        widget_width = self.ScreenShot.width()
        widget_height = self.ScreenShot.height()
        adjusted_width = int(widget_width * 1)
        adjusted_height = int(widget_height * 0.5)

        # Resize the image to the adjusted size
        resized_image = cv2.resize(rgb_image, (adjusted_width, adjusted_height))

        h, w, ch = resized_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            resized_image, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.ScreenShot.setPixmap(QPixmap.fromImage(convert_to_Qt_format))

        self.slider_text.setText("Slider value: {}".format(value))
        # print('Time taken by changedValue:', time.process_time() - start)

    # def add_image_path_to_list(self, index, path):
    #     self.csv_data.append(path)

    #     if index == len(self.csv_data) - 1:
    #         self.load_image(0)

    # def load_image(self, value):
    #     # Load the image and display it in the label
    #     path = self.csv_data[value]
    #     pixmap = QPixmap(path)

    #     # Set the label name
    #     label_name = os.path.basename(path)
    #     self.label_name.setText(label_name)

    #     # Load the pupil data
    #     x, y, _, _ = read_pupil_data()

    #     # Get the pupil data for the current image
    #     pupil_x = x.get(value, None)
    #     pupil_y = y.get(value, None)

    #     if pupil_x is not None and pupil_y is not None:
    #         # Calculate the center and radius of the circle
    #         center = (int(pupil_x), int(pupil_y))
    #         radius = 15

    #         # Draw the circle on the screenshot image
    #         image = cv2.imread(path)
    #         cv2.circle(image, center, radius, (0, 255, 0), 5)

    #         # Calculate the width and height for the adjusted image
    #         widget_width = self.ScreenShot.width()
    #         widget_height = self.ScreenShot.height()
    #         adjusted_width = int(widget_width * 1)
    #         adjusted_height = int(widget_height * 0.5)
            
    #         # Convert the OpenCV image to a QPixmap and display it in the label
    #         rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
    #         # Resize the image to the adjusted size
    #         resized_image = cv2.resize(rgb_image, (adjusted_width, adjusted_height))
            
    #         h, w, ch = resized_image.shape
    #         bytes_per_line = ch * w
    #         convert_to_Qt_format = QtGui.QImage(
    #             resized_image, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    #         self.ScreenShot.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
            
    #         self.slider_text.setText("Slider value: {}".format(value))


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec_())
