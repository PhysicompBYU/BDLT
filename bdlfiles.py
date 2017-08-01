#!/usr/bin/env python3
import os.path


class BadFileRootException(Exception):
    def __init__(self, message):
        self.message = 'Bad file root exception in BDLFileManager\n\r\t' + message


class BDLFileManager(object):
    DATAPATH = 'BDL_DATA'
    FILENAME = 'DATA_{0:03d}.TXT'
    EMPTY_HEADER = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    FILE_SIZE = 2 ** 28

    def __init__(self):
        self.sd_root = None
        pass

    def set_sd_card(self, filepath):
        self.sd_root = str(filepath)

    def retrieve_file_status(self):
        if self.sd_root is None:
            raise BadFileRootException
        n = 0
        file_list = []
        while True:
            filename = self.FILENAME.format(n)
            filepath = os.path.join(self.sd_root, self.DATAPATH, filename)
            n = n + 1
            if not os.path.isfile(filepath):
                break
            file = open(filepath, 'rb')
            header = file.read(8)
            file.close()
            if header == self.EMPTY_HEADER:
                file_list.extend([(filename, 'empty')])
            else:
                file_list.extend([(filename, 'full')])
            #print(header)

        return file_list

    def clear_files(self):
        if self.sd_root is None:
            raise BadFileRootException
        n = 0
        while True:
            filename = os.path.join(self.sd_root, self.DATAPATH, self.FILENAME.format(n))
            n = n + 1
            if not os.path.isfile(filename):
                break
            file = open(filename, 'r+b')
            file.write(self.EMPTY_HEADER)
            file.close()

    def initialize_files(self, lock=None, count=20):
        if lock is not None:
            lock.acquire()
        if self.sd_root is None:
            raise BadFileRootException
        if os.path.exists(os.path.join(self.sd_root, self.DATAPATH)):
            self.delete_files()
        os.mkdir(os.path.join(self.sd_root, self.DATAPATH))

        print("Making files")
        n = 0
        while n <= count:

            print("file {0:d} ... ".format(n), end='')
            filename = os.path.join(self.sd_root, self.DATAPATH, self.FILENAME.format(n))
            n = n + 1
            file = open(filename, 'w+')
            file.seek(self.FILE_SIZE - 1)
            file.write('\0')
            file.close()
            print("done")

        if lock is not None:
            lock.release()

    def delete_files(self):
        if self.sd_root is None:
            raise BadFileRootException
        n = 0
        while True:
            filename = os.path.join(self.sd_root, self.DATAPATH, self.FILENAME.format(n))
            n = n + 1
            if not os.path.isfile(filename):
                break
            os.remove(filename)
        os.removedirs(os.path.join(self.sd_root, self.DATAPATH))
