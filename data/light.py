from datarecord import DataRecord


class Light(DataRecord):
    pattern = '<hh'
    length = 4 + 1
    tag = 'L'  # I think?
