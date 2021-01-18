class Command:
    level_1_commands = [
        'emergency',
        'streamoff',
        'streamon',
        'command',
        'takeoff',
        'land',
        'stop',
    ]
    level_2_commands = [
        'forward',
        'right',
        'left',
        'back',
        'down',
        'ccw',
        'up',
        'cw',
    ]
    level_3_commands = [
        'flip',
    ]

    def __init__(self, command: str):
        self.command = command

    def tobytes(self):
        return self.command.encode('utf-8')

    def validate(self):
        try:
            self._validate()
        except AssertionError:
            raise ValueError(f"invalid command '{self.command}'")

    def _validate(self):
        split = self.command.split()
        assert len(split) in [1, 2]
        if len(split) == 1:
            assert split[0] in self.level_1_commands
        elif len(split[0]) == 2:
            command, value = split
            if command in self.level_2_commands:
                assert value.isnumeric()
            elif command in self.level_3_commands:
                assert value == 'b'

    def is_init_command(self):
        return self.command == 'command'

    @classmethod
    def from_string(cls, string):
        instance = cls(string)
        instance.validate()
        return instance

    def __repr__(self):
        return f"Command('{self.command}')"


# add the standard commands
for command in Command.level_1_commands:
    setattr(Command, command, Command.from_string(command))


def level_2_command_fn(command):
    @classmethod
    def fn(cls, value):
        return cls.from_string(f"{command} {value}")

    return fn


for command in Command.level_2_commands:
    setattr(Command, command, level_2_command_fn(command))

for command in Command.level_3_commands:
    setattr(Command, command, level_2_command_fn(command))
