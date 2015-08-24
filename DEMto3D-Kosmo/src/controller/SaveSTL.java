package org.saig.jump.controller.demto3d;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.Observable;
import java.util.Observer;

import javax.swing.JFrame;
import javax.vecmath.Point3d;

import org.gdal.gdal.Dataset;
import org.saig.jump.dialog.demto3d.DemTo3DDialog;
import org.saig.jump.lang.I18N;
import org.saig.jump.stlbuild.demto3d.DemTo3DStlBuild;
import org.saig.jump.stlbuild.demto3d.DemTo3DStlBuild.face;

public class SaveSTL extends Observable implements Runnable {

	File f;
	Point3d[][] matrizdem;
	face[] base;
	face[] dem;
	face[] walls;
	double RoiXmin;
	double RoiYmin;
	double scale;
	double spacing;
	double spac_aux;
	double high;
	double width;
	double zscale;
	double hbase;
	double RasterXmax;
	double RasterXmin;
	double RasterYmax;
	double RasterYmin;
	int numCol;
	int numFil;
	float tamCell;
	boolean projected;
	Dataset dataset;
	DemTo3DDialog dialog;
	JFrame frame;
	static String estado;

	public SaveSTL(File f, double RoiXmin, double RoiYmin, double scale,
			double spacing,double spac_aux, double high, double width, double zscale,double hbase,
			double RasterXmax, double RasterXmin, double RasterYmax,
			double RasterYmin, int numCol, int numFil, float tamCell,boolean projected,
			Dataset dataset, DemTo3DDialog dialog, Observer o, JFrame frame) {
		super();
		if (o != null) {
			addObserver(o);
		}
		this.f = f;
		this.RoiXmin = RoiXmin;
		this.RoiYmin = RoiYmin;
		this.scale = scale;
		this.spacing = spacing;
		this.spac_aux = spac_aux;;
		this.high = high;
		this.width = width;
		this.zscale = zscale;
		this.hbase = hbase;
		this.RasterXmax = RasterXmax;
		this.RasterXmin = RasterXmin;
		this.RasterYmax = RasterYmax;
		this.RasterYmin = RasterYmin;
		this.numCol = numCol;
		this.numFil = numFil;
		this.tamCell = tamCell;
		this.projected = projected;
		this.dataset = dataset;
		this.dialog = dialog;
		this.frame = frame;
	}

	public static String getEstado() {
		return estado;
	}

	@Override
	public void run() {
		try {
			FileWriter w = new FileWriter(f);
			BufferedWriter bw = new BufferedWriter(w);
			PrintWriter wr = new PrintWriter(bw);

			matrizdem = DemTo3DStlBuild.matrixdembuild(dataset, high ,
					width , spacing,spac_aux, RoiXmin, RoiYmin, scale, RasterXmin,
					RasterYmin, RasterXmax, RasterYmax, tamCell, numCol,
					numFil, zscale,hbase, projected);

			if (dialog.getchckbxZinverse().isSelected() == true) {
				DemTo3DStlBuild.matrixdeminversebuild(matrizdem);
			}

			if (frame == null) {	
				estado = I18N.getString("org.saig.jump.controller.demto3d.SaveSTL.creating-STL-geometry");
				setChanged();
				notifyObservers();
			}

			// Escritura del archivo stl
			wr.write("solid "
					+ dialog.getselectInputLayerComboBox().getSelectedItem()
							.toString() + "\n");

			DecimalFormatSymbols simbolos = new DecimalFormatSymbols();
			simbolos.setDecimalSeparator('.');
			DecimalFormat formateador = new DecimalFormat("0.000000E000",
					simbolos);
			
			base = DemTo3DStlBuild.faceBaseVector(matrizdem);
			for (int j = 0; j < base.length; j++) {
				wr.write("  facet normal "
						+ formateador.format(base[j].getN().x) + " "
						+ formateador.format(base[j].getN().y) + " "
						+ formateador.format(base[j].getN().z) + "\n");
				wr.write("    outer loop" + "\n");
				wr.write("      vertex  "
						+ formateador.format(base[j].getP1().x) + " "
						+ formateador.format(base[j].getP1().y) + " " + 0
						+ "\n");
				wr.write("      vertex  "
						+ formateador.format(base[j].getP2().x) + " "
						+ formateador.format(base[j].getP2().y) + " " + 0
						+ "\n");
				wr.write("      vertex  "
						+ formateador.format(base[j].getP3().x) + " "
						+ formateador.format(base[j].getP3().y) + " " + 0
						+ "\n");
				wr.write("    endloop" + "\n");
				wr.write("  endfacet" + "\n");
			}
			walls = DemTo3DStlBuild.faceWallsVector(matrizdem);
			for (int j = 0; j < walls.length; j++) {
				wr.write("  facet normal "
						+ formateador.format(walls[j].getN().x) + " "
						+ formateador.format(walls[j].getN().y) + " "
						+ formateador.format(walls[j].getN().z) + "\n");
				wr.write("    outer loop" + "\n");
				wr.write("      vertex  "
						+ formateador.format(walls[j].getP1().x) + " "
						+ formateador.format(walls[j].getP1().y) + " "
						+ formateador.format(walls[j].getP1().z) + "\n");
				wr.write("      vertex  "
						+ formateador.format(walls[j].getP2().x) + " "
						+ formateador.format(walls[j].getP2().y) + " "
						+ formateador.format(walls[j].getP2().z) + "\n");
				wr.write("      vertex  "
						+ formateador.format(walls[j].getP3().x) + " "
						+ formateador.format(walls[j].getP3().y) + " "
						+ formateador.format(walls[j].getP3().z) + "\n");
				wr.write("    endloop" + "\n");
				wr.write("  endfacet" + "\n");
			}
			dem = DemTo3DStlBuild.faceMdeVector(matrizdem);
			for (int j = 0; j < dem.length; j++) {
				wr.write("  facet normal "
						+ formateador.format(dem[j].getN().x) + " "
						+ formateador.format(dem[j].getN().y) + " "
						+ formateador.format(dem[j].getN().z) + "\n");
				wr.write("    outer loop" + "\n");
				wr.write("      vertex  "
						+ formateador.format(dem[j].getP1().x) + " "
						+ formateador.format(dem[j].getP1().y) + " "
						+ formateador.format(dem[j].getP1().z) + "\n");
				wr.write("      vertex  "
						+ formateador.format(dem[j].getP2().x) + " "
						+ formateador.format(dem[j].getP2().y) + " "
						+ formateador.format(dem[j].getP2().z) + "\n");
				wr.write("      vertex  "
						+ formateador.format(dem[j].getP3().x) + " "
						+ formateador.format(dem[j].getP3().y) + " "
						+ formateador.format(dem[j].getP3().z) + "\n");
				wr.write("    endloop" + "\n");
				wr.write("  endfacet" + "\n");
			}
			wr.write("endsolid "
					+ dialog.getselectInputLayerComboBox().getSelectedItem()
							.toString());
			wr.close();
			bw.close();
			w.close();

		} catch (IOException e) {
		}
		if (frame != null) {
			frame.dispose();
		}
		if (frame == null) {
			estado = I18N.getString("org.saig.jump.controller.demto3d.SaveSTL.STL-geometry-created");
			setChanged();
			notifyObservers();
		}
		if (frame != null) {
			setChanged();
			notifyObservers();
		}
	}

}
