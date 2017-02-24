#!/usr/bin/env python3


from data.datarecord import DataRecord, CRCException
from data.light import Light
from data.motion import Motion, Accelerometer, Gyroscope, Compass
from data.pressure import Pressure
from data.time import Time


class Decode:

    def __init__(self):
