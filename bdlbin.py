from codecs import IncrementalDecoder, CodecInfo, register as register_codec
from struct import unpack_from


class BDLBin(IncrementalDecoder):

    STATE_RESET = 0
    STATE_ASCII = 1
    STATE_LOG = 2
    STATE_ERR = 3
    STATE_ACCELEROMETER = 4
    STATE_BAROMETER = 5
    STATE_LIGHT = 6

    TAGS = {
        b'A': STATE_ASCII,               # Accelerometer
        b'B': STATE_ASCII,               # Barometer
        b'G': STATE_ASCII,               # Gyroscope
        b'L': STATE_ASCII,               # Log message
        b'E': STATE_ASCII,               # Error message
        b'T': STATE_ASCII,               # Temperature
        b'V': STATE_ASCII,               # Voltage
        b'a': STATE_ACCELEROMETER,       # Accelerometer
        b'b': STATE_BAROMETER,           # Barometer
        b'l': STATE_LOG,                 # Log message
        b'e': STATE_ERR,                 # Error message
        b'i': STATE_LIGHT,               # Light intensity
    }

    BYTE_COUNT_ACCELEROMETER = 12

    def __init__(self, output='text', errors='strict'):
        super(BDLBin, self).__init__(errors)
        self.bytes = bytearray()
        self.state = 0
        self.output_text = True  # if output == 'text' else False
        self.errors = True if errors == 'strict' else False
        print(self.errors)

    def decode(self, obj, final=False):
        self.bytes.extend(obj)
        lines = ['']

        while len(self.bytes) > 0:
            if self.state == self.STATE_RESET:
                if bytes([self.bytes[0]]) in self.TAGS:
                    self.state = self.TAGS[bytes([self.bytes[0]])]
                else:
                    if self.errors:
                        raise DecodeException(
                            'Bad tag found {}'.format(bytes([self.bytes[0]])))
                    else:
                        del self.bytes[0]  # Skip to next
            elif self.state == self.STATE_ASCII:
                dex = self.bytes.find(b'\n')
                if dex >= 0:
                    line = str(self.bytes[:dex])
                    del self.bytes[:dex+1]
                    lines.append(line)
                    self.state = 0
                else:
                    break
            elif self.state == self.STATE_ACCELEROMETER:
                if len(self.bytes) >= self.BYTE_COUNT_ACCELEROMETER:
                    nums = unpack_from('>hhhhhh', self.bytes)
                    if self.output_text:
                        lines.append('A,{},{},{}\nG,{},{},{}'.format(*nums))
                    else:
                        lines.append(nums)
                    del self.bytes[:self.BYTE_COUNT_ACCELEROMETER]
                    self.state = 0
                else:
                    break

        if final and len(self.bytes > 0):
            raise DecodeException('Bad final state')

        return '\n'.join(lines) if self.output_text else lines

    def reset(self):
        self.bytes = bytearray()
        self.state = 0

    def getstate(self):
        return tuple(self.bytes, self.state)

    def setstate(self, state):
        self.state = state
        if state == 0:
            self.bytes = bytearray()

    @staticmethod
    def getregentry(name):
        if name == 'bdl':
            return CodecInfo(
                encode=None,
                decode=None,
                incrementalencoder=None,
                incrementaldecoder=BDLBin,
                name='bdl',
                _is_text_encoding=False
            )
        else:
            return None

    @staticmethod
    def register():
        register_codec(BDLBin.getregentry)


class DecodeException(Exception):
    pass
