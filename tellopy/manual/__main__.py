from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication
from .keyboard import Keyboard
from .control import ButtonControl
from .device import Device
from .mock_device import Device as MockDevice


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
    buttons = ButtonControl(device, keyboard)
    buttons.show()
    print(buttons.keyboard)
    app.exec_()
