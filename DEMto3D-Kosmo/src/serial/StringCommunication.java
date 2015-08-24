/*
 * Class uses the RXTX Library for Serial Communication
 * to send, receive and encode Strings from an Arduino
 * 
 * done by Laurid Meyer
 * 28.04.2012
 * 
 * http://www.lauridmeyer.com
 */

package org.saig.jump.serial.demto3d;

import gnu.io.CommPortIdentifier;
import gnu.io.SerialPort;
import gnu.io.SerialPortEvent;
import gnu.io.SerialPortEventListener;

import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;

import javax.swing.JTextArea;

public class StringCommunication implements SerialPortEventListener {
	SerialPort serialPort;
	/** The port we're normally going to use. */
	private static String PORT_NAME;

	/** Buffered input stream from the port */
	private InputStream input;
	/** The output stream to the port */
	private OutputStream output;
	/** Milliseconds to block while waiting for port open */
	private static final int TIME_OUT = 2000;
	/** Default bits per second for COM port. */
	private static final int DATA_RATE = 9600;

	private String inputBuffer = "";
	public String mensaje;

	public JTextArea jtext;

	public void setJText(JTextArea JT) {
		jtext = JT;
	}

	@SuppressWarnings("rawtypes")
	public void initialize() {

		CommPortIdentifier portId = null;
		Enumeration portEnum = CommPortIdentifier.getPortIdentifiers();

		// iterate through, looking for the port
		while (portEnum.hasMoreElements()) {
			CommPortIdentifier currPortId = (CommPortIdentifier) portEnum
					.nextElement();
			if (currPortId.getName().equals(PORT_NAME)) {
				portId = currPortId;
				break;
			}
		}
		if (portId == null) {
			System.out.println("Could not find COM port.");
			return;
		} else {
			System.out.println("Found your Port");
		}
		try {
			// open serial port, and use class name for the appName.
			serialPort = (SerialPort) portId.open(this.getClass().getName(),
					TIME_OUT);

			// set port parameters
			serialPort.setSerialPortParams(DATA_RATE, SerialPort.DATABITS_8,
					SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);

			// open the streams
			input = serialPort.getInputStream();
			output = serialPort.getOutputStream();

			// add event listeners
			serialPort.addEventListener(this);
			serialPort.notifyOnDataAvailable(true);

		} catch (Exception e) {
			System.err.println(e.toString());
		}
	}

	/**
	 * This should be called when you stop using the port. This will prevent
	 * port locking on platforms like Linux.
	 */
	public synchronized void close() {
		if (serialPort != null) {
			serialPort.removeEventListener();
			serialPort.close();
		}
	}

	/**
	 * This Method can be called to print a String to the serial connection
	 */
	public synchronized void sendString(String msg) {
		try {
			msg += '\n';// add a newline character
			output.write(msg.getBytes());// write it to the serial
			output.flush();// refresh the serial
			// output for debugging
			//jtext.append("<- " + msg);
		} catch (Exception e) {
			System.err.println(e.toString());
		}
	}

	/**
	 * This Method is called when a command is recieved and needs to be encoded
	 */
	private synchronized void encodeCommand(String com) {
		// checks if the String starts with s for set
		if (com.indexOf("s:") == 0) {
			// remove the s, and store the "p1"
			String id = com.substring(com.indexOf("s:") + 2, com.indexOf(","));
			// store everything after the ","
			String value = com.substring(com.indexOf(",") + 1, com.length());
			// if it's my poti1 and it sends a value
			if (id.equals("p1") && !value.equals("")) {
				String myValue = "s:s1," + value;// set the value to my servo1
				sendString(myValue);// and send it via the serial
			} else {
				System.out.println("not correct values");
			}
		}
	}

	/**
	 * This Method is called when Serialdata is recieved
	 */
	public synchronized void serialEvent(SerialPortEvent oEvent) {
		if (oEvent.getEventType() == SerialPortEvent.DATA_AVAILABLE) {
			try {
				int available = input.available();
				// read all incoming characters
				for (int i = 0; i < available; i++) {
					// store it into an int (because of the input.read method
					int receivedVal = input.read();
					// if the character is not a new line "\n" and not a
					// carriage return
					if (receivedVal != 10 && receivedVal != 13) {
						// store the new character into a buffer
						inputBuffer += (char) receivedVal;
						// if it's a new line character
					} else if (receivedVal == 10) {
						// output for debugging

						jtext.append("-> " + inputBuffer
								+ System.getProperty("line.separator"));

						// call the method to encode the recieved command
						encodeCommand(inputBuffer);

						// clear the buffer
						inputBuffer = "";
					}
				}
			} catch (Exception e) {
				System.err.println(e.toString());
			}
		}
	}

	public void setPortName(String port_name) {
		PORT_NAME = port_name;
	}

}
