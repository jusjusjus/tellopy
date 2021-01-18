from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton


class ButtonControl(QDialog):

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
        for c, command in enumerate(self.device.commands):
            button = QPushButton(command)
            action = getattr(self.device, command)
            button.clicked.connect(action)
            for key in command:
                try:
                    self.keyboard.register(key, action)
                    break
                except AssertionError as err:
                    print(f"Error while adding '{key}' for '{command}': {err}")
                    continue

            button_grid.addWidget(button, c // 4, c % 4)

        return button_grid
