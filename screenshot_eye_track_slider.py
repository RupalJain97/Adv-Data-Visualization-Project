import matplotlib.pyplot as plt
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QLabel
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from utils import read_screenshots, read_pupil_data
import time
import cv2
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "ToMCAT offline viz"
        self.top = 200
        self.left = 500
        self.width = 1400
        self.height = 1300
        self.InitWindow()

    def InitWindow(self):
        hbox = QHBoxLayout()
        min, max, self.screenshots = read_screenshots()

        self.x, self.y, point_scale, id_labels = read_pupil_data()

        self.slider_text = QLabel(self)
        self.slider_text.setGeometry(100, 830, 900, 20)

        self.ScreenShot = QLabel(self)
        # self.ScreenShot.setPixmap(QPixmap(self.screenshots[0]))
        self.ScreenShot.setGeometry(60, 60, 1280, 720)
        
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setTickInterval(1)

        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        self.slider.setGeometry(100, 830, 1000, 20)
        self.slider.sliderMoved[int].connect(self.changedValue)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.setLayout(hbox)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def changedValue(self, value):
        # change value of the slider when you move the slider and switch to the next img
        start = time.process_time()

        rgb_image = cv2.cvtColor(self.screenshots[value], cv2.COLOR_BGR2RGB)
        # print(self.x[value], self.y[value])
        cv2.circle(rgb_image, (int(self.x[value]), int(self.y[value])), 5, (255, 0, 0), 2)

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.ScreenShot.setPixmap(QPixmap.fromImage(convert_to_Qt_format))

        val = self.slider.value()
        self.slider_text.setText(str(val))
        # print('Time taken by changedValue:', time.process_time() - start)
            

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec_())
