import serial
from serial.tools import list_ports, miniterm
from bdlbin import BDLBin
from sys import stderr, exit

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

            if len(ports) == 0:
                print('No valid ports found. Please specify a port or try ' +
                      'again.', file=stderr)
                raise Exception('No ports found')
                sys.exit(1)
            if len(ports) > 1:
                print('Too many ports returned in search. Please specify a ' +
                      'valid port.', file=stderr)
                for n, port in enumerate(ports):
                    print(n, port.device, port.description)
                n = -1
                while n not in range(len(ports)):
                    n = int(input('0-{}: '.format(len(ports)-1)))

                print('Using port:', ports[n].device)

                try:
                    self.port = serial.Serial(port=ports[n].device)
                except serial.SerialException as se:
                    print('Error connecting to ', ports[n].device, file=stderr)
                    self.port.close()
                    raise se

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
