import serial
from serial.tools import list_ports, miniterm
from codecs import IncrementalDecoder
import platform
import time

__author__ = 'Kristian Sims'


class BDLT:

    def __init__(self, port=None, file=None):
        """
        Opens a serial connection to a BDL. If no port is specified, BDLT will
        try to find a valid port. Failing this, it will raise an exception.

        :param port: Optionally specify a port to connect to.
        :return: A BDLT object with a (hopefully) initialized port.
        """

        # Open port
        if port is not None:
            self.port = serial.Serial(port=port)
        else:
            ports = self.enum_serial_ports()
            if len(ports) == 1:
                try:
                    self.port = serial.Serial(port=ports[0])
                except serial.SerialException as se:
                    print('Error connecting to ', ports[0], file=sys.stderr)
                    raise se
                finally:
                    self.port.close()
            elif len(ports) > 1:
                print('Too many ports returned in search. Please specify a ' +
                      'valid port.', file=sys.stderr)
                raise Exception('Could not find a single valid port')
            else:
                print('No valid ports found. Please specify a port or try ' +
                      'again.', file=sys.stderr)
                raise Exception('No ports found')

        self.file = file
        self.miniterm = miniterm.Miniterm(self.port,
                                          filters=(miniterm.NoTerminal,))
        self.miniterm.rx_decoder =

    @staticmethod
    def enum_serial_ports():
        """
        Creates and returns a list of valid serial ports.

        :return: A list of serial ports to connect to.
        """
        ports = list(list_ports.grep("BDL*"))
        if len(ports) > 0:
            return ports
        ports = list(list_ports.grep("BD*"))
        if len(ports) > 0:
            return ports
        ports = list(list_ports.grep(""))
        if len(ports) > 0:
            return ports
        else:
            return None

    def read_serial(self):
        """
        Reads out a maximum of 100 bytes from the BDL. If more than zero and
        less that 100 bytes are read, read_serial times out after 0.2 seconds.

        :return: A string containing up to 100 bytes of data from the BDL.
        """
        out = ''
        i = 100
        while self.port.inWaiting() > 0 and i > 0:
            while self.port.inWaiting() > 0 and i > 0:
                byte = self.port.read(1)
                out += byte.decode('ascii')
                i -= 1
            time.sleep(.2)
        return out

    def wait_serial(self):
        """
        Wait for data on serial port, timeout of 1 second (10 * .1).
        """
        for i in range(10):
            if self.port.inWaiting() > 0:
                return
            else:
                time.sleep(.1)

    def listen(self):
        print('Connecting...',)


class Decoder(IncrementalDecoder):

    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)

    def decode(self, input, final=False):
