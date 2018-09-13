import sys
import random
import zmq
import signal

from PyQt5 import QtCore, QtWidgets
import numpy as np

from mplplot import MplPlotCanvas, MplNavigationToolbar
from framestatsbar import FrameStatisticsBar

class LiveViewReceiver():

    def __init__(self):

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect("tcp://127.0.0.1:5558")

        self.zmq_flags = 0
        self.zmq_copy = True
        self.zmq_track = False

        self.frames_received = 0

    def receive_frame(self):

        header = {}
        frame_data = None

        flags = self.socket.getsockopt(zmq.EVENTS)
        while flags != 0:

            if flags & zmq.POLLIN:

                #print("[Socket] zmq.POLLIN")
                header = self.socket.recv_json(flags=self.zmq_flags)
                print("[Socket] received header: " + repr(header))
                msg = self.socket.recv(flags=flags, copy=self.zmq_copy, track=self.zmq_track)
                buf = memoryview(msg)
                array = np.frombuffer(buf, dtype=header['dtype'])
                frame_data =  array.reshape(header['shape'])
                #print("[Socket] recevied frame shape: " + repr(frame_data.shape))
                self.frames_received += 1

            elif flags & zmq.POLLOUT:
                #print("[Socket] zmq.POLLOUT")
                pass
            elif flags & zmq.POLLERR:
                #print("[Socket] zmq.POLLERR")
                pass
            else:
                #print("[Socket] FAILURE")
                pass

            flags = self.socket.getsockopt(zmq.EVENTS)
            #print("Flags at end", flags)

        return (header, frame_data)

    def get_socket_fd(self):

        return self.socket.getsockopt(zmq.FD)

    def reset_statistics(self):

        self.frames_received = 0

class LiveViewer(QtWidgets.QMainWindow):
 
    def __init__(self):

        super().__init__()
        
        self.left = 10
        self.top = 10
        self.width = 600
        self.height = 500
        self.title = 'ODIN Data Live View'
        
        self.frames_shown = 0

        self.init_ui()

        self.receiver = LiveViewReceiver()
        self.notifier = QtCore.QSocketNotifier(
            self.receiver.get_socket_fd(), QtCore.QSocketNotifier.Read, self
        )
        self.notifier.activated.connect(self.handle_receive)


    def init_ui(self):

        # Set window title and geometry
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create a main widget
        self.main_widget = QtWidgets.QWidget(self)

        # Create a vertical box layout
        vbl = QtWidgets.QVBoxLayout(self.main_widget)

        # Instantiate a Matplotlib canvas
        self.plot = MplPlotCanvas(self.main_widget)

        # Instantiate the navigation toolbar for the plot
        self.nav_tool_bar = MplNavigationToolbar(self.plot, self.main_widget)

        # Instantiate and configure the frame statistics bar
        self.stats_bar = FrameStatisticsBar(self.main_widget)
        self.stats_bar.connect_reset(self.on_reset_stats)

        # Pack widgets into the vertical box layout
        vbl.addWidget(self.nav_tool_bar)
        vbl.addWidget(self.plot)
        vbl.addWidget(self.stats_bar)
        vbl.setContentsMargins(0, 0, 0, 0)
        vbl.setSpacing(0)

        # Set focus on the main widget
        self.main_widget.setFocus()

        # Set the central widget of the main window to main_widget
        self.setCentralWidget(self.main_widget)
 
        # Show the window
        self.show()

    @QtCore.pyqtSlot()
    def on_reset_stats(self):
        self.reset_statistics()
        self.stats_bar.update(self.receiver.frames_received, self.frames_shown)

    def handle_receive(self):

        self.notifier.setEnabled(False)

        (header, frame_data) = self.receiver.receive_frame()
        if frame_data is not None:
            self.plot.render_frame(frame_data)
            self.frames_shown += 1

        self.stats_bar.update(self.receiver.frames_received, self.frames_shown)
        self.notifier.setEnabled(True)

    def reset_statistics(self):

        self.receiver.reset_statistics()
        self.frames_shown = 0

def main():

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)
    live_viewer = LiveViewer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()