#!/usr/bin/env python3


from sys import stderr
from motion import Motion
from pressure import Pressure
from light import Light


def read_chunks(file, size=512):
    try:
        chunk = '-'
        while chunk and not file.closed:
            chunk = file.read(size)
            yield chunk
    finally:
        if not file.closed:
            file.close()


def main(file):

    sensors = {
        Motion.tag: Motion(),
        Pressure.tag: Pressure(),
        Light.tag: Light()
    }

    data = b''
    for chunk in read_chunks(file, 1024):
        data += chunk
        dex = 0
        while dex < len(data) - 16:

            if data[dex] in sensors:
                tag = data[dex]
                dex += 1
                sensors[tag].append(data, dex)
                dex += sensors[tag].length
            elif tag == 0x75:
                dex += 5  # FIXME!!!
            elif tag == 0x58:
                if data[dex:dex + 9] == b'\0\0\0\0\0\0\0\0q':
                    file.close()  # FIXME :(
            elif tag == 0x4C:
                end = data.find(b'\n', dex)
                if end > 0:
                    # result += chr(tag) + data[dex:end + 1].decode()
                    dex = end + 1
                else:
                    dex -= 1
                    break
            else:
                print('Skipping bad tag: <' + hex(data[dex]) + '>')
                dex += 1
