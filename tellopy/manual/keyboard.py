import logging
from terminaltables import AsciiTable
from PyQt5.QtCore import Qt


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
