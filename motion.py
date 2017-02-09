from datarecord import DataRecord


class Motion(DataRecord):
    pattern = '<hhhhhh'
    length = 12 + 1
    tag = '-'

    @classmethod
    def decode(cls, record):
        nums = Motion.read(record)
        return 'A,' + ','.join(map(str, nums[:3])) + '\n' + \
               'G,' + ','.join(map(str, nums[3:])) + '\n'


class Accelerometer(DataRecord):
    pattern = '<hhh'
    length = 6 + 1
    tag = 'A'


class Gyroscope(DataRecord):
    pattern = '<hhh'
    length = 6 + 1
    tag = 'G'


class Compass(DataRecord):
    pattern = '<hhh'
    length = 6 + 1
    tag = 'C'
