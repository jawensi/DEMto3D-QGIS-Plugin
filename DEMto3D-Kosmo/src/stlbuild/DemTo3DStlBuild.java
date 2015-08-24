package org.saig.jump.stlbuild.demto3d;

import javax.vecmath.Point3d;

import org.gdal.gdal.Dataset;
import org.saig.jump.controller.demto3d.DemTo3DController;

public class DemTo3DStlBuild {

	public static Point3d[][] matrixdembuild(Dataset d, double heigh,
			double width, double spacing, double spac_aux, double RoiXmin, double RoiYmin,
			double escala, double Xmin, double Ymin, double Xmax, double Ymax,
			double res, int numCol, int numFil, double zscale, double hbase, boolean projected) {
		
		heigh = heigh*1000;
		width = width*1000;		
		
		int filStl = (int) (DemTo3DController.Redondearmas(heigh / spacing, 0) + 1);
		int colStl = (int) (DemTo3DController.Redondearmas(width / spacing, 0) + 1);

		Point3d[][] matrizdem = new Point3d[filStl][colStl];

		double var_y = heigh;
		for (int i = 0; i < filStl; i++) {
			double var_x = 0;
			for (int j = 0; j < colStl; j++) {
				matrizdem[i][j] = new Point3d();

				/* ORIGEN RESPECTO AL CENTRO DEL PIXEL
				 * matrizdem[i][j].x = DemTo3DController.Redondear(var_x, 2);
				 * double X = (matrizdem[i][j].x * escala) / 1000 + RoiXmin;
				 * double Xcol = (X - (Xmin - res / 2)) * numCol / ((Xmax -
				 * Xmin) + res); int col = (int)
				 * DemTo3DController.Redondearmenos(Xcol, 0);
				 * 
				 * matrizdem[i][j].y = DemTo3DController.Redondear(var_y, 2);
				 * double Y = (matrizdem[i][j].y * escala) / 1000 + RoiYmin;
				 * double Yfil = ((Ymax + res / 2) - Y) * numFil / ((Ymax -
				 * Ymin) + res); int fil = (int)
				 * DemTo3DController.Redondearmenos(Yfil, 0);
				 */
				
				matrizdem[i][j].x = DemTo3DController.Redondear(var_x, 2);
				double X;
				if (projected){
					X = (matrizdem[i][j].x * escala) / 1000 + RoiXmin;
				}else{
					X = matrizdem[i][j].x * spac_aux/spacing  + RoiXmin;
				}
				double Xcol = (X - Xmin) * numCol / (Xmax - Xmin);
				int col = (int) DemTo3DController.Redondearmenos(Xcol, 0);

				if (col == numCol) {
					col = col - 1;
				}

				matrizdem[i][j].y = DemTo3DController.Redondear(var_y, 2);
				double Y;
				if (projected){
					Y = (matrizdem[i][j].y * escala) / 1000 + RoiYmin;
				}else{
					Y = matrizdem[i][j].y * spac_aux/spacing  + RoiYmin;
				}

				double Yfil = (Ymax - Y) * numFil / (Ymax - Ymin);
				int fil = (int) DemTo3DController.Redondearmenos(Yfil, 0);

				if (fil == numFil) {
					fil = fil - 1;
				}

				if (getZ(col, fil, d) < hbase || Double.isNaN(getZ(col, fil, d))) {
					matrizdem[i][j].z = 2;
				} else {

					matrizdem[i][j].z = DemTo3DController
							.Redondear(((getZ(col, fil, d) - hbase) / escala
									* 1000 * zscale), 2) + 2;
					/*
					 * double Z = bilineal(col, fil, X, Y, res, Xmin, Ymin,
					 * Xmax, Ymax, numCol, numFil, d); matrizdem[i][j].z =
					 * DemTo3DController.Redondear( ((Z - hbase) / escala * 1000
					 * * zscale), 2) + 2;
					 */
				}
				var_x = var_x + spacing;
				if (var_x > width) {
					var_x = width;
				}
			}
			var_y = spacing * (filStl - (i + 2));
		}
		return matrizdem;
	}

	public static Point3d[][] matrixdeminversebuild(Point3d[][] matrixdembuild) {
		int fil = matrixdembuild.length;
		int col = matrixdembuild[0].length;

		Point3d[][] matrizdem = new Point3d[fil][col];

		double Zmax = matrixdembuild[0][0].z;
		for (int j = 0; j < fil; j++) {
			for (int k = 0; k < col; k++) {
				if (matrixdembuild[j][k].z > Zmax) {
					Zmax = matrixdembuild[j][k].z;
				}
			}
		}
		for (int j = 0; j < fil; j++) {
			for (int k = 0; k < col; k++) {
				matrixdembuild[j][k].z = (Zmax - matrixdembuild[j][k].z) + 2;
			}
		}
		return matrizdem;
	}

	public static double getZ(int col, int fil, Dataset d) {
		/*
		 * GDALDataType { GDT_Unknown = 0, GDT_Byte = 1, GDT_UInt16 = 2,
		 * GDT_Int16 = 3, GDT_UInt32 = 4, GDT_Int32 = 5, GDT_Float32 = 6,
		 * GDT_Float64 = 7, GDT_CInt16 = 8, GDT_CInt32 = 9, GDT_CFloat32 = 10,
		 * GDT_CFloat64 = 11, GDT_TypeCount = 12 }
		 */

		int dataType = d.GetRasterBand(1).getDataType();
		if (dataType == 6 || dataType == 10) {
			float buffer[] = new float[1];
			int lista[] = new int[d.getRasterCount()];
			for (int i = 0; i < d.getRasterCount(); i++)
				lista[i] = i + 1;
			d.ReadRaster(col, fil, 1, 1, 1, 1,
					d.GetRasterBand(1).getDataType(), buffer, lista);
			if (buffer[0] < 0) {
				return 0;
			} else {
				return buffer[0];
			}
		} else if (dataType == 7 || dataType == 11) {
			double buffer[] = new double[1];
			int lista[] = new int[d.getRasterCount()];
			for (int i = 0; i < d.getRasterCount(); i++)
				lista[i] = i + 1;
			d.ReadRaster(col, fil, 1, 1, 1, 1,
					d.GetRasterBand(1).getDataType(), buffer, lista);
			if (buffer[0] < 0) {
				return 0;
			} else {
				return buffer[0];
			}
		} else if (dataType == 4 || dataType == 5 || dataType == 9) {
			int buffer[] = new int[1];
			int lista[] = new int[d.getRasterCount()];
			for (int i = 0; i < d.getRasterCount(); i++)
				lista[i] = i + 1;
			d.ReadRaster(col, fil, 1, 1, 1, 1,
					d.GetRasterBand(1).getDataType(), buffer, lista);
			if (buffer[0] < 0) {
				return 0;
			} else {
				return buffer[0];
			}
		} else if (dataType == 2 || dataType == 3 || dataType == 8) {
			short buffer[] = new short[1];
			int lista[] = new int[d.getRasterCount()];
			for (int i = 0; i < d.getRasterCount(); i++)
				lista[i] = i + 1;
			d.ReadRaster(col, fil, 1, 1, 1, 1,
					d.GetRasterBand(1).getDataType(), buffer, lista);
			if (buffer[0] < 0) {
				return 0;
			} else {
				return buffer[0];
			}
		}else if (dataType == 1) {
			byte buffer[] = new byte[1*d.getRasterCount()];
			int lista[] = new int[d.getRasterCount()];
			for (int i = 0; i < d.getRasterCount(); i++)
				lista[i] = i + 1;
			d.ReadRaster(col, fil, 1, 1, 1, 1,
					d.GetRasterBand(1).getDataType(), buffer, lista);
				if (buffer[0] < 0) {
					return buffer[0]+128;
				} else {
					return buffer[0]+128;
				}
		}
		return 0;
	}

	public static face[] faceBaseVector(Point3d[][] matrixdembuild) {
		int fil = matrixdembuild.length;
		int col = matrixdembuild[0].length;

		/*
		 * face[] vectorfaces = new face[2];
		 * 
		 * vectorfaces[0] = new face();
		 * vectorfaces[0].setP1(matrixdembuild[0][0]);
		 * vectorfaces[0].setP2(matrixdembuild[0][col - 1]);
		 * vectorfaces[0].setP3(matrixdembuild[fil - 1][0]); Point3d N = new
		 * Point3d(); N.set(0, 0, -1); vectorfaces[0].setN(N);
		 * 
		 * vectorfaces[1] = new face();
		 * vectorfaces[1].setP1(matrixdembuild[0][col - 1]);
		 * vectorfaces[1].setP2(matrixdembuild[fil - 1][col - 1]);
		 * vectorfaces[1].setP3(matrixdembuild[fil - 1][0]);
		 * vectorfaces[1].setN(N);
		 */

		face[] vectorfaces = new face[((fil - 1) * (col - 1)) * 2];

		int i = 0;
		for (int j = 0; j < (fil - 1); j++) {
			for (int k = 0; k < (col - 1); k++) {
				vectorfaces[i] = new face();
				vectorfaces[i].setP1(matrixdembuild[j][k]);
				vectorfaces[i].setP2(matrixdembuild[j][k + 1]);
				vectorfaces[i].setP3(matrixdembuild[j + 1][k]);
				Point3d N = new Point3d();
				N.set(0, 0, -1);
				vectorfaces[i].setN(N);

				vectorfaces[i + 1] = new face();
				vectorfaces[i + 1].setP1(matrixdembuild[j][k + 1]);
				vectorfaces[i + 1].setP2(matrixdembuild[j + 1][k + 1]);
				vectorfaces[i + 1].setP3(matrixdembuild[j + 1][k]);
				vectorfaces[i + 1].setN(N);

				i += 2;
			}
		}

		return vectorfaces;
	}

	public static face[] faceMdeVector(Point3d[][] matrixdembuild) {
		int fil = matrixdembuild.length;
		int col = matrixdembuild[0].length;

		face[] vectorfaces = new face[((fil - 1) * (col - 1)) * 2];

		int i = 0;
		for (int j = 0; j < (fil - 1); j++) {
			for (int k = 0; k < (col - 1); k++) {
				vectorfaces[i] = new face();
				vectorfaces[i].setP3(matrixdembuild[j][k]);
				vectorfaces[i].setP2(matrixdembuild[j][k + 1]);
				vectorfaces[i].setP1(matrixdembuild[j + 1][k]);
				vectorfaces[i].setN(getNormal(vectorfaces[i].getP1(),
						vectorfaces[i].getP2(), vectorfaces[i].getP3()));

				vectorfaces[i + 1] = new face();
				vectorfaces[i + 1].setP3(matrixdembuild[j][k + 1]);
				vectorfaces[i + 1].setP2(matrixdembuild[j + 1][k + 1]);
				vectorfaces[i + 1].setP1(matrixdembuild[j + 1][k]);
				vectorfaces[i + 1]
						.setN(getNormal(vectorfaces[i + 1].getP1(),
								vectorfaces[i + 1].getP2(),
								vectorfaces[i + 1].getP3()));

				i += 2;
			}
		}
		return vectorfaces;
	}

	public static face[] faceWallsVector(Point3d[][] matrixdembuild) {
		int fil = matrixdembuild.length;
		int col = matrixdembuild[0].length;

		face[] vectorfaces = new face[(fil - 1) * 2 * 2 + (col - 1) * 2 * 2];

		int i = 0;
		for (int j = 0; j < (fil - 1); j++) {

			vectorfaces[i] = new face();
			vectorfaces[i].setP1(getBasePoint(matrixdembuild[j][0]));
			vectorfaces[i].setP2(matrixdembuild[j + 1][0]);
			vectorfaces[i].setP3(matrixdembuild[j][0]);
			Point3d N = new Point3d();
			N.set(0, -1, 0);
			vectorfaces[i].setN(N);

			vectorfaces[i + 1] = new face();
			vectorfaces[i + 1].setP3(matrixdembuild[j + 1][0]);
			vectorfaces[i + 1].setP2(getBasePoint(matrixdembuild[j + 1][0]));
			vectorfaces[i + 1].setP1(getBasePoint(matrixdembuild[j][0]));
			vectorfaces[i + 1].setN(N);

			vectorfaces[i + 2] = new face();
			vectorfaces[i + 2].setP3(getBasePoint(matrixdembuild[j][col - 1]));
			vectorfaces[i + 2].setP2(matrixdembuild[j + 1][col - 1]);
			vectorfaces[i + 2].setP1(matrixdembuild[j][col - 1]);
			Point3d N2 = new Point3d();
			N2.set(0, 1, 0);
			vectorfaces[i + 2].setN(N2);

			vectorfaces[i + 3] = new face();
			vectorfaces[i + 3].setP1(matrixdembuild[j + 1][col - 1]);
			vectorfaces[i + 3]
					.setP2(getBasePoint(matrixdembuild[j + 1][col - 1]));
			vectorfaces[i + 3].setP3(getBasePoint(matrixdembuild[j][col - 1]));
			vectorfaces[i + 3].setN(N2);

			i += 4;
		}
		for (int j = 0; j < (col - 1); j++) {

			vectorfaces[i] = new face();
			vectorfaces[i].setP3(getBasePoint(matrixdembuild[0][j]));
			vectorfaces[i].setP2(matrixdembuild[0][j + 1]);
			vectorfaces[i].setP1(matrixdembuild[0][j]);
			Point3d N = new Point3d();
			N.set(-1, 0, 0);
			vectorfaces[i].setN(N);

			vectorfaces[i + 1] = new face();
			vectorfaces[i + 1].setP1(matrixdembuild[0][j + 1]);
			vectorfaces[i + 1].setP2(getBasePoint(matrixdembuild[0][j + 1]));
			vectorfaces[i + 1].setP3(getBasePoint(matrixdembuild[0][j]));
			vectorfaces[i + 1].setN(N);

			vectorfaces[i + 2] = new face();
			vectorfaces[i + 2].setP1(getBasePoint(matrixdembuild[fil - 1][j]));
			vectorfaces[i + 2].setP2(matrixdembuild[fil - 1][j + 1]);
			vectorfaces[i + 2].setP3(matrixdembuild[fil - 1][j]);
			Point3d N2 = new Point3d();
			N2.set(1, 0, 0);
			vectorfaces[i + 2].setN(N2);

			vectorfaces[i + 3] = new face();
			vectorfaces[i + 3].setP3(matrixdembuild[fil - 1][j + 1]);
			vectorfaces[i + 3]
					.setP2(getBasePoint(matrixdembuild[fil - 1][j + 1]));
			vectorfaces[i + 3].setP1(getBasePoint(matrixdembuild[fil - 1][j]));
			vectorfaces[i + 3].setN(N2);

			i += 4;
		}
		return vectorfaces;
	}

	public static double bilineal(int col, int fil, double X, double Y,
			double res, double Xmin, double Ymin, double Xmax, double Ymax,
			int numCol, int numFil, Dataset d) {
		double Y2 = 0;
		double X2 = 0;
		double X1 = 0;
		double Y1 = 0;
		double Z21 = 0;
		double Z12 = 0;
		double Z22 = 0;
		double Z11 = 0;
		double Xpix = Xmin + res * col + res / 2;
		double Ypix = Ymax - res * fil - res / 2;

		if (X - Xpix <= 0) {
			X1 = Xmin + res * (col);
			X2 = Xmin + res * (col + 1);
		}
		if (Y - Ypix >= 0) {
			Y1 = Ymax - res * (fil);
			Y2 = Ymax - res * (fil + 1);
		}
		if (X - Xpix > 0) {
			X1 = Xmin + res * (col - 1);
			X2 = Xmin + res * (col);
		}
		if (Y - Ypix < 0) {
			Y1 = Ymax - res * (fil - 1);
			Y2 = Ymax - res * (fil);
		}

		int col1 = (int) DemTo3DController.Redondearmenos(
				(X1 - (Xmin - res / 2)) * numCol / ((Xmax - Xmin) + res), 0);
		int fil1 = (int) DemTo3DController.Redondearmenos(
				((Ymax + res / 2) - Y1) * numFil / ((Ymax - Ymin) + res), 0);
		int col2 = (int) DemTo3DController.Redondearmenos(
				(X2 - (Xmin - res / 2)) * numCol / ((Xmax - Xmin) + res), 0);
		int fil2 = (int) DemTo3DController.Redondearmenos(
				((Ymax + res / 2) - Y2) * numFil / ((Ymax - Ymin) + res), 0);

		Z11 = getZ(col1, fil1, d);
		Z22 = getZ(col2, fil2, d);
		Z12 = getZ(col1, fil2, d);
		Z21 = getZ(col2, fil1, d);

		double Z0 = (X2 - X) * (Y2 - Y) / ((X2 - X1) * (Y2 - Y1)) * Z11;
		double Z1 = (X - X1) * (Y2 - Y) / ((X2 - X1) * (Y2 - Y1)) * Z21;
		double Z2 = (X2 - X) * (Y - Y1) / ((X2 - X1) * (Y2 - Y1)) * Z12;
		double Z3 = (X - X1) * (Y - Y1) / ((X2 - X1) * (Y2 - Y1)) * Z22;
		return Z0 + Z1 + Z2 + Z3;
	}

	public static Point3d getBasePoint(Point3d Pto) {
		Point3d P = new Point3d();
		P.x = Pto.x;
		P.y = Pto.y;
		P.z = 0;
		return P;
	}

	public static Point3d getNormal(Point3d P1, Point3d P2, Point3d P3) {
		Point3d V = new Point3d();
		V.set(P2.x - P1.x, P2.y - P1.y, P2.z - P1.z);
		Point3d W = new Point3d();
		W.set(P3.x - P1.x, P3.y - P1.y, P3.z - P1.z);

		Point3d normal = new Point3d();
		normal.x = (V.y * W.z) - (V.z - W.y);
		normal.y = (V.z * W.x) - (V.x - W.z);
		normal.z = (V.x * W.y) - (V.y - W.x);

		double modulo = Math.sqrt(normal.x * normal.x + normal.y * normal.y
				+ normal.z * normal.z);

		normal.x = (normal.x / modulo);
		normal.y = (normal.y / modulo);
		normal.z = (normal.z / modulo);

		return normal;
	}

	public static class face {
		private Point3d P1;
		private Point3d P2;
		private Point3d P3;
		private Point3d N;

		public face() {
			P1 = null;
			P2 = null;
			P3 = null;
			N = null;
		}

		public Point3d getP1() {
			return P1;
		}

		public void setP1(final Point3d P1) {
			this.P1 = P1;
		}

		public Point3d getP2() {
			return P2;
		}

		public void setP2(final Point3d P2) {
			this.P2 = P2;
		}

		public Point3d getP3() {
			return P3;
		}

		public void setP3(final Point3d P3) {
			this.P3 = P3;
		}

		public Point3d getN() {
			return N;
		}

		public void setN(final Point3d N) {
			this.N = N;
		}
	}
}
