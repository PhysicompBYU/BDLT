import codecs
import argparse
from struct import unpack_from


class IncrementalDecoder(codecs.IncrementalDecoder):
    # TODO: This should actually be a BufferedIncrementalEncoder
    STATE_RESET = 0
    STATE_ASCII = 1
    STATE_LOG = 2
    STATE_ERR = 3
    STATE_ACCELEROMETER = 4
    STATE_BAROMETER = 5
    STATE_LIGHT = 6
    STATE_TIME = 7
    STATE_END = 8
    STATE_OVER = 9

    TAGS = {
        b'A': STATE_ASCII,  # Accelerometer
        b'B': STATE_ASCII,  # Barometer
        b'G': STATE_ASCII,  # Gyroscope
        b'L': STATE_ASCII,  # Log message
        b'E': STATE_ASCII,  # Error message
        b'T': STATE_ASCII,  # Temperature
        b'V': STATE_ASCII,  # Voltage
        b'a': STATE_ACCELEROMETER,  # Accelerometer
        b'b': STATE_BAROMETER,  # Barometer
        b'l': STATE_LOG,  # Log message
        b'e': STATE_ERR,  # Error message
        b'i': STATE_LIGHT,  # Light intensity
        b'u': STATE_TIME,  # Time stamp
        b'X': STATE_END  # End of file
    }

    BYTE_COUNT_ACCELEROMETER = 12
    BYTE_COUNT_BAROMETER = 6
    BYTE_COUNT_LIGHT = 4
    BYTE_COUNT_TIME_STAMP = 4

    def __init__(self, output='text', errors='strict'):
        super(IncrementalDecoder, self).__init__(errors)
        self.bytes = bytearray()
        self.state = 0
        self.time = 0  # TODO: Kosher??
        self.output_text = True  # if output == 'text' else False
        self.errors = True if errors == 'strict' else False

    def decode(self, obj, final=False):
        self.bytes.extend(obj)
        lines = []

        while len(self.bytes) > 0:
            if self.state == self.STATE_RESET:
                if bytes([self.bytes[0]]) in self.TAGS:
                    self.state = self.TAGS[bytes([self.bytes[0]])]
                else:
                    if self.errors:
                        raise DecodeException(
                            'Bad tag found {}'.format(bytes([self.bytes[0]])))
                del self.bytes[0]  # Skip to next
            elif self.state == self.STATE_ASCII:
                dex = self.bytes.find(b'\n')
                if dex >= 0:
                    line = 'S,' + str(self.bytes[:dex])
                    del self.bytes[:dex + 1 + 1]  # TODO: CRC??
                    # lines.append(line)

                    if 'RED' in line:
                        lines.append('S,' + str(self.time) + ',LED Sync')

                    self.state = 0
                else:
                    break
            elif self.state == self.STATE_ACCELEROMETER:
                if len(self.bytes) > self.BYTE_COUNT_ACCELEROMETER:
                    nums = unpack_from('<hhhhhhx', self.bytes)
                    # TODO: Check CRC
                    if self.output_text:
                        lines.append('A,{},{},{},{}\nG,{},{},{},{}'.format(
                            self.time, *nums[:3], self.time, *nums[3:]))
                    else:
                        lines.append(nums)
                    del self.bytes[:(self.BYTE_COUNT_ACCELEROMETER + 1)]
                    self.state = 0
                    self.time += 10
                else:
                    break
            elif self.state == self.STATE_BAROMETER:
                if len(self.bytes) > self.BYTE_COUNT_BAROMETER:
                    nums = unpack_from('>xhBbBx', self.bytes)
                    # TODO: change to pressure; calculate altitude
                    altitude = nums[0] + nums[1] / 256  # 4 bits, but upper
                    temperature = nums[2] + nums[3] / 256  # 4 bits, but upper
                    # if self.output_text:
                    #     lines.append('B,{},{},{}'.format(self.time, altitude,
                    #                                      temperature))
                    # else:
                    #     lines.append((altitude, temperature))
                    del self.bytes[:(self.BYTE_COUNT_BAROMETER + 1)]
                    self.state = 0
                else:
                    break
            elif self.state == self.STATE_LIGHT:
                if len(self.bytes) > self.BYTE_COUNT_LIGHT:
                    nums = unpack_from('<hh', self.bytes)
                    if self.output_text:
                        lines.append('L,{},{},{}'.format(self.time, *nums))
                    else:
                        lines.append(nums)
                    del self.bytes[:(self.BYTE_COUNT_LIGHT + 1)]
                    self.state = 0
                else:
                    break
            elif self.state == self.STATE_TIME:
                if len(self.bytes) > self.BYTE_COUNT_TIME_STAMP:
                    nums = unpack_from('<Ix', self.bytes)
                    # if self.output_text:
                    #     lines.append('U,{}'.format(nums[0]))
                    # else:
                    #     lines.append(nums[0])
                    self.time = nums[0]
                    del self.bytes[:(self.BYTE_COUNT_TIME_STAMP + 1)]
                    self.state = 0
                else:
                    break
            elif self.state == self.STATE_END:
                if len(self.bytes) > 8:
                    if self.bytes[:9] == b'\x00\x00\x00\x00\x00\x00\x00\x00q':
                        self.state = self.STATE_OVER
                    else:
                        raise DecodeException('Bad end of file tag found')
                else:
                    break
            elif self.state == self.STATE_OVER:
                self.bytes.clear()
                break
            else:
                self.state = self.STATE_RESET

        if final and len(self.bytes) > 0:
            raise DecodeException('Bad final state')

        return '\n'.join([''] + lines) if self.output_text else lines

    def reset(self):
        self.bytes = bytearray()
        self.state = 0

    def getstate(self):
        return tuple(self.bytes, self.state)

    def setstate(self, state):
        self.state = state
        if state == 0:
            self.bytes = bytearray()


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, data, final=False):
        return b''


class StreamWriter(IncrementalEncoder, codecs.StreamWriter):
    pass


class StreamReader(IncrementalDecoder, codecs.StreamReader):
    pass


def getregentry(name):
    if name == 'bdl':
        return codecs.CodecInfo(
            encode=None,
            decode=None,
            incrementalencoder=IncrementalEncoder,
            incrementaldecoder=IncrementalDecoder,
            streamwriter=StreamWriter,
            streamreader=StreamReader,
            name='bdl',
            _is_text_encoding=False
        )
    else:
        return None


def register():
    codecs.register(getregentry)


class DecodeException(Exception):
    pass


def read16(file):
    chunk = '-'
    while chunk:
        chunk = file.read(16)
        yield chunk


def main(infile, outfile):
    decoder = IncrementalDecoder(output='text')
    try:
        for chunks in read16(infile):
            if chunks == bytearray(16):
                break
            outfile.write(decoder.decode(chunks))
        decoder.decode(bytes(), final=True)
    finally:
        infile.close()
        outfile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decode BDL binary file')
    parser.add_argument('file', type=argparse.FileType('rb'))
    parser.add_argument('output', type=argparse.FileType('w'))

    args = parser.parse_args()

    main(args.file, args.output)
