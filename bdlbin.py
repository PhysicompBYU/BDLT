import codecs
import motion
import pressure
import light


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    TAGS = {
        0x41: None,  # A - Accelerometer
        0x42: None,  # B - Barometer
        0x47: None,  # G - Gyroscope
        0x4c: None,  # L - Log message
        0x45: None,  # E - Error message
        0x54: None,  # T - Temperature
        0x56: None,  # V - Voltage
        0x61: motion.Motion,  # a - Accelerometer
        0x62: pressure.Pressure,  # b - Barometer
        # 0x6C: LOG,  # l - Log message
        # 0x65: ERR,  # e - Error message
        0x6c: light.Light,  # l - Light intensity
        0x75: None,  # u - Time stamp
        0x58: None  # X - End of file
    }

    def __init__(self, errors='strict'):
        super(IncrementalDecoder, self).__init__(errors)

    def _buffer_decode(self, data, errors, final):

        dex = 0
        result = ''
        while dex < len(data) - 4:

            if data[dex] in IncrementalDecoder.TAGS:
                tag = data[dex]
                dex += 1

                if tag in {0x61, 0x62, 0x6c}:
                    record = IncrementalDecoder.TAGS[tag]
                    if len(data) - dex >= record.length:
                        result += record.decode(data[dex:dex + record.length])
                        dex += record.length
                    else:
                        dex -= 1
                        break
                elif tag == 0x75:
                    if len(data) - dex >= 5:
                        dex += 5  # FIXME!!!
                    else:
                        dex -= 1
                        break
                elif tag == 0x58:
                    if len(data) - dex >= 9:
                        if data[dex:dex+9] == b'\0\0\0\0\0\0\0\0q':
                            dex = len(data)  # FIXME!!!
                            result += 'S,EOT'
                        else:
                            if self.errors == 'strict':
                                raise DecodeException
                            else:
                                continue
                    else:
                        dex -= 1
                        break
                else:
                    end = data.find(b'\n', dex)
                    if end > 0:
                        result += chr(tag) + data[dex:end+1].decode()
                        dex = end + 1
                    else:
                        dex -= 1
                        break
            else:
                if self.errors == 'strict':
                    raise DecodeException
                elif 'replace' in self.errors:
                    result += '<' + hex(data[dex]) + '>'
                    dex += 1
                else:  # Ignore
                    dex += 1

        return result, dex


def getregentry(name):
    if name == 'bdl':
        return codecs.CodecInfo(
            encode=None,
            decode=None,
            incrementalencoder=None,
            incrementaldecoder=IncrementalDecoder,
            streamwriter=None,
            streamreader=None,
            name='bdl',
            _is_text_encoding=False
        )
    else:
        return None


def register():
    codecs.register(getregentry)


class DecodeException(Exception):
    pass
