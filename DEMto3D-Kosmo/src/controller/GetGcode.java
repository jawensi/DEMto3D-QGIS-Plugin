package org.saig.jump.controller.demto3d;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Observable;
import java.util.Observer;

import org.saig.jump.dialog.demto3d.PrintDialog;

import com.vividsolutions.jump.workbench.plugin.PlugInManager;

public class GetGcode extends Observable implements Runnable {

	private String DirPrint;
	private String DirPrinter;
	private String DirFilament;

	private String print;
	private String printer;
	private String filament;

	private String file;
	
	private static String estado;
	private static boolean gcode;

	public GetGcode(boolean gcode,String file, String DirPrint, String DirPrinter,
			String DirFilament, String print, String printer, String filament,
			PrintDialog Printdialog, Observer o) {
		super();
		addObserver(o);
		GetGcode.gcode =gcode;
		this.DirPrint = DirPrint;
		this.DirPrinter = DirPrinter;
		this.DirFilament = DirFilament;
		this.print = print;
		this.printer = printer;
		this.filament = filament;
		this.file = file;
	}

	public static String getEstado() {
		return estado;
	}
	public static boolean getgcode() {
		return gcode;
	}
	
	@Override
	public void run() {
		gcode = false;
		String slicer = PlugInManager.plugInDirectory.getAbsolutePath() + "\\demto3d\\Slic3r\\slic3r-console.exe";
		String[] command = { slicer, "-load", DirPrinter.concat(printer),
				"-load", DirPrint.concat(print), "-load",
				DirFilament.concat(filament), file };
		try {
			Process p = Runtime.getRuntime().exec(command);
			BufferedReader in = new BufferedReader(new InputStreamReader(
					p.getInputStream()));

			while ((estado = in.readLine()) != null) {
				setChanged();
				notifyObservers();
			}

		} catch (IOException e) {
			e.printStackTrace();
		}
		
		gcode = true;
		
		File archivo = null;
		FileReader fr = null;
		BufferedReader br = null;

		try {
			File f = new File("tempstl.gcode");

			System.out.println(f.getPath());
			// Apertura del fichero y creacion de BufferedReader para poder
			// hacer una lectura comoda (disponer del metodo readLine()).
			archivo = new File(f.getPath());
			fr = new FileReader(archivo);
			br = new BufferedReader(fr);

			String linea;
			while ((linea = br.readLine()) != null) {
				if (linea.startsWith(";")) {

				} else if (linea.contains(";")) {
					estado = (linea.substring(0, linea.indexOf(";") - 1));
					setChanged();
					notifyObservers();
				} else {
					estado = (linea);
					setChanged();
					notifyObservers();
				}
			}

		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			// En el finally cerramos el fichero, para asegurarnos
			// que se cierra tanto si todo va bien como si salta
			// una excepcion.
			try {
				if (null != fr) {
					fr.close();
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
		}
		
		
	}
}
