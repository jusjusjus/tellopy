from ..device import Device as _Device
from ..device.command import Command


class Device(_Device):
    _move_distance = 25
    _rotate_angle = 30
    _flip_direction = 'b'
    commands = Command.level_1_commands + \
        Command.level_2_commands

    def left(self):
        super().left(self._move_distance)

    def right(self):
        super().right(self._move_distance)

    def up(self):
        super().up(self._move_distance)

    def down(self):
        super().down(self._move_distance)

    def forward(self):
        super().forward(self._move_distance)

    def back(self):
        super().back(self._move_distance)

    def cw(self):
        super().cw(self._rotate_angle)

    def ccw(self):
        super().ccw(self._rotate_angle)

    def flip(self):
        super().flip(self._flip_direction)
