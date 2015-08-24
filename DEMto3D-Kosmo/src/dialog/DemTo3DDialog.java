package org.saig.jump.dialog.demto3d;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import java.awt.Toolkit;
import java.util.Hashtable;

import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSlider;
import javax.swing.JTextField;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.border.TitledBorder;

import org.saig.jump.lang.I18N;
import java.awt.FlowLayout;
import java.awt.Dimension;

public class DemTo3DDialog extends javax.swing.JFrame {

	// INPUT LAYER OPTIONS
	private JLabel inputLayerLabel;
	private JComboBox selectInputLayerComboBox;

	// EXTENSION OPTIONS
	private JPanel extensionOptionPanel;
	private JLabel lblUpperCorner;
	private JLabel lblDownCorner;
	private JLabel lbl_1X;
	private JTextField selectInputXUpperCorner;
	private JLabel lbl_1Y;
	private JTextField selectInputYUpperCorner;
	private JLabel lbl_2X;
	private JTextField selectInputXDownCorner;
	private JLabel lbl_2Y;
	private JTextField selectInputYDownCorner;
	private JButton selectCustomExtension;
	private JButton selectFullExtension;

	// RESOLUTION OPTIONS
	private JPanel resolutionOptionPanel;
	private JLabel lblPrinterSettings;
	private JComboBox PrintSettingComboBox;
	private JButton selectPrinter;
	private JLabel TamaoCeldaLabel;
	private JTextField cellSizeTextField;
	private JLabel lblRecomendadoMayorA;
	private JLabel DimensionesLabel;
	private JLabel lblAlto;
	private JTextField HighTextField;
	private JLabel lblAncho;
	private JTextField WidthTextField;
	private JLabel lblEscala;
	private JLabel escaleLabel;
	private JTextField scaleTextField;

	// ELEVATION OPTIONS
	private JPanel SmothOptionPanel;
	private JLabel lblSuavizado;
	private JSlider slider;
	private JLabel lblExageracin;

	// HEIGHT BASE OPTION
	private JPanel HeightBaseOptionPanel;
	private JLabel lblCotam;
	private JTextField HeightTextField;
	private JLabel lblHmodel;
	private JLabel labelMaxH;
	private JLabel labelMinH;

	// OTHERS OPTIONS
	private JPanel othersParametersOpctionPanel;
	private JCheckBox chckbxZInverse;

	// MAIN BUTTONS
	private JButton btnAceptar;
	private JButton btnCancelar;
	private JButton btnAyuda;
	private JButton btnExportStl;

	public DemTo3DDialog() {
		initComponents();
	}

	private void initComponents() {
		setTitle(I18N
				.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.title"));
		setResizable(false);
		setIconImage(Toolkit
				.getDefaultToolkit()
				.getImage(
						DemTo3DDialog.class
								.getResource("/org/saig/jump/images/demto3d/stl_icon.png")));

		inputLayerLabel = new JLabel(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.Select-layer-to-print"));

		selectInputLayerComboBox = new JComboBox();

		extensionOptionPanel = new JPanel();
		extensionOptionPanel
				.setBorder(new TitledBorder(
						UIManager.getBorder("TitledBorder.border"),
						I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.Select-area-to-print"),
						TitledBorder.LEADING, TitledBorder.TOP, null,
						new Color(0, 0, 0)));

		resolutionOptionPanel = new JPanel();
		resolutionOptionPanel
				.setBorder(new TitledBorder(
						UIManager.getBorder("TitledBorder.border"),
						I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.Select-print-resolution"),
						TitledBorder.LEADING, TitledBorder.TOP, null,
						new Color(0, 0, 0)));

		SmothOptionPanel = new JPanel();
		SmothOptionPanel
				.setBorder(new TitledBorder(
						UIManager.getBorder("TitledBorder.border"),
						I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.exaggeration-smoothing-terrain"),
						TitledBorder.LEADING, TitledBorder.TOP, null, null));

		HeightBaseOptionPanel = new JPanel();
		HeightBaseOptionPanel
				.setBorder(new TitledBorder(
						null,
						I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.select-height-base"),
						TitledBorder.LEADING, TitledBorder.TOP, null, null));

		othersParametersOpctionPanel = new JPanel();
		othersParametersOpctionPanel
				.setBorder(new TitledBorder(
						UIManager.getBorder("TitledBorder.border"),
						I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.other-parameters"),
						TitledBorder.LEADING, TitledBorder.TOP, null, null));

		btnAceptar = new JButton(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.print"));

		btnCancelar = new JButton(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.cancel"));

		btnAyuda = new JButton(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.help"));

		btnExportStl = new JButton(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.stl-export"));

		GroupLayout groupLayout = new GroupLayout(getContentPane());
		groupLayout
				.setHorizontalGroup(groupLayout
						.createParallelGroup(Alignment.LEADING)
						.addGroup(
								groupLayout
										.createSequentialGroup()
										.addGroup(
												groupLayout
														.createParallelGroup(
																Alignment.LEADING,
																false)
														.addGroup(
																groupLayout
																		.createSequentialGroup()
																		.addContainerGap()
																		.addComponent(
																				inputLayerLabel,
																				GroupLayout.PREFERRED_SIZE,
																				404,
																				GroupLayout.PREFERRED_SIZE))
														.addGroup(
																groupLayout
																		.createSequentialGroup()
																		.addGap(10)
																		.addGroup(
																				groupLayout
																						.createParallelGroup(
																								Alignment.LEADING,
																								false)
																						.addComponent(
																								selectInputLayerComboBox,
																								GroupLayout.PREFERRED_SIZE,
																								404,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								extensionOptionPanel,
																								GroupLayout.PREFERRED_SIZE,
																								404,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								resolutionOptionPanel,
																								GroupLayout.PREFERRED_SIZE,
																								404,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								SmothOptionPanel,
																								GroupLayout.PREFERRED_SIZE,
																								404,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								HeightBaseOptionPanel,
																								GroupLayout.PREFERRED_SIZE,
																								404,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								othersParametersOpctionPanel,
																								GroupLayout.PREFERRED_SIZE,
																								404,
																								GroupLayout.PREFERRED_SIZE)))
														.addGroup(
																groupLayout
																		.createSequentialGroup()
																		.addContainerGap()
																		.addComponent(
																				btnAceptar,
																				GroupLayout.PREFERRED_SIZE,
																				80,
																				GroupLayout.PREFERRED_SIZE)
																		.addPreferredGap(
																				ComponentPlacement.UNRELATED)
																		.addComponent(
																				btnCancelar,
																				GroupLayout.PREFERRED_SIZE,
																				80,
																				GroupLayout.PREFERRED_SIZE)
																		.addPreferredGap(
																				ComponentPlacement.UNRELATED)
																		.addComponent(
																				btnAyuda,
																				GroupLayout.PREFERRED_SIZE,
																				80,
																				GroupLayout.PREFERRED_SIZE)
																		.addPreferredGap(
																				ComponentPlacement.RELATED,
																				GroupLayout.DEFAULT_SIZE,
																				Short.MAX_VALUE)
																		.addComponent(
																				btnExportStl,
																				GroupLayout.PREFERRED_SIZE,
																				110,
																				GroupLayout.PREFERRED_SIZE)))
										.addContainerGap()));
		groupLayout.setVerticalGroup(groupLayout.createParallelGroup(
				Alignment.LEADING)
				.addGroup(
						groupLayout
								.createSequentialGroup()
								.addContainerGap()
								.addComponent(inputLayerLabel)
								.addPreferredGap(ComponentPlacement.RELATED)
								.addComponent(selectInputLayerComboBox,
										GroupLayout.PREFERRED_SIZE,
										GroupLayout.DEFAULT_SIZE,
										GroupLayout.PREFERRED_SIZE)
								.addGap(11)
								.addComponent(extensionOptionPanel,
										GroupLayout.PREFERRED_SIZE, 110,
										GroupLayout.PREFERRED_SIZE)
								.addGap(11)
								.addComponent(resolutionOptionPanel,
										GroupLayout.PREFERRED_SIZE, 123,
										GroupLayout.PREFERRED_SIZE)
								.addGap(11)
								.addComponent(SmothOptionPanel,
										GroupLayout.PREFERRED_SIZE, 80,
										GroupLayout.PREFERRED_SIZE)
								.addGap(11)
								.addComponent(HeightBaseOptionPanel,
										GroupLayout.PREFERRED_SIZE, 68,
										GroupLayout.PREFERRED_SIZE)
								.addGap(11)
								.addComponent(othersParametersOpctionPanel,
										GroupLayout.PREFERRED_SIZE, 52,
										GroupLayout.PREFERRED_SIZE)
								.addPreferredGap(ComponentPlacement.RELATED,
										18, Short.MAX_VALUE)
								.addGroup(
										groupLayout
												.createParallelGroup(
														Alignment.BASELINE)
												.addComponent(btnAceptar)
												.addComponent(btnCancelar)
												.addComponent(btnAyuda)
												.addComponent(btnExportStl))
								.addGap(12)));
		groupLayout.linkSize(SwingConstants.VERTICAL, new Component[] {
				btnAceptar, btnCancelar, btnAyuda, btnExportStl });
		groupLayout.linkSize(SwingConstants.HORIZONTAL, new Component[] {
				btnAceptar, btnCancelar, btnAyuda });
		groupLayout.linkSize(SwingConstants.HORIZONTAL, new Component[] {
				inputLayerLabel, selectInputLayerComboBox,
				extensionOptionPanel, resolutionOptionPanel, SmothOptionPanel,
				HeightBaseOptionPanel, othersParametersOpctionPanel });

		// lblCotam = new JLabel("Cota (m):");
		lblCotam = new JLabel(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.height"));

		HeightTextField = new JTextField();
		HeightTextField.setColumns(10);

		// lblHmodel = new JLabel("Altura del modelo: ");
		lblHmodel = new JLabel(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.height-model"));

		// labelMaxH = new JLabel("Cota m\u00E1x: ");
		labelMaxH = new JLabel(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.max-height"));
		labelMaxH.setForeground(Color.GRAY);

		// labelMinH = new JLabel("Cota m\u00EDn: ");
		labelMinH = new JLabel(
				I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.min-height"));
		labelMinH.setForeground(Color.GRAY);

		GroupLayout gl_HeightBaseOptionPanel = new GroupLayout(
				HeightBaseOptionPanel);
		gl_HeightBaseOptionPanel.setHorizontalGroup(
			gl_HeightBaseOptionPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_HeightBaseOptionPanel.createSequentialGroup()
					.addContainerGap()
					.addGroup(gl_HeightBaseOptionPanel.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_HeightBaseOptionPanel.createSequentialGroup()
							.addComponent(lblCotam, GroupLayout.PREFERRED_SIZE, 61, GroupLayout.PREFERRED_SIZE)
							.addPreferredGap(ComponentPlacement.RELATED)
							.addComponent(HeightTextField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
						.addComponent(lblHmodel, GroupLayout.PREFERRED_SIZE, 181, GroupLayout.PREFERRED_SIZE))
					.addGap(29)
					.addGroup(gl_HeightBaseOptionPanel.createParallelGroup(Alignment.LEADING)
						.addComponent(labelMaxH, 0, 0, Short.MAX_VALUE)
						.addComponent(labelMinH, GroupLayout.PREFERRED_SIZE, 162, Short.MAX_VALUE))
					.addContainerGap())
		);
		gl_HeightBaseOptionPanel.setVerticalGroup(
			gl_HeightBaseOptionPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_HeightBaseOptionPanel.createSequentialGroup()
					.addGroup(gl_HeightBaseOptionPanel.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblCotam)
						.addComponent(HeightTextField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
						.addComponent(labelMaxH, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE))
					.addPreferredGap(ComponentPlacement.RELATED)
					.addGroup(gl_HeightBaseOptionPanel.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblHmodel)
						.addComponent(labelMinH))
					.addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
		);
		gl_HeightBaseOptionPanel.linkSize(SwingConstants.VERTICAL, new Component[] {lblCotam, HeightTextField, lblHmodel, labelMaxH, labelMinH});
		HeightBaseOptionPanel.setLayout(gl_HeightBaseOptionPanel);
		othersParametersOpctionPanel.setLayout(new FlowLayout(
				FlowLayout.LEADING, 5, 5));

		//chckbxZInverse = new JCheckBox("Inversión del relieve");
		 chckbxZInverse = new JCheckBox(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.topographic-inversion"));

		othersParametersOpctionPanel.add(chckbxZInverse);
		
		//lblSuavizado = new JLabel("Suavizado");
		 lblSuavizado = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.smoothing"));
		 lblSuavizado.setHorizontalTextPosition(SwingConstants.RIGHT);
		SmothOptionPanel.add(lblSuavizado);

		slider = new JSlider(JSlider.HORIZONTAL, 0, 100, 50);
		slider.setPreferredSize(new Dimension(250, 50));
		slider.setSize(new Dimension(300, 50));

		SmothOptionPanel.add(slider);

		slider.setMajorTickSpacing((int) 5);
		slider.setPaintTicks(true);

		Hashtable<Integer, JLabel> labelTable = new Hashtable<Integer, JLabel>();
		labelTable.put(new Integer(0), new JLabel("0"));
		labelTable.put(new Integer(25), new JLabel("0.5"));
		labelTable.put(new Integer(50), new JLabel("1"));
		labelTable.put(new Integer(75), new JLabel("2"));
		labelTable.put(new Integer(100), new JLabel("3"));
		slider.setLabelTable(labelTable);
		slider.setPaintLabels(true);

		//lblExageracin = new JLabel("Exagerado");
		 lblExageracin = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.exaggeration"));
		 lblExageracin.setHorizontalTextPosition(SwingConstants.LEFT);
		SmothOptionPanel.add(lblExageracin);

		//lblPrinterSettings = new JLabel("Parámetros impresora:");
		 lblPrinterSettings = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.printer-settings"));

		PrintSettingComboBox = new JComboBox();

		selectPrinter = new JButton("");

		selectPrinter
				.setToolTipText(I18N
						.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.slicer"));
		selectPrinter
				.setIcon(new ImageIcon(
						DemTo3DDialog.class
								.getResource("/com/vividsolutions/jump/workbench/ui/images/BigWrench.gif")));

		//TamaoCeldaLabel = new JLabel("Espaciado (mm):");
		 TamaoCeldaLabel = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.spacing"));

		cellSizeTextField = new JTextField();
		cellSizeTextField.setColumns(10);

		//lblRecomendadoMayorA = new JLabel("recomendado mayor de" + " 0.2 mm");
		 lblRecomendadoMayorA = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.minimum-recommended")
		 + " 0.2 mm");
		lblRecomendadoMayorA
				.setToolTipText(I18N
						.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.minimum-recommended-tip"));
		lblRecomendadoMayorA.setForeground(Color.GRAY);
		lblRecomendadoMayorA.setFont(new Font("Tahoma", Font.PLAIN, 10));

		//DimensionesLabel = new JLabel("Dimensiones (mm):");
		 DimensionesLabel = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.size"));

		//lblAlto = new JLabel("Alto:");
		 lblAlto = new JLabel(
		I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.high"));
		 lblAlto.setHorizontalAlignment(SwingConstants.RIGHT);

		HighTextField = new JTextField();
		HighTextField.setColumns(10);

		//lblAncho = new JLabel("Ancho:");
		
		 lblAncho = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.width"));
		 lblAncho.setHorizontalAlignment(SwingConstants.RIGHT);

		WidthTextField = new JTextField();
		WidthTextField.setColumns(10);

		//lblEscala = new JLabel("Escala:");
		 lblEscala = new JLabel(
		 I18N.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.scale"));

		escaleLabel = new JLabel("1:");

		scaleTextField = new JTextField();
		scaleTextField.setColumns(10);

		GroupLayout gl_resolutionOptionPanel = new GroupLayout(
				resolutionOptionPanel);
		gl_resolutionOptionPanel.setHorizontalGroup(
			gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
					.addContainerGap()
					.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
							.addComponent(lblPrinterSettings, GroupLayout.PREFERRED_SIZE, 118, GroupLayout.PREFERRED_SIZE)
							.addPreferredGap(ComponentPlacement.UNRELATED)
							.addComponent(PrintSettingComboBox, GroupLayout.PREFERRED_SIZE, 206, GroupLayout.PREFERRED_SIZE)
							.addPreferredGap(ComponentPlacement.UNRELATED)
							.addComponent(selectPrinter, GroupLayout.PREFERRED_SIZE, 25, GroupLayout.PREFERRED_SIZE))
						.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
							.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING)
								.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.TRAILING, false)
									.addComponent(DimensionesLabel, 0, 0, Short.MAX_VALUE)
									.addComponent(TamaoCeldaLabel, GroupLayout.PREFERRED_SIZE, 100, GroupLayout.PREFERRED_SIZE))
								.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
									.addComponent(lblEscala, GroupLayout.PREFERRED_SIZE, 69, GroupLayout.PREFERRED_SIZE)
									.addGap(18)
									.addComponent(escaleLabel, GroupLayout.PREFERRED_SIZE, 10, GroupLayout.PREFERRED_SIZE)))
							.addPreferredGap(ComponentPlacement.RELATED)
							.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING)
								.addComponent(scaleTextField, GroupLayout.PREFERRED_SIZE, 61, GroupLayout.PREFERRED_SIZE)
								.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING)
									.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
										.addComponent(cellSizeTextField, GroupLayout.PREFERRED_SIZE, 57, GroupLayout.PREFERRED_SIZE)
										.addGap(18)
										.addComponent(lblRecomendadoMayorA, GroupLayout.PREFERRED_SIZE, 175, Short.MAX_VALUE))
									.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
										.addComponent(lblAlto, GroupLayout.PREFERRED_SIZE, 52, GroupLayout.PREFERRED_SIZE)
										.addPreferredGap(ComponentPlacement.RELATED)
										.addComponent(HighTextField, GroupLayout.PREFERRED_SIZE, 70, GroupLayout.PREFERRED_SIZE)
										.addPreferredGap(ComponentPlacement.UNRELATED)
										.addComponent(lblAncho, GroupLayout.PREFERRED_SIZE, 36, GroupLayout.PREFERRED_SIZE)
										.addPreferredGap(ComponentPlacement.RELATED)
										.addComponent(WidthTextField, GroupLayout.PREFERRED_SIZE, 51, GroupLayout.PREFERRED_SIZE))))))
					.addGap(13))
		);
		gl_resolutionOptionPanel.setVerticalGroup(
			gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
					.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.TRAILING)
						.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.BASELINE)
							.addComponent(lblPrinterSettings, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE)
							.addComponent(PrintSettingComboBox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
						.addComponent(selectPrinter, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE))
					.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING, false)
						.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
							.addGap(30)
							.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.BASELINE)
								.addComponent(DimensionesLabel)
								.addComponent(HighTextField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
								.addComponent(lblAlto)
								.addComponent(WidthTextField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
								.addComponent(lblAncho)))
						.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
							.addPreferredGap(ComponentPlacement.RELATED)
							.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.BASELINE, false)
								.addComponent(TamaoCeldaLabel, GroupLayout.PREFERRED_SIZE, 20, GroupLayout.PREFERRED_SIZE)
								.addComponent(cellSizeTextField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
								.addComponent(lblRecomendadoMayorA))))
					.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
							.addGap(4)
							.addGroup(gl_resolutionOptionPanel.createParallelGroup(Alignment.BASELINE)
								.addComponent(lblEscala)
								.addComponent(escaleLabel)))
						.addGroup(gl_resolutionOptionPanel.createSequentialGroup()
							.addPreferredGap(ComponentPlacement.RELATED)
							.addComponent(scaleTextField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)))
					.addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
		);
		gl_resolutionOptionPanel.linkSize(SwingConstants.VERTICAL, new Component[] {lblPrinterSettings, PrintSettingComboBox, selectPrinter, TamaoCeldaLabel, cellSizeTextField, lblRecomendadoMayorA, DimensionesLabel, lblAlto, HighTextField, lblAncho, WidthTextField, lblEscala, escaleLabel, scaleTextField});
		gl_resolutionOptionPanel.linkSize(SwingConstants.HORIZONTAL, new Component[] {lblAlto, lblAncho});
		gl_resolutionOptionPanel.linkSize(SwingConstants.HORIZONTAL, new Component[] {cellSizeTextField, HighTextField, WidthTextField, scaleTextField});
		resolutionOptionPanel.setLayout(gl_resolutionOptionPanel);

		lblUpperCorner = new JLabel("");
		lblUpperCorner.setIcon(new ImageIcon(DemTo3DDialog.class
				.getResource("/org/saig/jump/images/demto3d/uppcorner.png")));

		lblDownCorner = new JLabel("");
		lblDownCorner.setIcon(new ImageIcon(DemTo3DDialog.class
				.getResource("/org/saig/jump/images/demto3d/downcorner.png")));

		lbl_1X = new JLabel("X:");

		selectInputXUpperCorner = new JTextField();
		selectInputXUpperCorner.setColumns(10);

		lbl_1Y = new JLabel("Y:");

		selectInputYUpperCorner = new JTextField();
		selectInputYUpperCorner.setColumns(10);

		lbl_2X = new JLabel("X:");

		selectInputXDownCorner = new JTextField();
		selectInputXDownCorner.setColumns(10);

		lbl_2Y = new JLabel("Y:");

		selectInputYDownCorner = new JTextField();
		selectInputYDownCorner.setColumns(10);

		selectCustomExtension = new JButton("");
		selectCustomExtension
				.setToolTipText(I18N
						.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.Use-extension-from-other-layer"));
		selectCustomExtension
				.setIcon(new ImageIcon(
						DemTo3DDialog.class
								.getResource("/org/saig/jump/images/demto3d/cursor_extension.png")));

		selectFullExtension = new JButton("");
		selectFullExtension
				.setToolTipText(I18N
						.getString("org.saig.jump.dialog.demto3d.DemTo3DDialog.Use-extension-from-layer"));
		selectFullExtension
				.setIcon(new ImageIcon(
						DemTo3DDialog.class
								.getResource("/com/vividsolutions/jump/workbench/ui/images/SmallWorld.gif")));

		GroupLayout gl_extensionOptionPanel = new GroupLayout(
				extensionOptionPanel);
		gl_extensionOptionPanel
				.setHorizontalGroup(gl_extensionOptionPanel
						.createParallelGroup(Alignment.LEADING)
						.addGroup(
								gl_extensionOptionPanel
										.createSequentialGroup()
										.addGap(12)
										.addGroup(
												gl_extensionOptionPanel
														.createParallelGroup(
																Alignment.TRAILING)
														.addGroup(
																gl_extensionOptionPanel
																		.createSequentialGroup()
																		.addComponent(
																				selectFullExtension,
																				GroupLayout.PREFERRED_SIZE,
																				25,
																				GroupLayout.PREFERRED_SIZE)
																		.addPreferredGap(
																				ComponentPlacement.RELATED)
																		.addComponent(
																				selectCustomExtension,
																				GroupLayout.PREFERRED_SIZE,
																				25,
																				GroupLayout.PREFERRED_SIZE)
																		.addGap(12))
														.addGroup(
																gl_extensionOptionPanel
																		.createSequentialGroup()
																		.addGroup(
																				gl_extensionOptionPanel
																						.createParallelGroup(
																								Alignment.LEADING,
																								false)
																						.addGroup(
																								gl_extensionOptionPanel
																										.createSequentialGroup()
																										.addComponent(
																												lblUpperCorner)
																										.addGap(21)
																										.addComponent(
																												lbl_1X))
																						.addGroup(
																								gl_extensionOptionPanel
																										.createSequentialGroup()
																										.addComponent(
																												lblDownCorner,
																												GroupLayout.PREFERRED_SIZE,
																												20,
																												GroupLayout.PREFERRED_SIZE)
																										.addPreferredGap(
																												ComponentPlacement.RELATED,
																												GroupLayout.DEFAULT_SIZE,
																												Short.MAX_VALUE)
																										.addComponent(
																												lbl_2X,
																												GroupLayout.PREFERRED_SIZE,
																												10,
																												GroupLayout.PREFERRED_SIZE)))
																		.addPreferredGap(
																				ComponentPlacement.RELATED)
																		.addGroup(
																				gl_extensionOptionPanel
																						.createParallelGroup(
																								Alignment.TRAILING)
																						.addComponent(
																								selectInputXUpperCorner,
																								GroupLayout.PREFERRED_SIZE,
																								140,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								selectInputXDownCorner,
																								GroupLayout.PREFERRED_SIZE,
																								140,
																								GroupLayout.PREFERRED_SIZE))
																		.addGap(18)
																		.addGroup(
																				gl_extensionOptionPanel
																						.createParallelGroup(
																								Alignment.LEADING)
																						.addGroup(
																								gl_extensionOptionPanel
																										.createSequentialGroup()
																										.addComponent(
																												lbl_1Y,
																												GroupLayout.PREFERRED_SIZE,
																												10,
																												GroupLayout.PREFERRED_SIZE)
																										.addPreferredGap(
																												ComponentPlacement.RELATED)
																										.addComponent(
																												selectInputYUpperCorner,
																												GroupLayout.PREFERRED_SIZE,
																												140,
																												GroupLayout.PREFERRED_SIZE))
																						.addGroup(
																								gl_extensionOptionPanel
																										.createSequentialGroup()
																										.addComponent(
																												lbl_2Y,
																												GroupLayout.PREFERRED_SIZE,
																												10,
																												GroupLayout.PREFERRED_SIZE)
																										.addPreferredGap(
																												ComponentPlacement.RELATED)
																										.addComponent(
																												selectInputYDownCorner,
																												GroupLayout.PREFERRED_SIZE,
																												140,
																												GroupLayout.PREFERRED_SIZE)))))
										.addContainerGap(13, Short.MAX_VALUE)));
		gl_extensionOptionPanel
				.setVerticalGroup(gl_extensionOptionPanel
						.createParallelGroup(Alignment.LEADING)
						.addGroup(
								gl_extensionOptionPanel
										.createSequentialGroup()
										.addGroup(
												gl_extensionOptionPanel
														.createParallelGroup(
																Alignment.LEADING)
														.addGroup(
																gl_extensionOptionPanel
																		.createSequentialGroup()
																		.addComponent(
																				lblUpperCorner)
																		.addPreferredGap(
																				ComponentPlacement.RELATED)
																		.addComponent(
																				lblDownCorner))
														.addGroup(
																gl_extensionOptionPanel
																		.createSequentialGroup()
																		.addGroup(
																				gl_extensionOptionPanel
																						.createParallelGroup(
																								Alignment.BASELINE)
																						.addComponent(
																								lbl_1Y,
																								GroupLayout.PREFERRED_SIZE,
																								20,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								selectInputYUpperCorner,
																								GroupLayout.PREFERRED_SIZE,
																								GroupLayout.DEFAULT_SIZE,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								selectInputXUpperCorner,
																								GroupLayout.PREFERRED_SIZE,
																								GroupLayout.DEFAULT_SIZE,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								lbl_1X,
																								GroupLayout.PREFERRED_SIZE,
																								20,
																								GroupLayout.PREFERRED_SIZE))
																		.addPreferredGap(
																				ComponentPlacement.RELATED)
																		.addGroup(
																				gl_extensionOptionPanel
																						.createParallelGroup(
																								Alignment.BASELINE)
																						.addComponent(
																								selectInputXDownCorner,
																								GroupLayout.PREFERRED_SIZE,
																								GroupLayout.DEFAULT_SIZE,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								lbl_2X,
																								GroupLayout.PREFERRED_SIZE,
																								20,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								lbl_2Y,
																								GroupLayout.PREFERRED_SIZE,
																								20,
																								GroupLayout.PREFERRED_SIZE)
																						.addComponent(
																								selectInputYDownCorner,
																								GroupLayout.PREFERRED_SIZE,
																								GroupLayout.DEFAULT_SIZE,
																								GroupLayout.PREFERRED_SIZE))))
										.addPreferredGap(
												ComponentPlacement.UNRELATED)
										.addGroup(
												gl_extensionOptionPanel
														.createParallelGroup(
																Alignment.LEADING)
														.addComponent(
																selectFullExtension)
														.addComponent(
																selectCustomExtension,
																GroupLayout.PREFERRED_SIZE,
																25,
																GroupLayout.PREFERRED_SIZE))
										.addContainerGap(
												GroupLayout.DEFAULT_SIZE,
												Short.MAX_VALUE)));
		gl_extensionOptionPanel.linkSize(SwingConstants.VERTICAL,
				new Component[] { selectCustomExtension, selectFullExtension });
		gl_extensionOptionPanel
				.linkSize(SwingConstants.VERTICAL,
						new Component[] { lblUpperCorner, lblDownCorner,
								lbl_1X, selectInputXUpperCorner, lbl_1Y,
								selectInputYUpperCorner, lbl_2X,
								selectInputXDownCorner, lbl_2Y,
								selectInputYDownCorner });
		gl_extensionOptionPanel.linkSize(SwingConstants.HORIZONTAL,
				new Component[] { selectCustomExtension, selectFullExtension });
		gl_extensionOptionPanel.linkSize(SwingConstants.HORIZONTAL,
				new Component[] { selectInputXUpperCorner,
						selectInputYUpperCorner, selectInputXDownCorner,
						selectInputYDownCorner });
		gl_extensionOptionPanel.linkSize(SwingConstants.HORIZONTAL,
				new Component[] { lbl_1X, lbl_1Y, lbl_2X, lbl_2Y });
		gl_extensionOptionPanel.linkSize(SwingConstants.HORIZONTAL,
				new Component[] { lblUpperCorner, lblDownCorner });
		extensionOptionPanel.setLayout(gl_extensionOptionPanel);
		getContentPane().setLayout(groupLayout);
		pack();
	}

	// **************************INPUT LAYER OPTIONS************************//
	/**
	 * @return Returns the selectInputLayerComboBox.
	 */
	public JComboBox getselectInputLayerComboBox() {
		return selectInputLayerComboBox;
	}

	/**
	 * @return Returns the selectInputXUpperCorner.
	 */
	public JTextField getselectInputXUpperCorner() {
		return selectInputXUpperCorner;
	}

	/**
	 * @return Returns the selectInputYUpperCorner.
	 */
	public JTextField getselectInputYUpperCorner() {
		return selectInputYUpperCorner;
	}

	/**
	 * @return Returns the selectInputYDownCorner.
	 */
	public JTextField getselectInputYDownCorner() {
		return selectInputYDownCorner;
	}

	/**
	 * @return Returns the selectInputXDownCorner.
	 */
	public JTextField getselectInputXDownCorner() {
		return selectInputXDownCorner;
	}

	/**
	 * @return Returns the selectFullExtension.
	 */
	public JButton getselectFullExtension() {
		return selectFullExtension;
	}

	/**
	 * @return Returns the selectCustomExtension.
	 */
	public JButton getselectCustomExtension() {
		return selectCustomExtension;
	}

	// **************************RESOLUTION OPTIONS************************//

	/**
	 * @return Returns the selectInputInterpMethodComboBox.
	 */
	public JComboBox getPrintSettingComboBox() {
		return PrintSettingComboBox;
	}

	/**
	 * @return Returns the recommended spacing.
	 */
	public JLabel getRecomendedSpaceLbl() {
		return lblRecomendadoMayorA;
	}

	/**
	 * @return Returns the selectPrinter.
	 */
	public JButton getSelectPrinter() {
		return selectPrinter;
	}

	/**
	 * @return Returns the cellSizeTextField.
	 */
	public JTextField getcellSizeTextField() {
		return cellSizeTextField;
	}

	/**
	 * @return Returns the HighTextField.
	 */
	public JTextField getHighTextField() {
		return HighTextField;
	}

	/**
	 * @return Returns the WidthTextField.
	 */
	public JTextField getWidthTextField() {
		return WidthTextField;
	}

	/**
	 * @return Returns the scaleTextField.
	 */
	public JTextField getscaleTextField() {
		return scaleTextField;
	}

	// **************************ELEVATION OPTIONS************************//

	/**
	 * @return Returns the slider.
	 */
	public JSlider getslider() {
		return slider;
	}

	// **************************HEIGHT BASE OPTIONS************************//

	public JLabel getlabelMaxH() {
		return labelMaxH;
	}

	public JLabel getlabelMinH() {
		return labelMinH;
	}

	public JTextField getHeightTextField() {
		return HeightTextField;
	}

	public JLabel getlabelHbaseModel() {
		return lblHmodel;
	}

	// **************************OTHERS OPTIONS************************//

	/**
	 * @return Returns the chckbxInversinDelRelieve.
	 */
	public JCheckBox getchckbxZinverse() {
		return chckbxZInverse;
	}

	public JButton getbtnExportStl() {
		return btnExportStl;
	}

	/**
	 * @return Returns the Help,OK,cancel buttons.
	 */
	public JButton getbtnAyuda() {
		return btnAyuda;
	}

	public JButton getbtnAceptar() {
		return btnAceptar;
	}

	public JButton getbtnCancelar() {
		return btnCancelar;
	}
}
