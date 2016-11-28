from codecs import IncrementalDecoder


class BDLBin(IncrementalDecoder):

    STATE_RESET = 0
    STATE_ASCII = 1
    STATE_LOG = 2
    STATE_ERR = 3
    STATE_ACCELEROMETER = 4
    STATE_BAROMETER = 5
    STATE_LIGHT = 6

    TAGS = {
        "A": 1,
        "B": 1,
        "G": 1,
        "L": 1,
        "T": 1,
        "E": 1,
        "S": 1,
        "V": 1,
        "a": 4,
        "b": 5,
        "l": 2,
        "e": 3,
        "i": 6,
    }

    def __init__(self, output='text', errors='strict'):
        super(BDLBin, self).__init__(errors)
        self.bytes = bytearray()
        self.state = 0
        self.output = output
        self.errors = errors

    def decode(self, obj, final=False):
        self.bytes.append(obj)
        lines = []

        while len(self.bytes) > 0:
            if self.state == self.STATE_RESET:
                if self.bytes[0] in self.TAGS:
                    self.state = self.TAGS[self.bytes[0]]
                else:
                    if self.errors == 'strict':  # TODO: is this how?
                        raise DecodeException
                    else:
                        del self.bytes[0]  # Skip to next
            elif self.state == self.STATE_ASCII:
                dex = self.bytes.find(b'\n')
                if dex >= 0:
                    self.state = 0
                    line = str(self.bytes[:dex+1])
                    del self.bytes[:dex+1]
                    return line
                else:
                    chunk = str(self.bytes)
                    self.bytes.clear()
                    return chunk
            elif self.state == self.STATE_ACCELEROMETER:


    def reset(self):
        self.bytes = bytearray()
        self.state = 0

    def getstate(self):
        return tuple(self.bytes, self.state)

    def setstate(self, state):
        self.state = state
        if state == 0:
            self.bytes = bytearray()


class DecodeException(Exception):
    pass
