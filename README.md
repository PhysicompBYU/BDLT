# BDLT

Interfacing with Berry Data Loggers.  

##### Terminal 
Run bdlt.py in the command line

##### File decode
Run 'python3 bdlbin.py <infile> <outfile>' in the command line
'infile' should be a BDL binary file written to the SD card or collected on a computer.  

##### Notes If the BDL does not appear as a COM port on Windows, you
need to make sure that the FTDI drivers are installed and that under
USB Serial Converter/Properties/Advanced 'Load VCP' is checked, then
unplug/replug BDL.
