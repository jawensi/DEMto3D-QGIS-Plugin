package org.saig.jump.controller.demto3d;

import javax.swing.JOptionPane;

import org.saig.jump.lang.I18N;

class CheckSpacing extends Exception {
	CheckSpacing() {
		JOptionPane.showMessageDialog(null, I18N.getString("org.saig.jump.controller.demto3d.DemTo3DException.incorrect-spacing"), "DEMTO3D",
				JOptionPane.ERROR_MESSAGE);
	}
}

class CheckExtension extends Exception {
	CheckExtension() {
		JOptionPane
				.showMessageDialog(
						null,
						I18N.getString("org.saig.jump.controller.demto3d.DemTo3DException.extension-bigger"),
						"DEMTO3D", JOptionPane.ERROR_MESSAGE);
	}
}

class CheckDimension extends Exception {
	CheckDimension() {
		JOptionPane
				.showMessageDialog(
						null,
						I18N.getString("org.saig.jump.controller.demto3d.DemTo3DException.selec-model-size"),
						"DEMTO3D", JOptionPane.ERROR_MESSAGE);
	}
}
class CheckScale extends Exception {
	CheckScale() {
		JOptionPane
				.showMessageDialog(
						null,
						I18N.getString("org.saig.jump.controller.demto3d.DemTo3DException.selec-scale"),
						"DEMTO3D", JOptionPane.ERROR_MESSAGE);
	}
}
class CheckHbase extends Exception {
	CheckHbase() {
		JOptionPane
				.showMessageDialog(
						null,
						I18N.getString("org.saig.jump.controller.demto3d.DemTo3DException.selec-H-base"),
						"DEMTO3D", JOptionPane.ERROR_MESSAGE);
	}
}
