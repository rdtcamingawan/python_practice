# Initialize QGIS
from qgis.core import QgsApplication
path_to_qgis = r"C:\Program Files\QGIS 3.40.2"
QgsApplication.setPrefixPath(path_to_qgis, True)
qgs = QgsApplication([], False)
qgs.initQgis()

# QGIS Imports
from qgis.core import (QgsRasterLayer, QgsRasterShader, QgsColorRampShader,
                       QgsSingleBandPseudoColorRenderer, QgsMapSettings, QgsMapRendererParallelJob,
                        QgsDateTimeRange, QgsRasterLayerTemporalProperties)

from qgis.PyQt.QtGui import (QColor
                                )

from qgis.PyQt.QtCore import (QDateTime, QTime, QDate
                                )

# Other import modules
from glob import glob
import os

# Find all rainfall dataset
folder_glob_key = r"C:\Users\richmond\Downloads\testing\data\rainfall_daily\rainfall_day_*.tif"
rainfalls = glob(folder_glob_key)
print(rainfalls)
# Map renderer function
def style_raster(rlayer):# Apply a color ramp
    fcn = QgsColorRampShader()
    fcn.setColorRampType(QgsColorRampShader.Interpolated)
    lst = [ QgsColorRampShader.ColorRampItem(0, QColor(0,0,0,0)),
        QgsColorRampShader.ColorRampItem(10, QColor(102,255,178)),
        QgsColorRampShader.ColorRampItem(1000, QColor(255,178,102)),
        ]
    fcn.setColorRampItemList(lst)
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(fcn)
    renderer = QgsSingleBandPseudoColorRenderer(rlayer.dataProvider(), 1, shader)
    rlayer.setRenderer(renderer)
    return rlayer

'''
======================= QGIS Processing =======================

1. Load each raster as a QgsRasterLayer
2. Apply a color ramp
3. Save as PNG

'''
for day, rainfall in enumerate(rainfalls):
    # Load as all rainfall raster as QgsRasterLayer
    rainfall_rlayers = {}
    rainfall_rlayers[f'rainfall_day_{1+day}'] = QgsRasterLayer(rainfall, 'rainfall')
    if not  rainfall_rlayers[f'rainfall_day_{day+1}'].isValid():
        print(f"Failed to load {rainfall}")
        continue
    
    # Apply style to each rainfall raster
    rainfall_rlayers[f'rainfall_day_{day+1}'] = style_raster(rainfall_rlayers[f'rainfall_day_{day+1}'])

    rlayer = rainfall_rlayers[f'rainfall_day_{day+1}']

    # Apply a temporal range
   # Enable temporal
    temporal = rlayer.temporalProperties()
    temporal.setFixedTemporalRange(QgsDateTimeRange(
        QDateTime(QDate(2025, 4, 1), QTime(0, 0)),
        QDateTime(QDate(2025, 4, 1), QTime(23, 59))
    ))
    print(day)
    print(type(rlayer))
       

# exit QGIS
qgs.exitQgis()
