package org.saig.jump.plugin.demto3d;

import javax.swing.Icon;

import org.gdal.gdal.gdal;
import org.saig.jump.controller.demto3d.DemTo3DController;
import org.saig.jump.images.demto3d.DemTo3DIconLoader;
import org.saig.jump.lang.I18N;

import com.vividsolutions.jump.workbench.JUMPWorkbench;
import com.vividsolutions.jump.workbench.plugin.AbstractPlugIn;
import com.vividsolutions.jump.workbench.plugin.EnableCheck;
import com.vividsolutions.jump.workbench.plugin.EnableCheckFactory;
import com.vividsolutions.jump.workbench.plugin.MultiEnableCheck;
import com.vividsolutions.jump.workbench.plugin.PlugInContext;

public class DemTo3DPlugIn extends AbstractPlugIn {

	/** Plugin Name */
	private final static String NAME = I18N
			.getString("org.saig.jump.plugin.demto3d.DemTo3DPlugIn.DEMto3D");

	/** Plugin icon */
	public final static Icon ICON = DemTo3DIconLoader.icon("stl_icon.png");

	public String getName() {
		return NAME;
	}

	public Icon getIcon() {
		return ICON;
	}

	public Icon getDisabledIcon() {
		return null;
	}

	@Override
	public void initialize(PlugInContext context) throws Exception {
	
		context.getWorkbenchFrame().getToolBar()
				.addPlugIn(this, context.getWorkbenchContext());
	}

	/** Boolean to access Options dialog */
	public static boolean TstVentNvoPres = false;

	private DemTo3DController controller;

	@Override
	public boolean execute(PlugInContext context) throws Exception {
		
		if (TstVentNvoPres == false) {
			TstVentNvoPres = true;
			gdal.AllRegister();
			controller = new DemTo3DController(context);
			controller.updateLayers();
			controller.openfile();
			controller.iniGeometricProperties();
			
			return true;
		} else {
			controller.getdialog().setVisible(true);
			return true;
		}
	}
	
	@Override
	public void finish(PlugInContext context) {
		context.getWorkbenchFrame().getToolBar().removePlugIn(this);
	}

	@Override
	public EnableCheck getCheck() {

		EnableCheckFactory ecf = new EnableCheckFactory(JUMPWorkbench
				.getFrameInstance().getContext());

		EnableCheck[] checks = {
				ecf.createWindowWithAssociatedTaskFrameMustBeActiveCheck(),
				ecf.createAtLeastNLayersMustExistCheck(1),
				ecf.createAtLeastNLayersMustBeRasterCheck(1),
				ecf.createAtLeastNVisibleLayersMustBeRasterCheck(1) };

		return new MultiEnableCheck(checks);
	}

}
