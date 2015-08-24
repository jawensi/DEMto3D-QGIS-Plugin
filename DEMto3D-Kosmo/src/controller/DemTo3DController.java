package org.saig.jump.controller.demto3d;


import java.awt.Desktop;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.File;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Observable;
import java.util.Observer;

import javax.swing.ImageIcon;
import javax.swing.JDialog;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.filechooser.FileNameExtensionFilter;

import org.gdal.gdal.Dataset;
import org.gdal.gdal.gdal;
import org.saig.jump.dialog.demto3d.DemTo3DDialog;
import org.saig.jump.dialog.demto3d.PrintDialog;
import org.saig.jump.lang.I18N;
import org.saig.jump.plugin.demto3d.DemTo3DPlugIn;

import com.vividsolutions.jts.geom.Envelope;
import com.vividsolutions.jump.workbench.model.Layer;
import com.vividsolutions.jump.workbench.plugin.PlugInContext;
import com.vividsolutions.jump.workbench.ui.GUIUtil;

public class DemTo3DController implements Observer {

	/** Options dialog */
	private DemTo3DDialog dialog;

	/** Current context */
	private PlugInContext context;

	/** Print Settings */
	private DemTo3DPrintSettings printSettings;

	/** Layer File path */
	private String LayerfilePath;

	/** Raster dataset */
	private Dataset dataset = null;

	/** Raster geometric properties */
	// Max y Min respect pixel limit 
	private double RasterXmax;
	private double RasterXmin;
	private double RasterYmax;
	private double RasterYmin;
	private int numCol;
	private int numFil;
	private float tamCell;
	private boolean projected;

	/** Region of interest properties */
	// center pixel
	private double RoiXmax;
	private double RoiXmin;
	private double RoiYmax;
	private double RoiYmin;
	private double scale;
	private double spacing; //mm
	private double spac_aux; //grad (if not projected)
	private double high;
	private double width;
	private double zscale;
	private double hbase;
	private double hmax;
	private double hmin;

	/** Print options dialog */
	private PrintDialog Printdialog;

	/****************************************************************************************/

	/**
	 * @param context
	 */
	public DemTo3DController(PlugInContext context) {
		createDialog();
		this.context = context;
	}

	/**
	 * Create the dialog panel
	 */
	private void createDialog() {
		dialog = new DemTo3DDialog();
		dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
		dialog.setVisible(true);
		dialog.setLocationRelativeTo(null);
		printSettings = new DemTo3DPrintSettings(dialog, Printdialog);
		printSettings.updatePrinters();
		addListeners();
	}

	/**
	 * Load the listener belonging to the dialog
	 */
	private void addListeners() {
		dialog.addWindowListener(new WindowAdapter() {
			public void windowClosed(WindowEvent e) {
				DemTo3DPlugIn.TstVentNvoPres = false;
				if (dataset != null) {
					dataset.delete();
				}
			}
		});
		dialog.getbtnAyuda().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				try {
					Desktop.getDesktop().browse(
							new URI("http://demto3d.com/?page_id=13"));
				} catch (IOException e1) {

					e1.printStackTrace();
				} catch (URISyntaxException e1) {

					e1.printStackTrace();
				}
			}
		});
		dialog.getbtnCancelar().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				DemTo3DPlugIn.TstVentNvoPres = false;
				dialog.dispose();
				if (dataset != null) {
					dataset.delete();
				}
			}
		});
		dialog.getbtnAceptar().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e)
					throws NumberFormatException {
				try {
					if (printSettings.Bed_size_high > (high * 1000)
							&& printSettings.Bed_size_width > (width * 1000)) {
						imprimir();
					} else if (printSettings.Bed_size_high == 0
							|| printSettings.Bed_size_width == 0) {
						JOptionPane.showMessageDialog(
								null,
								I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.select-printer"),
								"DEMto3D", 2);
					} else {
						JOptionPane.showMessageDialog(
								null,
								I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.model-exceed")
										+ "\n"
										+ I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.change-model-size"),
								"DEMto3D", 2);
					}
				} catch (NumberFormatException exc) {
					JOptionPane.showMessageDialog(
							null,
							I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.fill-correct"),
							"DEMto3D", 2);
				} catch (CheckSpacing e1) {
				} catch (CheckDimension e1) {
				}
			}
		});
		dialog.getSelectPrinter().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				printSettings.callSlic3r();
			}
		});
		dialog.getbtnExportStl().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				try {
					if (high == 0 && width == 0) {
						throw new CheckDimension();
					} else if (dialog.getHeightTextField().getText().length() == 0) {
						throw new CheckHbase();
					} else {
						getZscale();
						getSpacing();

						JFileChooser selectorArchivo = new JFileChooser();
						selectorArchivo
								.setFileSelectionMode(JFileChooser.FILES_ONLY);
						selectorArchivo = GUIUtil
								.createJFileChooserWithOverwritePromptingAndDefaultExtension("stl");
						javax.swing.filechooser.FileFilter filtro = new FileNameExtensionFilter(
								I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.stl-file"),
								"stl");
						selectorArchivo.setFileFilter(filtro);
						selectorArchivo.setMultiSelectionEnabled(false);

						try {
							if (selectorArchivo.showSaveDialog(null) == JFileChooser.APPROVE_OPTION) {
								File f = selectorArchivo.getSelectedFile();

								JFrame frame = new JFrame("DEMTO3D");
								frame.setIconImage(Toolkit
										.getDefaultToolkit()
										.getImage(
												DemTo3DDialog.class
														.getResource("/org/saig/jump/images/demto3d/stl_icon.png")));
								;
								JLabel label = new JLabel(
										"   "
												+ I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.export-model-stl"));
								frame.setSize(278, 129);
								frame.add(label);
								frame.setLocationRelativeTo(dialog);
								
								
								SaveSTL hilo = new SaveSTL(f, RoiXmin, RoiYmin,
										scale, spacing,spac_aux, high, width, zscale,
										hbase, RasterXmax, RasterXmin,
										RasterYmax, RasterYmin, numCol, numFil,
										tamCell, projected, dataset, dialog,
										DemTo3DController.this, frame);
								Thread savestl = new Thread(hilo);
								savestl.start();
								frame.setVisible(true);
								frame.setEnabled(false);
							}
						} catch (Exception ex) {
							ex.printStackTrace();
						}
					}
				} catch (CheckDimension ev) {
				} catch (CheckSpacing ev) {
				} catch (CheckHbase ev) {
				}
			}

		});
		dialog.getselectInputLayerComboBox().addItemListener(
				new ItemListener() {
					public void itemStateChanged(ItemEvent e) {
						// updateLayers();
						if (dataset == null) {
							openfile();
							iniGeometricProperties();

						} else {
							dataset.delete();
							openfile();
							iniGeometricProperties();

						}
					}
				});
		dialog.getPrintSettingComboBox().addItemListener(new ItemListener() {
			@Override
			public void itemStateChanged(ItemEvent e) {
				if (dialog.getPrintSettingComboBox().getSelectedItem()
						.toString() != I18N
						.getString("org.saig.jump.controller.demto3d.DemTo3DController.printer")) {
					String elem = dialog.getPrintSettingComboBox()
							.getSelectedItem().toString();
					printSettings.Printer = elem.substring(0,
							elem.indexOf("(") - 2).concat(".ini");
					printSettings.getBedSize(printSettings.DirPrinter
							+ printSettings.Printer);
				} else {
					printSettings.Bed_size_high = 0;
					printSettings.Bed_size_width = 0;
				}
			}
		});
		dialog.getselectFullExtension().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				iniGeometricProperties();
				getFullExtend();
			}
		});
		dialog.getselectCustomExtension().addActionListener(
				new ActionListener() {
					public void actionPerformed(ActionEvent e) {
						try {
							getCustomExtend();
						} catch (CheckExtension e1) {
						}
					}
				});
		dialog.getselectInputXDownCorner().addActionListener(
				new ActionListener() {
					public void actionPerformed(ActionEvent e) {
						RoiXmax = Double.parseDouble(dialog
								.getselectInputXDownCorner().getText());
						if (RoiXmax <= RasterXmax & RoiXmax >= RasterXmin
								& RoiXmin != 0 & RoiYmax != 0 & RoiYmin != 0) {
							getHmaxHmin();
						} else {
							JOptionPane.showMessageDialog(
									null,
									I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.wrong-coordinate"),
									"DEMTO3D", JOptionPane.ERROR_MESSAGE);
							dialog.getselectInputXDownCorner().setText("");
						}
					}
				});
		dialog.getselectInputXUpperCorner().addActionListener(
				new ActionListener() {
					public void actionPerformed(ActionEvent e) {
						RoiXmin = Double.parseDouble(dialog
								.getselectInputXUpperCorner().getText());
						if (RoiXmin <= RasterXmax & RoiXmin >= RasterXmin
								& RoiXmax != 0 & RoiYmax != 0 & RoiYmin != 0) {
							getHmaxHmin();
						} else {
							JOptionPane.showMessageDialog(
									null,
									I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.wrong-coordinate"),
									"DEMTO3D", JOptionPane.ERROR_MESSAGE);
							dialog.getselectInputXUpperCorner().setText("");
						}
					}
				});
		dialog.getselectInputYDownCorner().addActionListener(
				new ActionListener() {
					public void actionPerformed(ActionEvent e) {
						RoiYmin = Double.parseDouble(dialog
								.getselectInputYDownCorner().getText());
						if (RoiYmin <= RasterYmax & RoiYmin >= RasterYmin
								& RoiYmax != 0 & RoiXmax != 0 & RoiXmin != 0) {
							getHmaxHmin();
						} else {
							JOptionPane.showMessageDialog(
									null,
									I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.wrong-coordinate"),
									"DEMTO3D", JOptionPane.ERROR_MESSAGE);
							dialog.getselectInputYDownCorner().setText("");
						}
					}
				});
		dialog.getselectInputYUpperCorner().addActionListener(
				new ActionListener() {
					public void actionPerformed(ActionEvent e) {
						RoiYmax = Double.parseDouble(dialog
								.getselectInputYUpperCorner().getText());
						if (RoiYmax <= RasterYmax & RoiYmax >= RasterYmin
								& RoiYmin != 0 & RoiXmax != 0 & RoiXmin != 0) {
							getHmaxHmin();
						} else {
							JOptionPane.showMessageDialog(
									null,
									I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.wrong-coordinate"),
									"DEMTO3D", JOptionPane.ERROR_MESSAGE);
							dialog.getselectInputYUpperCorner().setText("");
						}
					}
				});
		dialog.getcellSizeTextField().addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				try {
					getSpacing();
				} catch (CheckSpacing ev) {
				}
			}
		});

		dialog.getHighTextField().addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				try {
					getDimensionFromHeight();
					getMinSpace();
				} catch (CheckExtension e1) {
					dialog.getHighTextField().setText("");
				} catch (NumberFormatException e1) {
					JOptionPane.showMessageDialog(
							null,
							I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.error"),
							"DEMTO3D", JOptionPane.ERROR_MESSAGE);
					dialog.getHighTextField().setText("");
				}
			}
		});
		dialog.getWidthTextField().addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				try {
					getDimensionFromWidth();
					getMinSpace();
				} catch (CheckExtension e1) {
					dialog.getWidthTextField().setText("");
				} catch (NumberFormatException e1) {
					JOptionPane.showMessageDialog(
							null,
							I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.error"),
							"DEMTO3D", JOptionPane.ERROR_MESSAGE);
					dialog.getWidthTextField().setText("");
				}
			}
		});
		dialog.getscaleTextField().addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				try {
					getDimensionFromScale();
					getMinSpace();
				} catch (CheckExtension e1) {
					dialog.getscaleTextField().setText("");
				} catch (NumberFormatException e1) {
					JOptionPane.showMessageDialog(
							null,
							I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.error"),
							"DEMTO3D", JOptionPane.ERROR_MESSAGE);
					dialog.getscaleTextField().setText("");
				}
			}
		});
		dialog.getslider().addChangeListener(new ChangeListener() {
			public void stateChanged(ChangeEvent e) {
				getZscale();
				dialog.getlabelHbaseModel()
						.setText(
								I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.height-model"));
			}
		});
		dialog.getHeightTextField().addActionListener(new ActionListener() {

			public void actionPerformed(ActionEvent e) {
				try {
					getHeightModel();
				} catch (CheckScale e1) {
					dialog.getHeightTextField().setText("");
				} catch (NumberFormatException e1) {
					JOptionPane.showMessageDialog(
							null,
							I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.error"),
							"DEMTO3D", JOptionPane.ERROR_MESSAGE);
					dialog.getHeightTextField().setText("");
				} catch (CheckHbase e1) {
					dialog.getHeightTextField().setText("");
					dialog.getlabelHbaseModel()
							.setText(
									I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.height-model"));
				}
			}
		});
	}

	public void imprimir() throws CheckSpacing, CheckDimension {
		if (high == 0 && width == 0) {
			throw new CheckDimension();
		} else {
			getSpacing();
			getZscale();
			Printdialog = new PrintDialog();
			Printdialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
			Printdialog.setLocationRelativeTo(dialog);
			Printdialog.setVisible(true);
			printSettings.Printdialog = Printdialog;
			printSettings.updatePrint();
			printSettings.updateFilament();
			printSettings.updatePorts();
			printSettings.addListeners();
			Printdialog.pack();

			File f = new File("tempstl.stl");

			SaveSTL hilo = new SaveSTL(f, RoiXmin, RoiYmin, scale, spacing,spac_aux,
					high, width, zscale, hbase, RasterXmax, RasterXmin,
					RasterYmax, RasterYmin, numCol, numFil, tamCell,projected, dataset,
					dialog, printSettings, null);
			Thread savestl = new Thread(hilo);
			savestl.start();
		}
	}

	public void iniGeometricProperties() {
		Layer layer = (Layer) dialog.getselectInputLayerComboBox()
				.getSelectedItem();
		Envelope extend = layer.getVista();
		
		this.projected = layer.getProjection().isProjected();
		this.RasterXmax = extend.getMaxX();
		this.RasterXmin = extend.getMinX();
		this.RasterYmax = extend.getMaxY();
		this.RasterYmin = extend.getMinY();
		this.numCol = dataset.getRasterXSize();
		this.numFil = dataset.getRasterYSize();
		double[] geotransform = dataset.GetGeoTransform();
		this.tamCell = (float) geotransform[1];
	}

	public void getHmaxHmin() {

		int xoff = (int) Redondearmenos(
				((RoiXmin - RasterXmin) * numCol / (RasterXmax - RasterXmin)),
				0);
		int yoff = (int) Redondearmenos(
				((RasterYmax - RoiYmax) * numFil / (RasterYmax - RasterYmin)),
				0);

		int col = (int) Redondearmenos(((RoiXmax - RoiXmin) / tamCell), 0);
		int fil = (int) Redondearmenos(((RoiYmax - RoiYmin) / tamCell), 0);

		int lista[] = new int[dataset.getRasterCount()];
		for (int i = 0; i < dataset.getRasterCount(); i++)
			lista[i] = i + 1;
		int dataType = dataset.GetRasterBand(1).getDataType();
		if (dataType == 6 || dataType == 10) {

			float buffer1[] = new float[fil * col];
			dataset.ReadRaster(xoff, yoff, col, fil, col, fil, dataset
					.GetRasterBand(1).getDataType(), buffer1, lista);
			double Zmin = buffer1[0];
			double Zmax = 0;
			for (int j = 0; j < buffer1.length; j++) {
				if (buffer1[j] > Zmax) {
					Zmax = buffer1[j];
				}
				if (buffer1[j] < Zmin) {
					Zmin = buffer1[j];
				}
			}
			this.hmax = Zmax;
			if (Zmin < 0  || Double.isNaN(Zmin)) {
				this.hmin = 0;
			} else {
				this.hmin = Zmin;
			}
		} else if (dataType == 7 || dataType == 11) {

			double buffer1[] = new double[fil * col];
			dataset.ReadRaster(xoff, yoff, col, fil, col, fil, dataset
					.GetRasterBand(1).getDataType(), buffer1, lista);
			double Zmin = buffer1[0];
			double Zmax = 0;
			for (int j = 0; j < buffer1.length; j++) {
				if (buffer1[j] > Zmax) {
					Zmax = buffer1[j];
				}
				if (buffer1[j] < Zmin) {
					Zmin = buffer1[j];
				}
			}
			this.hmax = Zmax;
			if (Zmin < 0|| Double.isNaN(Zmin)) {
				this.hmin = 0;
			} else {
				this.hmin = Zmin;
			}
		} else if (dataType == 4 || dataType == 5 || dataType == 9) {

			int buffer1[] = new int[fil * col];
			dataset.ReadRaster(xoff, yoff, col, fil, col, fil, dataset
					.GetRasterBand(1).getDataType(), buffer1, lista);
			double Zmin = buffer1[0];
			double Zmax = 0;
			for (int j = 0; j < buffer1.length; j++) {
				if (buffer1[j] > Zmax) {
					Zmax = buffer1[j];
				}
				if (buffer1[j] < Zmin) {
					Zmin = buffer1[j];
				}
			}
			this.hmax = Zmax;
			if (Zmin < 0|| Double.isNaN(Zmin)) {
				this.hmin = 0;
			} else {
				this.hmin = Zmin;
			}
		} else if (dataType == 2 || dataType == 3 || dataType == 8) {
			short buffer1[] = new short[fil * col];
			dataset.ReadRaster(xoff, yoff, col, fil, col, fil, dataset
					.GetRasterBand(1).getDataType(), buffer1, lista);
			double Zmin = buffer1[0];
			double Zmax = 0;
			for (int j = 0; j < buffer1.length; j++) {
				if (buffer1[j] > Zmax) {
					Zmax = buffer1[j];
				}
				if (buffer1[j] < Zmin) {
					Zmin = buffer1[j];
				}
			}
			this.hmax = Zmax;
			if (Zmin < 0|| Double.isNaN(Zmin)) {
				this.hmin = 0;
			} else {
				this.hmin = Zmin;
			}
		}else if (dataType == 1 ) {
			double min[] = new double[1];
			double max[] = new double[1];
			dataset.GetRasterBand(1).ComputeStatistics(false, min, max);
			this.hmin  = min[0];
			this.hmax = max[0];		
		}

		dialog.getlabelMaxH()
				.setText(
						I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.max-height")
								+ "   "
								+ String.valueOf(Redondear(hmax, 3))
								+ " m");
		dialog.getlabelMinH()
				.setText(
						I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.min-height")
								+ "    "
								+ String.valueOf(Redondear(hmin, 3))
								+ " m");
	}

	/**
	 * Load the selectInputLayerComboBox with the layers load in the layer list
	 */
	public void updateLayers() {
		List<Layer> layers = context.getLayerManager().getLayers();
		Collections.sort(layers);
		dialog.getselectInputLayerComboBox().removeAllItems();

		for (Iterator<Layer> iter = layers.iterator(); iter.hasNext();) {
			Layer element = iter.next();
			if (element.isRaster() && element.isVisible()) {
				dialog.getselectInputLayerComboBox().addItem(element);
			}
		}
	}

	/**
	 * return the dialog created
	 */
	public DemTo3DDialog getdialog() {
		return dialog;
	}

	/**
	 * return the file path for the layer selected in the
	 * selectInputLayerComboBox
	 */
	public void getfilePath() {
		LayerfilePath = null;
		Layer layer = (Layer) dialog.getselectInputLayerComboBox()
				.getSelectedItem();
		
		this.LayerfilePath = layer.getDataSourceQuery().getQuery();
	
		
		
	}

	/**
	 * open the data of the layer selected in a dataset.
	 */
	public void openfile() {
		getfilePath();
		this.dataset = gdal.Open(LayerfilePath);
	}

	/**
	 * get the max and min coord of the full extension of a layer.
	 */
	public void getFullExtend() {
		this.RoiXmax = RasterXmax;
		this.RoiXmin = RasterXmin;
		this.RoiYmax = RasterYmax;
		this.RoiYmin = RasterYmin;
		dialog.getselectInputXUpperCorner().setText(
				String.valueOf(Math.floor(RasterXmin * 1000) / 1000));
		dialog.getselectInputYUpperCorner().setText(
				String.valueOf(Math.floor(RasterYmax * 1000) / 1000));
		dialog.getselectInputXDownCorner().setText(
				String.valueOf(Math.floor(RasterXmax * 1000) / 1000));
		dialog.getselectInputYDownCorner().setText(
				String.valueOf(Math.floor(RasterYmin * 1000) / 1000));
		getHmaxHmin();
	}

	/**
	 * get the max and min coord of a custom extension defined on layer.
	 * 
	 * @return
	 * @throws CheckExtension
	 */

	public void getCustomExtend() throws CheckExtension {
		List<Layer> layerlist = context.getLayerManager().getLayers();
		Collections.sort(layerlist);
		Layer[] layers = layerlist.toArray(new Layer[0]);

		Layer layer = (Layer) JOptionPane
				.showInputDialog(
						dialog,
						I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.Use-another-layer-extension"),
						"DEMTO3D",
						JOptionPane.QUESTION_MESSAGE,
						new ImageIcon(
								DemTo3DDialog.class
										.getResource("/org/saig/jump/images/demto3d/cursor_extension.png")),
						layers, layers[0]);

		if (layer != null) {
			Envelope roi = layer.getVista();
			Envelope raster = new Envelope(RasterXmin, RasterXmax, RasterYmax,
					RasterYmin);

			if (!raster.contains(roi)) {
				throw new CheckExtension();
			} else {
				this.RoiXmax = roi.getMaxX();
				this.RoiXmin = roi.getMinX();
				this.RoiYmax = roi.getMaxY();
				this.RoiYmin = roi.getMinY();

				dialog.getselectInputXUpperCorner().setText(
						String.valueOf(Math.floor(RoiXmin * 1000) / 1000));
				dialog.getselectInputYUpperCorner().setText(
						String.valueOf(Math.floor(RoiYmax * 1000) / 1000));
				dialog.getselectInputXDownCorner().setText(
						String.valueOf(Math.floor(RoiXmax * 1000) / 1000));
				dialog.getselectInputYDownCorner().setText(
						String.valueOf(Math.floor(RoiYmin * 1000) / 1000));
			}
			getHmaxHmin();
		}

	}

	/**
	 * get the spacing between stl points.
	 * 
	 * @return
	 */
	public void getSpacing() throws CheckSpacing {
		try {	
			this.spacing = Double.parseDouble(dialog.getcellSizeTextField()
					.getText());
			if (!projected){
				double w = Double.parseDouble(dialog.getWidthTextField()
						.getText());
				
				double aux =this.RoiXmax-this.RoiXmin;
				this.spac_aux = Double.parseDouble(dialog.getcellSizeTextField()
						.getText())*aux/w;
			}
		} catch (NumberFormatException e) {
			throw new CheckSpacing();
		}
	}

	/**
	 * get the Z scale of the model.
	 */
	public void getZscale() {
		float val = dialog.getslider().getValue();
		if (val <= 50) {
			val = val / 50;
		} else {
			val = val * 3 / 75 - 1;
		}
		this.zscale = val;
	}

	/**
	 * get minimum spacing.
	 */
	public void getMinSpace() {
		double min;
		if (projected){
			min = tamCell/scale;
		}else{
			double w = Double.parseDouble(dialog.getWidthTextField()
					.getText());
			double aux =this.RoiXmax-this.RoiXmin;
			min = tamCell*w/aux/1000;
		}
		if (min * 1000 < 0.2) {
			dialog.getRecomendedSpaceLbl()
					.setText(
							I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.minimum-recommended")
									+ " 0.2 mm");
		} else {
			dialog.getRecomendedSpaceLbl()
					.setText(
							I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.minimum-recommended")
									+ " "
									+ String.valueOf(Redondear(min * 1000, 2))
									+ " mm");
		}
	}

	/**
	 * get the dimensions and scale from height, width or scale .
	 */
	public void getDimensionFromHeight() throws CheckExtension {
		Envelope roi = new Envelope(RoiXmin, RoiXmax, RoiYmax, RoiYmin);
		Envelope raster = new Envelope(RasterXmin, RasterXmax, RasterYmax,
				RasterYmin);
		if (!raster.contains(roi)) {
			throw new CheckExtension();
		} else {
			double widthRoi = (RoiXmax - RoiXmin);
			double heightRoi = (RoiYmax - RoiYmin);

			if (projected){
				double height = Double.parseDouble(dialog.getHighTextField()
						.getText()) / 1000;
				this.high = height;
				double escale1 = (heightRoi / height);
				double width = widthRoi / escale1;
				this.width = width;
				double escale2 = (widthRoi / width);
				double escale = ((escale1 + escale2) / 2);
				this.scale = Redondear(escale, 6);
				dialog.getWidthTextField().setText(
						String.valueOf(Redondear(width * 1000, 2)));
				dialog.getscaleTextField().setText(String.valueOf((int) escale));
			}else{
				double h = Double.parseDouble(dialog.getHighTextField()
						.getText());
				this.high = h/1000;
				dialog.getWidthTextField().setText(
						String.valueOf(Redondear((widthRoi * h / heightRoi), 2)));
				double w = Double.parseDouble(dialog.getWidthTextField()
						.getText());
				this.width = w/1000;
				double Dist = widthRoi*Math.PI/180*Math.cos(RoiYmax*Math.PI/180)*6371000*1000;
				double escale = Dist/w;
				this.scale = Redondear(escale, 6);
				dialog.getscaleTextField().setText(String.valueOf((int) escale));
			}
		}
	}

	public void getDimensionFromWidth() throws CheckExtension {
		Envelope roi = new Envelope(RoiXmin, RoiXmax, RoiYmax, RoiYmin);
		Envelope raster = new Envelope(RasterXmin, RasterXmax, RasterYmax,
				RasterYmin);

		if (!raster.contains(roi)) {
			throw new CheckExtension();
		} else {
			double widthRoi = (RoiXmax - RoiXmin);
			double heightRoi = (RoiYmax - RoiYmin);
			
			if (projected){
				double width = Double.parseDouble(dialog.getWidthTextField()
						.getText()) / 1000;
				this.width = width;
				double escale1 = (widthRoi / width);
				double height = heightRoi / escale1;
				this.high = height;
				double escale2 = (heightRoi / height);

				double escale = ((escale1 + escale2) / 2);
				this.scale = Redondear(escale, 6);
				dialog.getHighTextField().setText(
						String.valueOf(Redondear(height * 1000, 2)));
				dialog.getscaleTextField().setText(String.valueOf((int) escale));
			}else{
				double w = Double.parseDouble(dialog.getWidthTextField()
						.getText());
				this.width = w/1000;
				dialog.getHighTextField().setText(
						String.valueOf(Redondear((heightRoi * w / widthRoi), 2)));
				this.high = Double.parseDouble(dialog.getHighTextField()
						.getText())/1000;
				double Dist = widthRoi*Math.PI/180*Math.cos(RoiYmax*Math.PI/180)*6371000*1000;
				double escale = Dist/w;
				this.scale = Redondear(escale, 6);
				dialog.getscaleTextField().setText(String.valueOf((int) escale));
			}
		}
	}

	public void getDimensionFromScale() throws CheckExtension {
		Envelope roi = new Envelope(RoiXmin, RoiXmax, RoiYmax, RoiYmin);
		Envelope raster = new Envelope(RasterXmin, RasterXmax, RasterYmax,
				RasterYmin);

		if (!raster.contains(roi)) {
			throw new CheckExtension();
		} else {
			double widthRoi = (RoiXmax - RoiXmin);
			double heightRoi = (RoiYmax - RoiYmin);

			if (projected){
				double scale = Double.parseDouble(dialog.getscaleTextField()
						.getText());
				this.scale = Redondear(scale, 6);
				double height = heightRoi / scale;
				this.high = height;
				double width = widthRoi / scale;
				this.width = width;
				dialog.getHighTextField().setText(
						String.valueOf(Redondear(height * 1000, 2)));
				dialog.getWidthTextField().setText(
						String.valueOf(Redondear(width * 1000, 2)));
			}else{
				double scale = Double.parseDouble(dialog.getscaleTextField()
						.getText());
				this.scale = Redondear(scale, 6);

				double Dist = widthRoi*Math.PI/180*Math.cos(RoiYmax*Math.PI/180)*6371000*1000;
				dialog.getWidthTextField().setText(
						String.valueOf(Redondear(Dist/scale, 2)));
				double w = Double.parseDouble(dialog.getWidthTextField()
						.getText());
				dialog.getHighTextField().setText(
						String.valueOf(Redondear((heightRoi * w / widthRoi), 2)));
				this.high = Double.parseDouble(dialog.getHighTextField()
						.getText())/1000; 
				this.width = w/1000; 
			}
		}
	}

	public void getHeightModel() throws CheckScale, CheckHbase {
		if (dialog.getscaleTextField().getText().length() == 0) {
			throw new CheckScale();
		} else if (dialog.getHeightTextField().getText().length() == 0) {
			throw new CheckHbase();
		} else {
			this.hbase = Double.parseDouble(dialog.getHeightTextField()
					.getText());
			if (hbase >= hmax) {
				throw new CheckHbase();
			} else {
				getZscale();
				dialog.getlabelHbaseModel()
						.setText(
								I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.height-model")
										+ "   "
										+ String.valueOf(Redondear(
												(hmax - hbase) / scale * 1000
														* zscale + 2, 1))
										+ " mm");
			}
		}
	}

	public static double Redondear(double numero, int decimales) {
		String val = numero + "";
		BigDecimal big = new BigDecimal(val);
		big = big.setScale(decimales, RoundingMode.HALF_UP);
		return big.doubleValue();
	}

	public static double Redondearmas(double numero, int decimales) {
		String val = numero + "";
		BigDecimal big = new BigDecimal(val);
		big = big.setScale(decimales, RoundingMode.UP);
		return big.doubleValue();
	}

	public static double Redondearmenos(double numero, int decimales) {
		String val = numero + "";
		BigDecimal big = new BigDecimal(val);
		big = big.setScale(decimales, RoundingMode.DOWN);
		return big.doubleValue();
	}

	@Override
	public void update(Observable o, Object arg) {
		JOptionPane
				.showMessageDialog(
						null,
						I18N.getString("org.saig.jump.controller.demto3d.DemTo3DController.file-exported"),
						"DEMTO3D", JOptionPane.INFORMATION_MESSAGE);
	}
}