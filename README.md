
# DEMto3D

Extensión para impresión 3D de MDE (Modelos Digitales de Elevaciones) sobre QGIS

DEMto3D es una extensión que permite la exportación de MDE a formato STL.

## Requisitos previos
- QGIS 3.x instalado ([descargar QGIS](https://qgis.org/es/site/forusers/download.html))
- Python 3.7+
- Dependencias: PyQt5, numpy, osgeo (GDAL)


## Instalación

**Opción recomendada:**
1. Abre QGIS y ve a Complementos > Administrar e instalar complementos.
2. Busca "DEMto3D" en el buscador.
3. Haz clic en Instalar.

**Opción manual:**
1. Descarga el archivo ZIP del plugin desde [demto3d.com](http://demto3d.com) o desde este repositorio.
2. En QGIS, ve a Complementos > Administrar e instalar complementos > Instalar desde ZIP.
3. Selecciona el archivo descargado y sigue las instrucciones.

## Uso básico
1. Carga una capa raster de MDE en QGIS.
2. Abre el plugin DEMto3D desde el menú Complementos.
3. Configura la región, escala y parámetros de impresión.
4. Exporta el modelo a STL y ábrelo en tu software de impresión 3D.

## Ejemplo visual
![Ejemplo de uso](https://demto3d.com/img/demto3d_example.png)

## Documentación y ayuda
Más información, manual de usuario y guía de instalación en [demto3d.com](http://demto3d.com)

## Créditos
DEMto3D ha sido desarrollado como parte del Proyecto Fin de Carrera:
"Desarrollo de un módulo de impresión 3D de modelos digitales de elevaciones basado en sistema de bajo coste"
de la Ingeniería en Geodesía y Cartografía de la Universidad de Jaén.

Desarrollado por: Fco Javier Venceslá Simón
Contacto: demto3d@gmail.com

## Licencia
Este proyecto está licenciado bajo la GNU GPL v2 o superior.

## Contribuir
- Reporta bugs o solicita mejoras en la sección de Issues de este repositorio.
- Pull requests son bienvenidos.

---

# DEMto3D (English)

Extension to 3D printing DEM (Digital Elevation Model) in QGIS.

DEMto3D allows export DEM to STL format.

## Requirements
- QGIS 3.x installed ([download QGIS](https://qgis.org/en/site/forusers/download.html))
- Python 3.7+
- Dependencies: PyQt5, numpy, osgeo (GDAL)


## Installation

**Recommended option:**
1. Open QGIS and go to Plugins > Manage and Install Plugins.
2. Search for "DEMto3D" in the search bar.
3. Click Install.

**Manual option:**
1. Download the plugin ZIP file from [demto3d.com](http://demto3d.com) or from this repository.
2. In QGIS, go to Plugins > Manage and Install Plugins > Install from ZIP.
3. Select the downloaded file and follow the instructions.

## Basic usage
1. Load a DEM raster layer in QGIS.
2. Open the DEMto3D plugin from the Plugins menu.
3. Set the region, scale, and print parameters.
4. Export the model to STL and open it in your 3D printing software.

## Visual example
![Usage example](https://demto3d.com/img/demto3d_example.png)

## Documentation and help
More information, user manual and installation guide at [demto3d.com](http://demto3d.com)

## Credits
DEMto3D has been developed as part of the thesis:
"Development of a 3D printing module of digital elevation models based on low-cost system"
of the Master Degree in Cartography and Geodesy of the University of Jaén

Developed by: Francisco Javier Venceslá Simón
Contact: demto3d@gmail.com

## License
This project is licensed under the GNU GPL v2 or later.

## Contributing
- Report bugs or request features in the Issues section of this repository.
- Pull requests are welcome.
