import serial
from serial.tools import list_ports, miniterm
from bdlbin import BDLBin
from sys import stderr

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
                    self.port = serial.Serial(port=ports[0].device)
                except serial.SerialException as se:
                    print('Error connecting to ', ports[0], file=stderr)
                    raise se
                finally:
                    self.port.close()
            elif len(ports) > 1:
                print('Too many ports returned in search. Please specify a ' +
                      'valid port.', file=stderr)
                raise Exception('Could not find a single valid port')
            else:
                print('No valid ports found. Please specify a port or try ' +
                      'again.', file=stderr)
                raise Exception('No ports found')

        self.file = file
        self.miniterm = miniterm.Miniterm(self.port, filters=[])
        BDLBin.register()
        self.miniterm.set_rx_encoding('bdl')
        self.miniterm.set_tx_encoding('UTF-8')
        self.miniterm.exit_character = 'q'

    @staticmethod
    def enum_serial_ports():
        """
        Creates and returns a list of valid serial ports.

        :return: A list of serial ports to connect to.
        """
        import pdb; pdb.set_trace()
        ports = list(list_ports.grep("BDL"))
        if len(ports) > 0:
            return ports
        ports = list(list_ports.grep("BD"))
        if len(ports) > 0:
            return ports
        ports = list_ports.comports()
        if len(ports) > 0:
            return ports
        else:
            return []

    def run(self):

        self.port.open()
        print('Start')
        self.miniterm.start()
        try:
            self.miniterm.join()
        except KeyboardInterrupt:
            pass
        print('Bye')
        self.miniterm.join()
        self.miniterm.close()


if __name__ == '__main__':
    BDLT().run()
