from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton


class ButtonControl(QWidget):

    def __init__(self, device, keyboard, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyboard = keyboard
        self.device = device
        button_grid = self.create_button_grid()
        self.setLayout(button_grid)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.keyboard.keyPressEvent(event.key())

    def create_button_grid(self):
        button_grid = QGridLayout()
        self.buttons = []
        for c, command in enumerate(self.device.commands):
            button = QPushButton(command)
            handler = self.get_trigger_handler(command)
            button.clicked.connect(handler)
            button_grid.addWidget(button, c // 4, c % 4)
            self.buttons.append(button)
            for key in command:
                try:
                    self.keyboard.register(key, handler)
                    break
                except AssertionError as err:
                    print(f"Error while adding '{key}' for '{command}': {err}")
                    continue

        return button_grid

    def get_trigger_handler(self, command):
        action = getattr(self.device, command)

        def trigger_action():
            self.disable(True)
            response = action()
            print(command, '->', response)
            self.enable(True)

        return trigger_action

    def disable(self, draw=False):
        for button in self.buttons:
            button.setEnabled(False)

        if draw:
            self.repaint()

    def enable(self, draw=False):
        for button in self.buttons:
            button.setEnabled(True)

        if draw:
            self.repaint()
