#!/usr/bin/env python3


import argparse
from sys import stderr
from motion import Motion
from pressure import Pressure
from light import Light
from time import Time


def read_chunks(file, size=16):
    try:
        chunk = '-'
        while chunk and not file.closed:
            chunk = file.read(size)
            yield chunk
    finally:
        if not file.closed:
            file.close()


def csv_transcode(infile, outfile):

    sensors = {
        0x61: Motion(),  # TODO: Two kinds of tags here...
        0x62: Pressure(),
        0x6c: Light()
    }

    data = b''
    for chunk in read_chunks(infile, 1024):
        data += chunk
        dex = 0
        while dex < len(data) - 16:

            if data[dex] in sensors:
                tag = data[dex]
                dex += 1
                sensors[tag].append(data, dex)
                dex += sensors[tag].length
            elif tag == 0x75:
                time = Time.read(data, dex)
                for sensor in sensors.values():
                    sensor.time_sync(time)
                dex += Time.length
            elif tag == 0x58:
                if data[dex:dex + 9] == b'\0\0\0\0\0\0\0\0q':
                    infile.close()  # FIXME Uhh
            elif tag == 0x4C:
                end = data.find(b'\n', dex)
                if end > 0:
                    # result += chr(tag) + data[dex:end + 1].decode()
                    dex = end + 1
                else:
                    dex -= 1
                    break
            else:
                print('Skipping bad tag: <' + hex(data[dex]) + '>', file=stderr)
                dex += 1
        data = data[dex:]

    pass  # Assemble data


def main():
    parser = argparse.ArgumentParser(description='Decode BDL binary file')
    parser.add_argument('file', type=argparse.FileType('rb'))
    parser.add_argument('output', type=argparse.FileType('w'))

    args = parser.parse_args()

    try:
        csv_transcode(args.file, args.output)
    finally:
        if not args.file.closed:
            args.file.close()
        if not args.output.closed:
            args.output.close()


if __name__ == '__main__':
    main()
