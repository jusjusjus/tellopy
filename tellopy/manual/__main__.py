from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication, QMainWindow
from .keyboard import Keyboard
from .device import Device
from .mock_device import Device as MockDevice
from .controls import Controls


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--mockup', action='store_true')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.mockup:
        device = MockDevice.init()
    else:
        device = Device.init()

    keyboard = Keyboard()

    app = QApplication([])

    main = QMainWindow()
    controls = Controls(device, keyboard)
    main.setCentralWidget(controls)

    main.show()
    app.exec_()
