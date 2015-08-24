/* 
 * Kosmo - Sistema Abierto de Información Geográfica
 * Kosmo - Open Geographical Information System
 *
 * http://www.saig.es
 * (C) 2012, SAIG S.L.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public
 * License as published by the Free Software Foundation;
 * version 2.1 of the License.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 * For more information, contact:
 * 
 * Sistemas Abiertos de Información Geográfica, S.L.
 * Avnda. República Argentina, 28
 * Edificio Domocenter Planta 2ª Oficina 7
 * C.P.: 41930 - Bormujos (Sevilla)
 * España / Spain
 *
 * Teléfono / Phone Number
 * +34 954 788876
 * 
 * Correo electrónico / Email
 * info@saig.es
 *
 */
package org.saig.jump.images.demto3d;

import java.net.URL;

import javax.swing.ImageIcon;

import org.apache.log4j.Logger;
import org.saig.jump.lang.I18N;

import com.vividsolutions.jump.workbench.ui.images.IconLoader;

/**
 * Load icons from this class package
 * <p>
 * </p>
 * 
 * @author Sergio Ba&ntilde;os Calvo - sbc@saig.es
 * @since 1.0
 */
public class DemTo3DIconLoader {

    /** Default icon, it'd use it if the desired icon isn't found */
    public final static ImageIcon DEFAULT_UNKNOW_ICON =
        new ImageIcon(IconLoader.class.getResource("default_icon.png")); //$NON-NLS-1$

    /** Logger */
    public final static Logger LOGGER = Logger.getLogger(DemTo3DIconLoader.class);

    /**
     * @param filename
     * @return
     */
    public static ImageIcon icon( String filename ) {
        return icon(filename, true);
    }

    /**
     * @param filename
     * @param useDefaultForNull
     * @return
     */
    public static ImageIcon icon( String filename, boolean useDefaultForNull ) {
        URL urlIcon = DemTo3DIconLoader.class.getResource(filename);
        if (urlIcon == null) {
            if (useDefaultForNull) {
                LOGGER.warn(I18N.getMessage("com.vividsolutions.jump.workbench.ui.images.IconLoader.The-icon-{0}-has-not-been-found-default-icon-will-be-used", //$NON-NLS-1$
                    new Object[]{filename}));
                return DEFAULT_UNKNOW_ICON;
            } else {
                return null;
            }
        }
        return new ImageIcon(urlIcon);
    }

    /**
     * @param url
     * @return
     */
    public static ImageIcon icon( URL url ) {
        if (url == null) {

            LOGGER.warn(I18N.getMessage("com.vividsolutions.jump.workbench.ui.images.IconLoader.The-icon-{0}-has-not-been-found-default-icon-will-be-used", //$NON-NLS-1$
                new Object[]{url}));
            return DEFAULT_UNKNOW_ICON;
        }
        return new ImageIcon(url);
    }
}
