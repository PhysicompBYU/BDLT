from datarecord import DataRecord


class Pressure(DataRecord):
    pattern = '>hBbB'
    length = 5 + 1
    tag = 'B'

    @classmethod
    def read(cls, record):
        nums = super(Pressure, cls).read(record)  # I think that's right
        return nums[0] + nums[1] / 256, nums[2] + nums[3] / 256
