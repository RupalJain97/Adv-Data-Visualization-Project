import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QTabWidget, QSpacerItem, QSizePolicy, QSlider, QStackedWidget, QFrame, QLayout
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont, QColor, QFontMetrics
from matplotlib.widgets import SliderBase

from fnirs_slider import MainWindow
from NIRS_topo_slider import TopoMainWindow

from screenshot_eye_track_slider import Window

from EEG_slider import MainWindow as WindowEEG
from EEG_topo_slider import TopoMainWindow as TopoMainWindowEEG


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Get the screen resolution
        screen_resolution = QApplication.desktop().screenGeometry()

        # Calculate the desired position and size based on screen resolution
        x = int(screen_resolution.width() * 1)
        y = int(screen_resolution.height() * 1)
        width = int(screen_resolution.width() * 1)
        height = int(screen_resolution.height() * 1)

        # Create the layout managers
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # create the first row layout which includes eye-tracking and signal view
        sub_layout1 = QHBoxLayout()
        sub_layout1.setSpacing(0)
        sub_layout1.setContentsMargins(0, 0, 0, 0)
        
        # Create the second row layout
        sub_layout2 = QHBoxLayout()
        sub_layout2.setSpacing(0)
        sub_layout2.setContentsMargins(0, 0, 0, 0)

        # Create the widgets
        eye_tracking_widget = QWidget()
        fNIRS_widget = QWidget()
        EEG_widget = QWidget()
        slider_widget = QWidget()

        # Set fixed size for the widgets
        eye_tracking_widget.setFixedSize(int(width * 0.4), int(height * 0.9))
        fNIRS_widget.setFixedSize(int(width * 0.3), int(height * 0.9))
        EEG_widget.setFixedSize(int(width * 0.3), int(height * 0.9))
        slider_widget.setFixedSize(int(width * 1), int(height * 0.1))

        # Set margin and padding to 0 for each widget
        eye_tracking_widget.setContentsMargins(0, 0, 0, 0)
        fNIRS_widget.setContentsMargins(0, 0, 0, 0)
        EEG_widget.setContentsMargins(0, 0, 0, 0)
        slider_widget.setContentsMargins(100, 0, 0, 0)

        # Add widgets to the sub_layout1
        sub_layout1.addWidget(eye_tracking_widget)
        sub_layout1.addWidget(fNIRS_widget)
        sub_layout1.addWidget(EEG_widget)

        sub_layout2.addWidget(slider_widget)

        # Set the size policy for the widgets to Fixed
        eye_tracking_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        fNIRS_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        EEG_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        slider_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Set the position and size of the widget
        self.setGeometry(x, y, width, height)

        window = Window()
        signal_fNIRS = MainWindow()
        signal_EEG = WindowEEG()
        topo_fNIRS = TopoMainWindow()
        topo_EEG = TopoMainWindowEEG()

        eye_tracking_layout = QVBoxLayout(eye_tracking_widget)
        fNIRS_layout = QVBoxLayout(fNIRS_widget)
        EEG_layout = QVBoxLayout(EEG_widget)
        slider_box_layout = QVBoxLayout(slider_widget)
        
        eye_tracking_layout.setSpacing(0)
        eye_tracking_layout.setContentsMargins(0, 0, 0, 0)
        fNIRS_layout.setSpacing(0)
        fNIRS_layout.setContentsMargins(0, 0, 0, 0)
        EEG_layout.setSpacing(0)
        EEG_layout.setContentsMargins(0, 0, 0, 0)
        slider_box_layout.setSpacing(0)
        slider_box_layout.setContentsMargins(0, 0, 0, 0)

        # Set font properties
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        font.setBold(True)
        alignment = Qt.AlignCenter

        # Label over each fNIRS and EEG widget
        view_Label_fNIRS = QLabel("fNIRS")
        view_Label_EEG = QLabel("EEG")
        view_Label_fNIRS.setFont(font)
        view_Label_fNIRS.setAlignment(alignment)
        view_Label_EEG.setFont(font)
        view_Label_EEG.setAlignment(alignment)
        view_Label_fNIRS.setContentsMargins(0, 10, 0, 0)
        view_Label_EEG.setContentsMargins(0, 10, 0, 0)

        # Slider in sub_layout2
        slider = QSlider(Qt.Horizontal, self)
        slider.setTickInterval(1)
        slider.setMinimum(0)
        slider.setMaximum(50)
        slider.setGeometry(50, 1200, 100, 50)
        slider.setRange(0, 3000)
        slider.valueChanged.connect(window.changedValue)
        slider.valueChanged.connect(signal_fNIRS.update_plot_data)
        slider.valueChanged.connect(topo_fNIRS.slider_moved)
        slider.valueChanged.connect(signal_EEG.update_plot_data)
        slider.valueChanged.connect(topo_EEG.slider_moved)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setStyleSheet("border: 1px solid black;")
        slider.setFixedSize(int(width * 0.9), 50)
        slider.setFont(font)
        # slider.setAlignment(alignment)

        # Add a border style to each label and Set custom dimensions
        view_Label_fNIRS.setStyleSheet("border: 1px solid black;")
        view_Label_EEG.setStyleSheet("border: 1px solid black;")
        view_Label_fNIRS.setStyleSheet(
            "background-color: rgba(102, 102, 255, 100); padding: 2px;")
        view_Label_EEG.setStyleSheet(
            "background-color: rgba(102, 102, 255, 100); padding: 2px;")
        view_Label_fNIRS.setFixedSize(int(width * 0.2), 35)
        view_Label_EEG.setFixedSize(int(width * 0.2), 35)

        # Adding into the main layout to make row 1 and row 2
        main_layout.addLayout(sub_layout1)
        main_layout.addLayout(sub_layout2)

        # Create the stacked widget for the views in Box 2
        stacked_widget_fNIRS = QStackedWidget()
        stacked_widget_fNIRS.addWidget(signal_fNIRS)
        stacked_widget_fNIRS.addWidget(topo_fNIRS)

        # Create the stacked widget for the views in Box 2
        stacked_widget_EEG = QStackedWidget()
        stacked_widget_EEG.addWidget(signal_EEG)
        stacked_widget_EEG.addWidget(topo_EEG)

        def switchButton_fNIRS():
            button1_property = button_fNIRS.property("value")
            if button1_property == "signal":
                button_fNIRS.setProperty("value", "topological")
                stacked_widget_fNIRS.setCurrentIndex(1)
            elif button1_property == "topological":
                button_fNIRS.setProperty("value", "signal")
                stacked_widget_fNIRS.setCurrentIndex(0)

        def switchButton_EEG():
            button2_property = button_EEG.property("value")
            if button2_property == "signal":
                button_EEG.setProperty("value", "topological")
                stacked_widget_EEG.setCurrentIndex(1)
            elif button2_property == "topological":
                button_EEG.setProperty("value", "signal")
                stacked_widget_EEG.setCurrentIndex(0)

        # Create a button
        width_button = int(screen_resolution.width() * 0.2)
        button_fNIRS = QPushButton('Change View', self)
        button_fNIRS.setProperty("value", "signal")
        button_fNIRS.setFont(font)
        button_fNIRS.setFixedSize(width_button, 35)
        color = QColor(102, 102, 255, 100)  # Purple color
        button_fNIRS.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(color.red(), color.green(), color.blue(), color.alpha()))
        # button_fNIRS.setStyleSheet("font-weight: bold; text-align: center;")
        button_fNIRS.clicked.connect(switchButton_fNIRS)

        # Create a button
        button_EEG = QPushButton('Change View', self)
        button_EEG.setProperty("value", "signal")
        button_EEG.setFont(font)
        button_EEG.setFixedSize(width_button, 35)
        color = QColor(102, 102, 255, 100)  # Purple color
        button_EEG.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(color.red(), color.green(), color.blue(), color.alpha()))
        # button_EEG.setStyleSheet("font-weight: bold; text-align: center;")
        button_EEG.clicked.connect(switchButton_EEG)

        # Add the labels to the respective layouts
        eye_tracking_layout.addWidget(window)
        fNIRS_layout.addWidget(view_Label_fNIRS, alignment=Qt.AlignCenter)
        fNIRS_layout.addWidget(stacked_widget_fNIRS, alignment=Qt.AlignCenter)
        fNIRS_layout.addWidget(button_fNIRS, alignment=Qt.AlignCenter)

        EEG_layout.addWidget(view_Label_EEG, alignment=Qt.AlignCenter)
        EEG_layout.addWidget(stacked_widget_EEG, alignment=Qt.AlignCenter)
        EEG_layout.addWidget(button_EEG, alignment=Qt.AlignCenter)

        slider_box_layout.addWidget(slider)

        self.setLayout(main_layout)

        self.show()  # Show the widget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show
    sys.exit(app.exec_())
