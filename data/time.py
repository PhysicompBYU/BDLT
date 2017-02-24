from datarecord import DataRecord


class Time(DataRecord):
    pattern = '<I'
    length = 4 + 1
    tag = 'U'
