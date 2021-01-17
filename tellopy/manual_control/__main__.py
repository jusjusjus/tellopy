import logging
from terminaltables import AsciiTable
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton


_inv_key_map = {
    val: key
    for key, val in Qt.__dict__.items()
    if key.startswith('Key')
}


class Keyboard:

    logger = logging.getLogger(name="Keyboard")

    def __init__(self):
        self.registry = {}

    def register(self, key, method):
        key = 'Key_'+key.upper()
        key = Qt.__dict__[key] if isinstance(key, str) else key
        assert key not in self.registry, "key %s already in %s" % (
            key, self.registry.keys())
        self.registry[key] = method

    def keyPressEvent(self, key):
        try:
            self.registry[key]()
        except Exception:
            self.logger.info("Key %s not found [%s]" % (
                key, self.registry.keys()))

    def registry_table(self):
        T = [['Key', 'Function']]
        for key, method in self.registry.items():
            T.append([_inv_key_map.get(key, key)[4:].lower(), method.__name__])
        return AsciiTable(T).table

    def __str__(self):
        s = "\nKeyboard shortcuts:\n"
        s += self.registry_table()
        return s


class ButtonControl(QDialog):

    _move_distance = 1
    _rotate_angle = 30

    def __init__(self, device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyboard = Keyboard()
        self.device = device
        button_grid = self.create_button_grid()
        self.setLayout(button_grid)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.keyboard.keyPressEvent(event.key())

    def move_left(self, *args, **kwargs):
        self.device.move_left(self._move_distance)

    def move_right(self, *args, **kwargs):
        self.device.move_right(self._move_distance)

    def move_forward(self, *args, **kwargs):
        self.device.move_forward(self._move_distance)

    def move_backward(self, *args, **kwargs):
        self.device.move_backward(self._move_distance)

    def move_up(self, *args, **kwargs):
        self.device.move_up(self._move_distance)

    def move_down(self, *args, **kwargs):
        self.device.move_down(self._move_distance)

    def rotate_cw(self, *args, **kwargs):
        self.device.rotate_cw(self._rotate_angle)

    def rotate_ccw(self, *args, **kwargs):
        self.device.rotate_ccw(self._rotate_angle)

    def create_button_grid(self):
        button_grid = QGridLayout()

        T = QPushButton("Takeoff")
        La = QPushButton("Land")

        L = QPushButton("Left")
        R = QPushButton("Right")
        F = QPushButton("Forward")
        B = QPushButton("Backward")

        U = QPushButton("Up")
        D = QPushButton("Down")

        CW = QPushButton("Clockwise")
        CCW = QPushButton("Counter-Clockwise")

        La.clicked.connect(self.device.land)
        self.keyboard.register('r', self.device.land)
        T.clicked.connect(self.device.takeoff)
        self.keyboard.register('t', self.device.takeoff)

        L.clicked.connect(self.move_left)
        self.keyboard.register('u', self.move_right)
        R.clicked.connect(self.move_right)
        self.keyboard.register('i', self.move_left)
        F.clicked.connect(self.move_forward)
        self.keyboard.register('k', self.move_forward)
        B.clicked.connect(self.move_backward)
        self.keyboard.register('j', self.move_backward)

        U.clicked.connect(self.move_up)
        self.keyboard.register('a', self.move_up)
        D.clicked.connect(self.move_down)
        self.keyboard.register('d', self.move_down)

        CW.clicked.connect(self.rotate_cw)
        self.keyboard.register('l', self.rotate_cw)
        CCW.clicked.connect(self.rotate_ccw)
        self.keyboard.register('h', self.rotate_ccw)

        button_grid.addWidget(T, 0, 0)
        button_grid.addWidget(La, 0, 2)

        button_grid.addWidget(L, 1, 0)
        button_grid.addWidget(F, 0, 1)
        button_grid.addWidget(R, 1, 2)
        button_grid.addWidget(B, 1, 1)

        button_grid.addWidget(U, 0, 3)
        button_grid.addWidget(D, 1, 3)

        button_grid.addWidget(CW, 0, 4)
        button_grid.addWidget(CCW, 1, 4)

        return button_grid

    def show(self):
        super().show()


if __name__ == "__main__":

    from ..device import Device

    device = Device.init()

    app = QApplication([])
    buttons = ButtonControl(device)
    buttons.show()
    print(buttons.keyboard)
    app.exec_()
