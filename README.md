# BDLT

Repo for example code for interfacing with Berry Data Loggers.  

The master branch is actually going to be developed into a full client for interfacing with Berry networks.  

##### Branches
Example branch contains simple python example code

##### Usage
1. Plug in BDL (USB)
2. Run test.py via command line
3. Select serial port of BDL
4. Follow given help instructions

##### Notes
If the BDL does not appear as a COM port on Windows, you need to make sure that the FTDI drivers are installed and that under USB Serial Converter/Properties/Advanced 'Load VCP' is checked, then unplug/replug BDL.

In Linux, 'q' exits listening mode, while in Windows any key will do the same.  Just be thankful it is all error-free exiting on both platforms.  
