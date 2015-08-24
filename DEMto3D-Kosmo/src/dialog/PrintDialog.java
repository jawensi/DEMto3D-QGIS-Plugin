package org.saig.jump.dialog.demto3d;

import java.awt.Component;
import java.awt.Dimension;
import java.awt.Toolkit;

import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JTextArea;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.SwingConstants;
import javax.swing.JScrollPane;
import javax.swing.text.DefaultCaret;

import org.saig.jump.lang.I18N;

import java.awt.Font;

public class PrintDialog extends javax.swing.JFrame{
	private JLabel lblNewLabel;
	private JLabel lblNewLabel_1;
	private JComboBox PrintingComboBox;
	private JComboBox FilamentComboBox;
	private JButton btnImprimir;
	private JButton btnPausar;
	private JButton btnCancelar;
	private JScrollPane scrollPane;
	private JTextArea textArea;
	private JButton btnConectar;
	private JComboBox PortcomboBox;
	private JButton btnTemperatura;
	
	public PrintDialog() {
		initComponents();
	}
	
	private void initComponents() {
		setResizable(false);
		

		setPreferredSize(new Dimension(340, 320));
		setTitle(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.title"));
		setIconImage(Toolkit
				.getDefaultToolkit()
				.getImage(
						DemTo3DDialog.class
								.getResource("/org/saig/jump/images/demto3d/stl_icon.png")));
		
		lblNewLabel = new JLabel(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.print-settings"));
		
		lblNewLabel_1 = new JLabel(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.filament-settings"));
		
		PrintingComboBox = new JComboBox();

		
		FilamentComboBox = new JComboBox();

		
		btnImprimir = new JButton(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.print"));
		
		btnPausar = new JButton(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.pause"));

		btnCancelar = new JButton(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.cancel"));
		
		scrollPane = new JScrollPane();
		scrollPane.setAutoscrolls(true);
		
		
		btnConectar = new JButton(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.connect"));
		btnConectar.setSize(new Dimension(115, 23));
		
		PortcomboBox = new JComboBox();
		
		btnTemperatura = new JButton(I18N.getString("org.saig.jump.dialog.demto3d.PrintDialog.check-temp"));
	
		GroupLayout groupLayout = new GroupLayout(getContentPane());
		groupLayout.setHorizontalGroup(
			groupLayout.createParallelGroup(Alignment.LEADING)
				.addGroup(groupLayout.createSequentialGroup()
					.addGroup(groupLayout.createParallelGroup(Alignment.LEADING)
						.addGroup(Alignment.TRAILING, groupLayout.createSequentialGroup()
							.addContainerGap()
							.addGroup(groupLayout.createParallelGroup(Alignment.LEADING)
								.addGroup(groupLayout.createSequentialGroup()
									.addComponent(lblNewLabel, GroupLayout.PREFERRED_SIZE, 112, GroupLayout.PREFERRED_SIZE)
									.addGap(18)
									.addComponent(PrintingComboBox, 0, 176, Short.MAX_VALUE))
								.addGroup(groupLayout.createSequentialGroup()
									.addComponent(lblNewLabel_1, GroupLayout.PREFERRED_SIZE, 120, GroupLayout.PREFERRED_SIZE)
									.addGap(18)
									.addComponent(FilamentComboBox, 0, 176, Short.MAX_VALUE))))
						.addGroup(Alignment.TRAILING, groupLayout.createSequentialGroup()
							.addContainerGap()
							.addComponent(scrollPane, GroupLayout.DEFAULT_SIZE, 314, Short.MAX_VALUE))
						.addGroup(Alignment.TRAILING, groupLayout.createSequentialGroup()
							.addContainerGap()
							.addGroup(groupLayout.createParallelGroup(Alignment.TRAILING)
								.addComponent(btnTemperatura, Alignment.LEADING, GroupLayout.DEFAULT_SIZE, 131, Short.MAX_VALUE)
								.addComponent(btnConectar, GroupLayout.DEFAULT_SIZE, 131, Short.MAX_VALUE))
							.addPreferredGap(ComponentPlacement.RELATED)
							.addComponent(PortcomboBox, GroupLayout.PREFERRED_SIZE, 108, GroupLayout.PREFERRED_SIZE)
							.addGap(69))
						.addGroup(groupLayout.createSequentialGroup()
							.addGap(37)
							.addComponent(btnImprimir, GroupLayout.PREFERRED_SIZE, 75, GroupLayout.PREFERRED_SIZE)
							.addGap(18)
							.addComponent(btnPausar, GroupLayout.PREFERRED_SIZE, 75, GroupLayout.PREFERRED_SIZE)
							.addGap(18)
							.addComponent(btnCancelar)))
					.addContainerGap())
		);
		groupLayout.setVerticalGroup(
			groupLayout.createParallelGroup(Alignment.LEADING)
				.addGroup(groupLayout.createSequentialGroup()
					.addGap(13)
					.addGroup(groupLayout.createParallelGroup(Alignment.BASELINE)
						.addComponent(PrintingComboBox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
						.addComponent(lblNewLabel, GroupLayout.PREFERRED_SIZE, 24, GroupLayout.PREFERRED_SIZE))
					.addGap(8)
					.addGroup(groupLayout.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblNewLabel_1, GroupLayout.PREFERRED_SIZE, 24, GroupLayout.PREFERRED_SIZE)
						.addComponent(FilamentComboBox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
					.addPreferredGap(ComponentPlacement.UNRELATED)
					.addGroup(groupLayout.createParallelGroup(Alignment.BASELINE)
						.addComponent(btnConectar)
						.addComponent(PortcomboBox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
					.addGap(7)
					.addComponent(btnTemperatura)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(scrollPane, GroupLayout.PREFERRED_SIZE, 88, GroupLayout.PREFERRED_SIZE)
					.addGap(18)
					.addGroup(groupLayout.createParallelGroup(Alignment.BASELINE)
						.addComponent(btnPausar)
						.addComponent(btnCancelar)
						.addComponent(btnImprimir))
					.addGap(23))
		);
		groupLayout.linkSize(SwingConstants.VERTICAL, new Component[] {lblNewLabel, lblNewLabel_1});
		groupLayout.linkSize(SwingConstants.HORIZONTAL, new Component[] {lblNewLabel, lblNewLabel_1});
		
		textArea = new JTextArea();
		scrollPane.setViewportView(textArea);
		textArea.setFont(new Font("Monospaced", Font.PLAIN, 9));
		textArea.setEditable(false);
		DefaultCaret caret = (DefaultCaret) textArea.getCaret();
		caret.setUpdatePolicy(DefaultCaret.ALWAYS_UPDATE);
		pack();
		
		getContentPane().setLayout(groupLayout);
	}
	
	
	
	/**
	 * @return Returns the PrintingComboBox.
	 */
	public JComboBox getPrintingComboBox() {
		return PrintingComboBox;
	}

	/**
	 * @return Returns the FilamentComboBox.
	 */
	public JComboBox getFilamentComboBox() {
		return FilamentComboBox;
	}
	
	/**
	 * @return Returns the PortComboBox.
	 */
	public JComboBox getPortComboBox() {
		return PortcomboBox;
	}
	
	/**
	 * @return Returns the Conect button.
	 */
	public JButton getbtnConect() {
		return btnConectar;
	}
	
	/**
	 * @return Returns the temperature label.
	 */
	public JButton getbtnTemperatura() {
		return btnTemperatura;
	}
	
	/**
	 * @return Returns the textArea.
	 */
	public JTextArea gettextArea() {
		return textArea;
	}
	/**
	 * @return Returns the Imprimir,Pausar,cancelar buttons.
	 */
	public JButton getbtnImprimir() {
		return btnImprimir;
	}

	public JButton getbtnPausar() {
		return btnPausar;
	}

	public JButton getbtnCancelar() {
		return btnCancelar;
	}
}
