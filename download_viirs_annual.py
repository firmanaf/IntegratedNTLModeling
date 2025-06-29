from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFolderDestination,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsGeometry,
    QgsProject,
    QgsProcessing,
    QgsRasterLayer
)
import ee, os, urllib.request, zipfile

class DownloadVIIRSAnnual(QgsProcessingAlgorithm):
    INPUT_LAYER   = 'INPUT_LAYER'
    YEARS         = 'YEARS'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def tr(self, string):
        return QCoreApplication.translate('NighttimeLightAnnualComposer', string)

    def createInstance(self):
        return DownloadVIIRSAnnual()

    def name(self):
        return 'nighttime_light_annual_composer'

    def displayName(self):
        return self.tr('Nighttime Light Annual Composer')

    def shortHelpString(self):
        return self.tr(
            "Downloads VIIRS Nighttime Lights (avg_rad) annual composites "
            "from 'NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG', clips to an input polygon, "
            "and packages each composite into a GeoTIFF named VIIRS_YYYY.tif inside its zip archive.\n\n"
            "Created by Firman Afrianto during PT. Sagamartha Ultima SkillShare 2025"
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                self.tr('Input Polygon Layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        years = [str(y) for y in range(2014, 2026)]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.YEARS,
                self.tr('Select Years'),
                options=years,
                allowMultiple=True,
                defaultValue=[years.index('2024')]
            )
        )
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Output Folder for GeoTIFFs')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source      = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        years_idx   = self.parameterAsEnums(parameters, self.YEARS, context)
        out_folder  = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)

        years_all = [str(y) for y in range(2014, 2026)]
        years_sel = [int(years_all[i]) for i in years_idx]

        os.makedirs(out_folder, exist_ok=True)

        extent = source.sourceExtent()
        src_crs = source.sourceCrs()
        trg_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        transform = QgsCoordinateTransform(src_crs, trg_crs, QgsProject.instance())
        geom = QgsGeometry.fromRect(extent)
        geom.transform(transform)
        bb   = geom.boundingBox()
        roi  = ee.Geometry.Rectangle([bb.xMinimum(), bb.yMinimum(), bb.xMaximum(), bb.yMaximum()])

        try:
            ee.Initialize()
        except Exception:
            ee.Authenticate()
            ee.Initialize()

        for y in years_sel:
            start = f"{y}-01-01"
            end = f"{y}-12-31"
            feedback.pushInfo(f"Memproses komposit {y}")
            coll = (
                ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
                    .select('avg_rad')
                    .filterDate(start, end)
                    .filterBounds(roi)
            )
            if coll.size().getInfo() == 0:
                feedback.pushWarning(f"Data {y} tidak ditemukan.")
                continue

            img = coll.mean().clip(roi)
            url = img.getDownloadURL({'scale': 500, 'region': roi.toGeoJSONString(), 'crs': 'EPSG:4326'})

            # Download original ZIP
            zip_path = os.path.join(out_folder, f"VIIRS_{y}.zip")
            urllib.request.urlretrieve(url, zip_path)

            # Extract the first TIFF
            extracted_tif = None
            with zipfile.ZipFile(zip_path, 'r') as zin:
                for fn in zin.namelist():
                    if fn.lower().endswith('.tif'):
                        extracted_tif = zin.extract(fn, out_folder)
                        break

            if not extracted_tif or not zipfile.is_zipfile(zip_path):
                feedback.pushWarning(f"Gagal mengekstrak TIFF untuk {y}.")
                continue

            # Rename the TIFF to standard name
            new_name = f"VIIRS_{y}.tif"
            new_path = os.path.join(out_folder, new_name)
            os.replace(extracted_tif, new_path)

            # Repackage into ZIP with renamed TIFF
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                zout.write(new_path, arcname=new_name)

            # Load into QGIS
            layer = QgsRasterLayer(new_path, f"VIIRS_{y}")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)

        return {}
