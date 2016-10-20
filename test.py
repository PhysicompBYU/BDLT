#!/usr/bin/env python3

import time
import serial
import platform
import glob

# *************************************************************
#   
#   The important example code is in the 'listen()' function,
#   plus the serial port initialization near the beginning.  
#   
#   You may need to pip install pyserial
#
#   You will need to plug in a BDL to see the serial ports
#   It should be cross platform with the enum_serial_ports()
#   function, but it was developed and tested on linux.  
#   
# *************************************************************

# Function to find all valid serial ports on current system
def enum_serial_ports():
    system_name = platform.system()
    if system_name == "Windows":  # ... Windows
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append(i)
                s.close()
            except serial.SerialException:
                pass
        return available
    elif system_name == "Darwin":  # mac
        return glob.glob('/dev/tty.usb*')
    else:  # assume linux
        return glob.glob('/dev/ttyUSB*')


def read_serial(ser):
    out = ''
    # Read out a maximum of 100 bytes from device.
    # Double while loops ensure that after reading
    # all available bytes that it waits .2 seconds
    # and tries again before giving up and outputting
    i = 100
    while ser.inWaiting() > 0 and i > 0:
        while ser.inWaiting() > 0 and i > 0:
            byt = ser.read(1)
            out += byt.decode('ascii')
            i -= 1
        time.sleep(.2)

    if out != '':
        print(out, end='')
        if not out.endswith('\n'):
            print('')


# Wait for data on serial port, timeout of 1 second (10 * .1)
def wait_serial(ser):
    i = 10
    while ser.inWaiting() == 0 and i > 0:
        i -= 1
        time.sleep(.1)


# Listen on device serial port
def listen(writeFile):
    print('Connecting...', end='')
    save_timeout = ser.timeout
    ser.timeout = .1

#Flush all previously received data, this avoids garbled data 
#       at the beginning
    ser.flushInput()
    time.sleep(.1)
    ser.flushInput()

    print('Listening.')
    try:
        while True:
            data = ser.readline()
            print(data.decode('ascii'), end='')
            if writeFile:  # This checks if 'outfile' is declared
                outfile.write(data.decode('ascii'))
    except KeyboardInterrupt:
        print('Stopping...')

    if writeFile:
        outfile.close()
    ser.timeout = save_timeout

#The lock is acquired by input_check thread and released when 
#'q' is detected.  The listen thread attempts to acquire the lock
#to check if it should continue listening
    threadLock = threading.Lock()
    threads = []

    inputThread = threading.Thread(target=input_check,args = (threadLock,))
    listenThread = threading.Thread(target=listen,args = (filename,threadLock,))

    threads.append(inputThread)
    threads.append(listenThread)

    inputThread.start()
    listenThread.start()

    for th in threads:
        th.join()

# Configure the serial connections, enumerating valid and available serial
# ports for the current operating system.
print('Select serial port:')
options = enum_serial_ports()
for n in range(len(options)):

    print(str(n + 1) + ': ' + str(options[n]))
print('x' + ': None of the above, exit')

# Get user input to select serial port
while 1:
    try:
        n = input('>> ')
        if n == 'x':
            exit(0)
        n = int(n) - 1
        if n < 0 or n > len(options):  # Reject invalid numbers
            raise ValueError
        else:
            break
    except ValueError:
        print('Please enter a valid number or "x"')
        continue

# Open the serial port
ser = serial.Serial(
    port=options[n],
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)

# Make sure the port is open, but the above declaration should open it
if not ser.isOpen():
    ser.open()

print('Enter your commands below.')
help_string = """Commands:
help\t (h): This
config\t(cf): Enters Config mode, nothing happens before this
commit\t (c): Commit changes to device, resetting it
listen\t(ls): Print out data from device
empty\t (e): If serial buffers are full, run this to empty
exit\t (x): exits
Anything else will be sent straight to the device
"""
print(help_string)

# time (in seconds) before serial read timeout
ser.timeout = 1

while 1:
    inp = input(">> ")

    if inp == 'exit' or inp == 'x':
        ser.close()
        exit()
    elif inp == 'help' or inp == 'h':
        print(help_string)
        continue  # skip unnecessary serial read
    # Sends the command to enter config mode
    elif inp == 'config' or inp == 'cf':
        ser.write('config\r'.encode())
        wait_serial(ser)
    # Ends config mode on device, resetting it
    elif inp == 'commit' or inp == 'c':
        ser.write('commit\r'.encode())
        wait_serial(ser)
    # This command outputs anything received over serial to the terminal
    elif 'listen' in inp or inp == 'ls':
        print('Write to file: (enter filename or "n" to skip)')
        filename = input()
        writeFile = False
        if not (filename == 'n' or filename == 'no'):
            outfile = open(filename, 'w', -1)
            writeFile = True

        listen(writeFile)

        continue
        # I don't know if I should have this; it just skips an additional read
        # of the port

    # This command empties the serial buffer from the device, but doesnt
    # display it
    # Sometimes the client gets behind what the device is sending, use this
    # to clear
    elif inp == 'empty' or inp == 'e':
        while ser.inWaiting() > 0:
            while ser.inWaiting() > 0:
                byt = ser.read(1)  # read 1 byte
            time.sleep(.2)

            # Send command straight to device.  Will later be deprecated,
            # as all will be handled by client

    else:
        inp += '\r'
        ser.write(inp.encode('ascii'))
        wait_serial(ser)

    # This reading from the device occurs for every command
    # which is why it is on the level of the while(1)
    read_serial(ser)
