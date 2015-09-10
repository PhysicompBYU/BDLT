#!/usr/bin/env python3

import time
import serial
import serial.tools.list_ports
import sys
import platform
import glob
import select
import threading
import readchar
from os import path
import os
#readchar should work on windows but doesnt. I hope you are using Unix. 
#but it is not necessary to do the actual serial communication.

#*************************************************************
#   
#   The important example code is in the 'listen()' function,
#   plus the serial port initialization near the beginning.  
#   
#   You may need to pip install pyserial
#   I included the 'readchar' package because it was handy,
#   but it can also be installed via pip.
#   
#   You will need to plug in a BDL to see the serial ports
#   It should be cross platform with the enum_serial_ports()
#   function, but it was developed and tested on linux.  
#   
#*************************************************************

#Function to find all valid serial ports on current system
def enum_serial_ports():
    system_name = platform.system()
    if(system_name == "Windows"): #... Windows
        ports = list(serial.tools.list_ports.comports())
        available_ports = [(item[0],item[1]) for item in ports]
        #available_ports = list(map(lambda item: (item[0],item[1]),ports))
        return available_ports
    elif(system_name == "Darwin"):  #mac
        return glob.glob('/dev/tty.usb*')
    else: #assume linux
        ports = serial.tools.list_ports.grep('/dev/ttyUSB*')
        available_ports = [(item[0],item[0] + ' | ' + item[2][item[2].find('SNR=')+4:]) for item in ports]
        #return glob.glob('/dev/ttyUSB*')

def read_serial(ser):
    out = ''
#Read out a maximum of 100 bytes from device.  
#Double while loops ensure that after reading 
#   all available bytes that it waits .2 seconds
#   and tries again before giving up and outputting
    i = 100
    while ser.inWaiting() > 0 and i > 0:
        while ser.inWaiting() > 0 and i > 0:
            byt = ser.read(1)
            out += byt.decode('ascii')
            i -= 1
        time.sleep(.2)

    if out != '':
        print(out,end='')
        if not out.endswith('\n'):
            print('')

#Wait for data on serial port, timeout of 1 second (10 * .1)
def wait_serial(ser):
    i = 10
    while ser.inWaiting() == 0 and i > 0:
        i = i - 1
        time.sleep(.1)

#Called in a thread to check for exit character while listening on serial port
def input_check(threadLock):
    threadLock.acquire()
    try:
        while True:
            ch = readchar.readchar()
            if (ch == 'q'):
                break
    except:
        threadLock.release()    
        return
    threadLock.release()

#Listen on device serial port in a thread, stop when lock releases, 
#indicating that 'q' was pressed
def listen(writeFile,outFile,threadLock):
    print('Connecting...')
#Save previous timeout and make sure it is 1/10 of a second
    save_timeout = ser.timeout
    ser.timeout = .1

#Flush all previously received data, this avoids garbled data 
#       at the beginning
    ser.flushInput()
    time.sleep(.1)
    ser.flushInput()

    print('Listening: (\'q\' to quit)')

#This thread cannot acquire the lock until the input thread
#releases it.  Once that happens, exit thread, as we're done listening
    while not threadLock.acquire(blocking = False):
        data = ser.readline()
        print(data.decode('ascii'),end='')
        if(writeFile): #This checks if the program should write to file or not
            outFile.write(data.decode('ascii'))
    print('Stopping...')

    ser.timeout = save_timeout  #Restore saved timeout value


def listener():
    print('Write to file: (enter filename or \'n\' to skip)')
    filename = input()
    writeFile = False
    if not (filename == 'n' or filename == 'no'):
        filePath = path.relpath(filename)
        outFile = open(filePath,'w',-1)
        writeFile = True

#Setup threads to listen on port and check user for input; 
# if 'q' is pressed, stop listening. Threads are only necessary
# to allow quitting during listen

#The lock is acquired by input_check thread and released when 
#'q' is detected.  The listen thread attempts to acquire the lock
#to check if it should continue listening
    threadLock = threading.Lock()
    threads = []

    inputThread = threading.Thread(target=input_check,args = (threadLock,))
    listenThread = threading.Thread(target=listen,args = (writeFile,outFile,threadLock,))

    threads.append(inputThread)
    threads.append(listenThread)

    inputThread.start()
    listenThread.start()

    for th in threads:
        th.join()

    if(writeFile):  #Close the file if we were writing to one
        outFile.close()


# configure the serial connections, enumerating valid and available serial ports for
#the current operating system
print('Select serial port:')
options = enum_serial_ports()
for n in range(len(options)):
    print(str(n+1) + ': ' + str(options[n][1]))
print('x' + ': None of the above, exit')

n = input('>> ') #Get user input to select serial port

if(n == 'x'):
    exit()  #If none option selected, exit
else:
    try:
        port = options[int(n)-1][0]
    except:
        print('# That was not a valid selection #')
        exit()

#TODO add input validation on serial port selection

ser = serial.Serial(
    port=port,
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)

#This only to make sure the port is open, the above declaration should open it
if not ser.isOpen():
	ser.open()

print('Enter your commands below.')
helpstr = """Commands:
help\t (h): This
config\t(cf): Enters Config mode, nothing happens before this
commit\t (c): Commit changes to device, resetting it
listen\t(ls): Print out data from device
empty\t (e): If serial buffers are full, run this to empty
exit\t (x): exits
Anything else will be sent straight to the device
"""
print(helpstr)

#time (in seconds) before serial read timeout
ser.timeout = 1

while 1 :
    inp = input(">> ")

    if inp == 'exit' or inp == 'x':
        ser.close()
        exit()
    elif inp == 'help' or inp == 'h':
        print(helpstr)
        continue #skip unnecesary serial read
#Sends the command to enter config mode
    elif inp == 'config' or inp == 'cf':
        ser.write('config\r'.encode())
        wait_serial(ser)
#Ends config mode on device, resetting it
    elif inp == 'commit' or inp == 'c':
        ser.write('commit\r'.encode())
        wait_serial(ser)
#This command simply outputs enything received over serial to the terminal
    elif 'listen' in inp or inp == 'ls':
        listener()
        continue # I dont know if I should have this; it just skips
                # an additional read of the port
        
#This command empties the serial buffer from the device, but doesnt display it
#Sometimes the client gets behind what the device is sending, use this to clear
    elif inp == 'empty' or inp == 'e':
        while ser.inWaiting() > 0:
            while ser.inWaiting() > 0:
                byt = ser.read(1) #read 1 byte
            time.sleep(.2)

#Send command straight to device.  Will later be deprecated, 
#as all will be handled by client
    else:
        inp += '\r'
        ser.write(inp.encode('ascii'))
        wait_serial(ser)

#This reading from the device occurs for every command
#which is why it is on the level of the while(1)
    read_serial(ser)

