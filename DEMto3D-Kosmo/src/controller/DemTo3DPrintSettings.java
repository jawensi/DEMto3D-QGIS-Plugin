package org.saig.jump.controller.demto3d;

import gnu.io.CommPortIdentifier;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Enumeration;
import java.util.Observable;
import java.util.Observer;

import javax.swing.JOptionPane;

import org.saig.jump.dialog.demto3d.DemTo3DDialog;
import org.saig.jump.dialog.demto3d.PrintDialog;
import org.saig.jump.lang.I18N;
import org.saig.jump.serial.demto3d.StringCommunication;

import com.vividsolutions.jump.workbench.plugin.PlugInManager;

public class DemTo3DPrintSettings implements Observer {

	private DemTo3DDialog dialog;
	public PrintDialog Printdialog;
	public StringCommunication com;

	public String DirPrinter;
	public String DirPrint;
	public String DirFilament;

	public String Printer;
	public String Print;
	public String Filament;

	public double Bed_size_high;
	public double Bed_size_width;

	public String estado;

	public boolean puerto;
	public boolean gcode;

	public DemTo3DPrintSettings(DemTo3DDialog dialog, PrintDialog Printdialog) {
		String HomDir = System.getProperty("user.home");
		this.DirPrinter = HomDir + "\\AppData\\Roaming\\Slic3r\\printer\\";
		this.DirPrint = HomDir + "\\AppData\\Roaming\\Slic3r\\print\\";
		this.DirFilament = HomDir + "\\AppData\\Roaming\\Slic3r\\filament\\";
		this.dialog = dialog;
		this.Printdialog = Printdialog;
		this.com = new StringCommunication();

		puerto = false;
		gcode = false;
	}

	public void addListeners() {
		Printdialog.getPrintingComboBox().addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				if (Printdialog.getPrintingComboBox().getSelectedItem()
						.toString() != I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.print-settings")) {
					String elem = Printdialog.getPrintingComboBox()
							.getSelectedItem().toString();
					Print = elem.concat(".ini");
				} else {
					Print = null;
				}
			}
		});
		Printdialog.getFilamentComboBox().addItemListener(new ItemListener() {
			public void itemStateChanged(ItemEvent e) {
				if (Printdialog.getFilamentComboBox().getSelectedItem()
						.toString() != I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.filament-settings")) {
					String elem = Printdialog.getFilamentComboBox()
							.getSelectedItem().toString();
					Filament = elem.concat(".ini");
				} else {
					Filament = null;
				}
			}
		});

		Printdialog.getbtnConect().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				String port_name = Printdialog.getPortComboBox()
						.getSelectedItem().toString();
				if (puerto == false) {
					if (Printdialog.getPortComboBox().getSelectedItem()
							.toString() != "None") {
						com.setPortName(port_name);
						com.initialize();
						Printdialog.gettextArea().append(
								I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.conect-to-port")+" "+ port_name
										+ System.getProperty("line.separator"));
						puerto = true;
						Printdialog.getbtnConect().setText(
								I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.disconnect"));
						com.setJText(Printdialog.gettextArea());

						com.sendString("M111 S6");
						com.sendString("M80 S6");
						com.sendString("M220 S100");
						com.sendString("M221 S100");
						com.sendString("G28 X0 Y0");

						com.sendString("M104 S200");
						com.sendString("M140 S100");
						Printdialog.gettextArea().append(
								I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.heating-extruder-base")
										+ System.getProperty("line.separator"));
					} else {
						Printdialog.gettextArea().append(
								I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.no-port-available")
										+ System.getProperty("line.separator"));
					}
				} else {
					com.close();
					Printdialog.gettextArea().append(
							I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.disconnected-from")+" "+ port_name
									+ System.getProperty("line.separator"));
					Printdialog.getbtnConect().setText("Conectar puerto:");
					puerto = false;
				}
			}
		});
		Printdialog.getbtnTemperatura().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				if (puerto == true) {

					com.sendString("M105");

				} else if (puerto == false) {
					Printdialog.gettextArea().append(
							I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.printer-disconnected")
									+ System.getProperty("line.separator"));
				}
			}
		});

		Printdialog.getbtnPausar().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {

				gcode =false;
				com.sendString("M1");				
				com.sendString("M104 S0");
				com.sendString("M140 S0");
				com.sendString("M84");
				com.sendString("M18");
				com.sendString("M107");
				com.sendString("M1");
			}
		});
		Printdialog.getbtnCancelar().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				if (puerto == true) {
					com.sendString("G28");
					com.close();
				}
				Printdialog.dispose();
				Print = null;
				Filament = null;
				puerto = false;
			}
		});

		Printdialog.getbtnImprimir().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				if (Print == null || Filament == null) {
					JOptionPane
							.showMessageDialog(
									Printdialog,
									"Seleccione configuración de impresion y filamento",
									"DEMto3D", 1);
				} else if (puerto == false) {
					JOptionPane.showMessageDialog(Printdialog,
							"Conecte la impresora 3D", "DEMto3D", 1);
				} else {
					File f = new File("tempstl.stl");

					GetGcode hilo = new GetGcode(gcode, f.getPath(), DirPrint,
							DirPrinter, DirFilament, Print, Printer, Filament,
							Printdialog, DemTo3DPrintSettings.this);
					Thread GetGcode = new Thread(hilo);
					GetGcode.start();
				}
			}
		});
	}

	/**
	 * Load the PortComboBox with the available serial ports
	 */
	@SuppressWarnings("rawtypes")
	public void updatePorts() {

		Enumeration portEnum = CommPortIdentifier.getPortIdentifiers();
		Printdialog.getPortComboBox().removeAllItems();

		while (portEnum.hasMoreElements()) {
			CommPortIdentifier currPortId = (CommPortIdentifier) portEnum
					.nextElement();
			Printdialog.getPortComboBox().addItem(currPortId.getName());
		}

		if (Printdialog.getPortComboBox().getItemCount() == 0) {
			Printdialog.getPortComboBox().addItem("None");
		}
	}

	/**
	 * Load the PrintSettingComboBox with the printer settings defined in Slic3r
	 */
	public void updatePrinters() {
		File f = new File(DirPrinter);
		if (f.exists()) {
			File[] ficheros = f.listFiles();
			dialog.getPrintSettingComboBox().removeAllItems();
			dialog.getPrintSettingComboBox().addItem(
					I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.printer"));

			for (int x = 0; x < ficheros.length; x++) {
				String name = ficheros[x].getName();

				getBedSize(ficheros[x].getAbsolutePath());

				dialog.getPrintSettingComboBox().addItem(
						name.replace(".ini", "") + "  (" + Bed_size_high
								+ " x " + Bed_size_width + ")");
			}
			Bed_size_high = 0;
			Bed_size_width = 0;
		}
	}

	/**
	 * Load the PrintingComboBox with the printing settings defined in Slic3r
	 */
	public void updatePrint() {
		File f = new File(DirPrint);
		if (f.exists()) {
			File[] ficheros = f.listFiles();
			Printdialog.getPrintingComboBox().removeAllItems();
			Printdialog.getPrintingComboBox().addItem(
					I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.print-settings"));

			for (int x = 0; x < ficheros.length; x++) {
				String name = ficheros[x].getName();
				Printdialog.getPrintingComboBox().addItem(
						name.replace(".ini", ""));
			}
		}
	}

	/**
	 * Load the FilamentComboBox with the filament settings defined in Slic3r
	 */
	public void updateFilament() {
		File f = new File(DirFilament);
		if (f.exists()) {
			File[] ficheros = f.listFiles();
			Printdialog.getFilamentComboBox().removeAllItems();
			Printdialog.getFilamentComboBox().addItem(I18N.getString("org.saig.jump.controller.demto3d.DemTo3DPrintSettings.filament-settings"));
			for (int x = 0; x < ficheros.length; x++) {
				String name = ficheros[x].getName();
				Printdialog.getFilamentComboBox().addItem(
						name.replace(".ini", ""));
			}
		}
	}

	/**
	 * return the bed size of the printer
	 */
	public void getBedSize(String printer) {
		FileReader fr = null;
		BufferedReader br = null;

		try {
			fr = new FileReader(printer);
			br = new BufferedReader(fr);
			String linea;
			String datos = null;
			while ((linea = br.readLine()) != null) {
				if (linea.contains("bed_size")) {
					datos = linea;
				}
			}
			String[] anchoalto = datos.substring(datos.indexOf("=") + 1).split(
					",");
			this.Bed_size_high = Double.parseDouble(anchoalto[0]);
			this.Bed_size_width = Double.parseDouble(anchoalto[1]);

		} catch (FileNotFoundException e1) {
			e1.printStackTrace();
		} catch (IOException e1) {
			e1.printStackTrace();
		}
	}

	/**
	 * call to Slic3r
	 */
	public void callSlic3r() {
		try {
			String command = PlugInManager.plugInDirectory.getAbsolutePath()
					+ "\\demto3d\\Slic3r\\slic3r.exe";
			Runtime.getRuntime().exec(command);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void update(Observable o, Object arg) {
		if (Print == null || Filament == null) {
			estado = SaveSTL.getEstado();
			Printdialog.gettextArea().append(
					estado + System.getProperty("line.separator"));
		} else if (gcode == true) {
			estado = GetGcode.getEstado();
			com.sendString(estado);
		} else {
			gcode = GetGcode.getgcode();
			estado = GetGcode.getEstado();
			Printdialog.gettextArea().append(
					estado + System.getProperty("line.separator"));
		}
	}
}
