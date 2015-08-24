package org.saig.jump.plugin.demto3d;

import org.saig.jump.lang.I18N;
import org.saig.jump.plugin.demto3d.DemTo3DPlugIn;

import com.vividsolutions.jump.workbench.plugin.Extension;
import com.vividsolutions.jump.workbench.plugin.PlugInContext;

public class DemTo3DExtension extends Extension {

	/** Extension Name */
	private final static String NAME = I18N
			.getString("org.saig.jump.plugin.demto3d.DemTo3DExtension.DEMto3D"); 

	/** Extension Version */
	private final static String VERSION = "2.3 (20150503)";

	/** Extension Description */
	private final static String DESCRIPCION = I18N
			.getString("org.saig.jump.plugin.demto3d.DemTo3DExtension.Extension-that-allows-to-print-a-DEM-in-3D");

	public String getName() {
		return NAME;
	}

	public String getVersion() {
		return VERSION;
	}

	public String getDescription() {
		return DESCRIPCION;
	}

	/** Extension plugin */
	private DemTo3DPlugIn demto3dPlugIn;

	@Override
	public void install(PlugInContext context) throws Exception {
		// instancia la herramienta e invocar a su método initialize()
		if (demto3dPlugIn == null) {
			demto3dPlugIn = new DemTo3DPlugIn();
		}
		demto3dPlugIn.initialize(context);
	}

	@Override
	public void uninstall(PlugInContext context) throws Exception {
		// elimina las herramientas de la interfaz de Kosmo
		if (demto3dPlugIn != null) {
			demto3dPlugIn.finish(context);
		}
	}

}
