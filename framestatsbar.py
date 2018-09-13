from PyQt5 import QtWidgets

class FrameStatisticsBar(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(FrameStatisticsBar, self).__init__(parent)

        hbl = QtWidgets.QHBoxLayout(self)
        self.label_recvd = QtWidgets.QLabel("Frames recvd:")
        self.frames_recvd = QtWidgets.QLabel("0")
        self.frames_recvd.setFixedWidth(30)
        self.label_shown = QtWidgets.QLabel("Frames shown:")
        self.frames_shown = QtWidgets.QLabel("0")

        self.reset_button = QtWidgets.QPushButton("Reset")

        hbl.addWidget(self.label_recvd)
        hbl.addWidget(self.frames_recvd)
        hbl.addWidget(self.label_shown)
        hbl.addWidget(self.frames_shown)
        hbl.addStretch()
        hbl.addWidget(self.reset_button)

    def update(self, frames_recvd, frames_shown):

        self.frames_recvd.setText(str(frames_recvd))
        self.frames_recvd.repaint()
        self.frames_shown.setText(str(frames_shown))
        self.frames_shown.repaint()
        
    def connect_reset(self, slot):
        self.reset_button.clicked.connect(slot)