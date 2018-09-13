import time
import argparse
import sys
import os

import zmq
import numpy as np

class LiveViewProducerDefaults(object):

    def __init__(self):

        self.endpoint_url = "tcp://127.0.0.1:5558"

        self.num_frames = 1
        self.frame_rate = 1.0

        self.image_x = 256
        self.image_y = 256
        self.val_min = 0
        self.val_max = 4096

class LiveViewProducer(object):

    def __init__(self):

        self.image_x = 256
        self.image_y = 256
        self.val_min = 0
        self.val_max = 4096
 
        self.defaults = LiveViewProducerDefaults()


        self.args = self._parse_arguments()

    def _parse_arguments(self, prog_name=sys.argv[0], args=None):
        
        # Set the terminal width for argument help formatting
        try:
            term_columns = int(os.environ['COLUMNS']) - 2
        except (KeyError, ValueError):
            term_columns = 100

        # Build options for the argument parser
        parser = argparse.ArgumentParser(
            prog=prog_name, description='ODIN live view producer',
            formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(
                prog, max_help_position=40, width=term_columns)
        )

        parser.add_argument('--frames', '-n', type=int, dest='num_frames',
            default=self.defaults.num_frames, 
            help='Number of frames to send')
        parser.add_argument('--rate', '-r', type=float, dest='frame_rate',
            default=self.defaults.frame_rate, 
            help='Rate to transmit frames at (Hz)')
        parser.add_argument('--endpoint', type=str, dest="endpoint_url",
            default=self.defaults.endpoint_url,
            help='ZeroMQ endpoint URL to bind')

        parsed_args = parser.parse_args(args)
        return parsed_args

    def send_image(self, frame_num, image_arr, flags=0, copy=True, track=False):
        """send a numpy array with metadata header"""
        header = {
            'frame': frame_num,
            'dtype': str(image_arr.dtype),
            'shape': image_arr.shape,
        }
        self.socket.send_json(header, flags | zmq.SNDMORE)
        return self.socket.send(image_arr, flags, copy=copy, track=track)

    def run(self):

        print(self.args)

        try:
            context = zmq.Context()
            self.socket = context.socket(zmq.PUSH)
            self.socket.bind(self.args.endpoint_url)
        except zmq.error.ZMQError as e:
            print("Failed to connect ZeroMQ endpoint: {}".format(e))
            return 1

        sleep_time = 1.0 / self.args.frame_rate

        print("Sending {:d} frames at {:.1f} Hz".format(self.args.num_frames, self.args.frame_rate))

        for frame in range(self.args.num_frames):
            image_array = np.random.randint(
                self.val_min, self.val_max+1, (self.image_y, self.image_x), dtype=np.uint16)
            self.send_image(frame, image_array)
            time.sleep(sleep_time)
            
        return 0

def main():

    lvp = LiveViewProducer()
    sys.exit(lvp.run())

if __name__ == '__main__':
    main()