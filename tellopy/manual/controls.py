from PyQt5.QtWidgets import QVBoxLayout, QWidget, QFrame, QSizePolicy
from .button_control import ButtonControl
from .remote_control import RemoteControl


class QHLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1)
        self.setFixedHeight(20)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)


class Controls(QWidget):
    def __init__(self, device, keyboard):
        super().__init__()

        remote_control = RemoteControl(device)
        buttons = ButtonControl(device, keyboard)

        layout = QVBoxLayout()
        layout.addWidget(remote_control, 2)
        layout.addWidget(QHLine())
        layout.addWidget(buttons, 1)
        self.setLayout(layout)
        self.setMinimumSize(500, 400)
        print(buttons.keyboard)

