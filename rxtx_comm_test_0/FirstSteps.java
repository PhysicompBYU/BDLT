package rxtx_comm_test_0;

import gnu.io.CommPort;
import gnu.io.CommPortIdentifier;
import gnu.io.SerialPort;

//import javax.comm.*;
//import java.io.FileDescriptor;
import java.io.*;
//import java.io.IOException;
//import java.io.InputStream;
//import java.io.OutputStream;
import java.util.Scanner;

public class FirstSteps
{
	public FirstSteps()
	{
		super();
	}

	void connect ( String portName ) throws Exception
	{
		CommPortIdentifier portIdentifier = CommPortIdentifier.getPortIdentifier(portName);
		if ( portIdentifier.isCurrentlyOwned() )
		{
			System.out.println("Error: Port is currently in use");
		}
		else
		{
			System.out.println("Connect 1/2");
			CommPort commPort = portIdentifier.open(this.getClass().getName(),6000);

			if ( commPort instanceof SerialPort )
			{
				System.out.println("Connect 2/2");
				SerialPort serialPort = (SerialPort) commPort;
				System.out.println("BaudRate: " + serialPort.getBaudRate());
				System.out.println("DataBIts: " + serialPort.getDataBits());
				System.out.println("StopBits: " + serialPort.getStopBits());
				System.out.println("Parity: " + serialPort.getParity());
				System.out.println("FlowControl: " + serialPort.getFlowControlMode());
				serialPort.setSerialPortParams(4800,SerialPort.DATABITS_8,SerialPort.STOPBITS_1,SerialPort.PARITY_ODD);
				serialPort.setFlowControlMode(SerialPort.FLOWCONTROL_RTSCTS_IN);
				System.out.println("BaudRate: " + serialPort.getBaudRate());
				System.out.println("DataBIts: " + serialPort.getDataBits());
				System.out.println("StopBits: " + serialPort.getStopBits());
				System.out.println("Parity: " + serialPort.getParity());
				System.out.println("FlowControl: " + serialPort.getFlowControlMode());
				InputStream in = serialPort.getInputStream();
				//OutputStream out = serialPort.getOutputStream();

				(new Thread(new SerialReader(in))).start();
				//(new Thread(new SerialWriter(out))).start();

			}
			else
			{
				System.out.println("Error: Only serial ports are handled by this example.");
			}
		}     
	}

	/**
	 * This is where most of the code is.
	 * this will do 3 things:
	 * 1. print out the data to the console (terminal)
	 * 2. save the data so that it can later be written out..... or have somthing done to it
	 * 3. immediately write the data to file
	 * i have left in all three way since i dont know what would be the most convenient for you guys
	 */
	public static class SerialReader implements Runnable 
	{
		InputStream in;

		public SerialReader ( InputStream in )
		{
			this.in = in;
		}

		public void run ()
		{
			byte[] buffer = new byte[1024];
			int len = -1;
			try
			{
				int TIME_IN_SECONDS = 60;					// change this variable to change run time length
				long start_time = System.currentTimeMillis();	// store current time to later figure out how much time has elapsed
				String data = "Begin data collection: \n";	// 'data' is where the info is stored
				Scanner console = new Scanner(System.in);
				
				System.out.print("Enter filepath(NEC): ");
				String filepath = console.next();//"C:/Users/zack/Documents/";		// location where the file is to be stored
				System.out.print("\nEnter file name(NEC): ");
				String filename = console.next();
				
				File file = new File(filepath+filename);		// name of file
				File file2 = new File(filepath+"java_data2.csv");	// name of file
				if(!file.exists())
					file.createNewFile();					// check if the file already exists, if not then make it
				if(!file2.exists())
					file2.createNewFile();					// check if the file already exists, if not then make it
				
				FileWriter fw = new FileWriter(file);
				FileWriter fw2 = new FileWriter(file2);
				
				/** 'this.in.read(buffer)' is getting the data and storing the length of the new data in 'len'*/
				while ( ((len = this.in.read(buffer)) > -1 ) && ((System.currentTimeMillis()-start_time) < (TIME_IN_SECONDS * 1000)) )
				{
					/** this is where the data is being printed*/
					System.out.print(new String(buffer,0,len));	
					data += new String(buffer,0,len);		// add the line of data to the string, to write to file all at once later
					fw2.write(new String(buffer,0,len));	// write the line of data directly to file
				}
				System.out.println(" 				FINISHED!!");
				data += "\nEnd data collection.\n";
				fw.write(data);
				fw.close();
				fw2.close();
				System.out.println("Saved to file!");
			}
			catch ( IOException e )
			{
				e.printStackTrace();
			}            
		}
	}

	/** */
	public static class SerialWriter implements Runnable 
	{
		OutputStream out;

		public SerialWriter ( OutputStream out )
		{
			this.out = out;
		}

		public void run ()
		{
			try
			{                

				byte[] array = {0x1B, 0x50, 0x0D, 0x0A};
				while ( true )
				{
					this.out.write(new byte[]{0x1B, 0x50, 0x0D, 0x0A});
					this.out.flush();
					Thread.sleep(1000);  
				}                
			}
			catch ( IOException | InterruptedException e )
			{
				e.printStackTrace();
			}            
		}
	}

	public static void main ( String[] args )
	{
		try
		{
			System.out.println("NEC = NO ERROR CHECKING!!!!");
			System.out.print("Enter COM Port number(NEC): ");
			Scanner console = new Scanner(System.in);
			String com_port = "COM" + console.nextInt();		// get the user's input  
			/*NO ERROR CHECKING IS DONE!!!!*/
			(new FirstSteps()).connect(com_port);
		}
		catch ( Exception e )
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}