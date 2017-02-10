#!/usr/bin/env python3


from motion import Motion
from pressure import Pressure
from light import Light


def read_chunks(file, size=512):
    try:
        chunk = '-'
        while chunk:
            chunk = file.read(size)
            yield chunk
    finally:
        file.close()


def main(file):

    sensors = {
        Motion.tag: Motion(),
        Pressure.tag: Pressure(),
        Light.tag: Light()
    }

    data = b''
    for chunk in read_chunks(file):
        data += chunk
        while len(data) > 16:
            tag = data[0]
            if tag in sensors:
                sensors[tag].append(data[1:])
