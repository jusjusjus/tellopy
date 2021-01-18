from ..device.command import Command


class Device:
    commands = Command.level_1_commands + \
        Command.level_2_commands + \
        Command.level_3_commands

    def __getattr__(self, a):
        def fn():
            print(a)
        return fn

    @classmethod
    def init(cls):
        return cls()
