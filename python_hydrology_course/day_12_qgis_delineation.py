# Import modules
from qgis.core import QgsApplication

# Initialize QgsApplication
path_to_qgis = r"C:\Program Files\QGIS 3.40.2"
QgsApplication.setPrefixPath(path_to_qgis, True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Import QGIS processing
import processing
from processing.core.Processing import Processing
Processing.initialize()

# QGIS API imports
from qgis.core import (QgsRasterLayer, QgsVectorLayer,
                       QgsProcessingAlgorithm,)
from qgis.analysis import QgsGeometrySnapper, QgsInternalGeometrySnapper

# Other imports
import geopandas as gpd

# Read Files
dem_path = r"C:\Users\richmond\Downloads\testing\srtm.tif"
shp_path = r"C:\Users\richmond\Downloads\testing\shps\pour_point.shp"

# read raster
rlayer = QgsRasterLayer(dem_path, "dem")
if not rlayer.isValid():
    print("Layer failed to load!")

# read vector
# in QGIS
vlayer = QgsVectorLayer(shp_path, "outlet", "ogr")
if not vlayer.isValid():
    print("Layer failed to load!")

# in Geopandas -- to get point coordinates only
gdf = gpd.read_file(shp_path)
coords = gdf.get_coordinates()

"""

Hydrologic analysis using QGIS headless mode

Wateshed Delineation usign GRASS
1. r.fill.dir
2. r.watershed
3. r.water.outlet

"""

# Fill depressions
alg_params = {
    'input' : dem_path,
    'output' : 'TEMPORARY_OUTPUT',
    'direction': 'TEMPORARY_OUTPUT'
}
filled_dem = processing.run("grass85:r.fill.dir", alg_params)['output']

# Run streams and subbasin delineations
alg_params = {
    'elevation': dem_path,
    'depression': 'TEMPORARY_OUTPUT',
    'threshold': 100,
    'stream': 'TEMPORARY_OUTPUT',
    'drainage': 'TEMPORARY_OUTPUT',
    'basin': 'TEMPORARY_OUTPUT',
}
grass_watershed = processing.run('grass:r.watershed', alg_params),

# Snap outlet to nearest streams

# Vectorized stream segments
alg_params = {
    'input': grass_watershed['stream'],
    'output': 'TEMPORARY_OUTPUT',
    'type': 'line'
}
streams_vec = processing.run('grass:r.to.vect', alg_params)['output']

# Snap outlet
alg_params = {
    'INPUT': vlayer,
    'REFERENCE_LAYER': streams_vec,
    'TOLERANCE': 10.0,
    'OUTPUT': 'TEMPORARY_OUTPUT'
    }
snapped_point = processing.run('native:snapgeometries', alg_params)
point_coordinates = f"{coords[x]}, {coords['y']}"

# Finally delineate the watershed
alg_params = {
    'input': grass_watershed['drainage'],
    'output': 'TEMPORARY_OUTPUT',
    'coordinates': point_coordinates
}
basin = processing.run('grass:r.water.outlet', alg_params)

# Vectorize
alg_params = {
    'input': basin['output'],
    'output': 'TEMPORARY_OUTPUT',
    'type': 'area'
}
basin_vec = processing.run('grass:r.to.vect', alg_params)['output']

for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id())

qgs.exitQgis()