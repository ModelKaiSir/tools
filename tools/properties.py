import logging


class Comment:

    def __init__(self, message):
        self._message = message
        pass

    @property
    def message(self):
        return self._message
        pass

    def __str__(self):
        return f"#{self._message}"

    pass


class Item:

    def __init__(self, key, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        self._value = _value
        pass

    def __str__(self):
        return f"{self._key}={self._value}"

    pass


class Properties:

    def __init__(self, file_path, properties: list):
        self.file_path = file_path
        self.properties = properties
        pass

    def get(self, key):

        for _p in self.properties:
            if isinstance(_p, Item):

                if _p.key == key:
                    return _p
                pass

            pass
        pass

    def items(self):

        for _p in self.properties:

            if _p is not None:
                yield str(_p)

    def add(self, key, value, comment=None):

        if comment is not None:
            self.properties.append(Comment(comment))
        self.properties.append(Item(key, value))
        pass

    def finish(self):

        def end(_str):
            if _str != "":
                if _str[-1] != '\n':
                    return _str + '\n'
                else:
                    return _str
            else:
                return _str
            pass

        with open(self.file_path, mode='w', encoding='utf-8') as file:
            file.writelines([end(str(obj)) for obj in self.properties if obj is not None])

        logger.info("properties change update finish")
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    pass


logger = logging.getLogger(__name__)


def _analysis(_value: str):
    if _value != "":
        _value = _value.strip()
        if _value[0] == '#':
            return Comment(_value[1:])
        elif _value.find("=") > 0:
            _kv = _value.split("=")
            return Item(_kv[0], _kv[1])
    else:
        return None
        pass


def load(properties_path):
    with open(properties_path, mode='r', encoding='utf-8') as file:
        _properties = [_analysis(v) for v in file.readlines()]
        return Properties(properties_path, _properties)
        pass
    pass


def loads(properties_path, data_lines):
    _properties = [_analysis(v) for v in data_lines]
    return Properties(properties_path, _properties)
    pass


if __name__ == '__main__':
    with load("D:/config.properties") as p:
        p.get("TranslateClassList").value = "Test"

    pass
