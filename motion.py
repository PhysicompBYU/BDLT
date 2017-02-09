

from datarecord import DataRecord


class Motion(DataRecord):
    pattern = '<hhhhhh'


class Accelerometer(DataRecord):
    pattern = '<hhh'


class Gyroscope(DataRecord):
    pattern = '<hhh'


class Compass(DataRecord):
    pattern = '<hhh'
