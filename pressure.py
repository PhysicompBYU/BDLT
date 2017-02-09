

from datarecord import DataRecord


class Pressure(DataRecord):
    pattern = '>hBbB'

    @classmethod
    def decode(cls, record):
        nums = super(Pressure, cls).decode(record)  # I think that's right
        return nums[0] + nums[1] / 256, nums[2] + nums[3] / 256
