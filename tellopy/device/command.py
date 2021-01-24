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
        'flip',
        'ccw',
        'up',
        'cw',
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
            assert command in self.level_2_commands

    def is_init_command(self):
        return self.command == 'command'

    @classmethod
    def from_string(cls, string):
        instance = cls(string)
        instance.validate()
        return instance

    def __repr__(self):
        return f"Command('{self.command}')"


def get_command_handler(command, argc):
    if argc == 0:
        return Command.from_string(command)

    @classmethod
    def fn(cls, *args):
        assert len(args) == argc
        string = command + ' '.join(*map(str, args))
        return cls.from_string(string)

    return fn

for command in Command.level_1_commands:
    setattr(Command, command, get_command_handler(command, argc=0))

for command in Command.level_2_commands:
    setattr(Command, command, get_command_handler(command, argc=1))
