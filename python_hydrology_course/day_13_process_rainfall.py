# Initialize QGIS
from qgis.core import QgsApplication
path_to_qgis = r"C:\Program Files\QGIS 3.40.2"
QgsApplication.setPrefixPath(path_to_qgis, True)
qgs = QgsApplication([], False)
qgs.initQgis()

# QGIS Imports
from qgis.core import (QgsRasterLayer, QgsRasterShader, QgsColorRampShader,
                       QgsSingleBandPseudoColorRenderer, QgsMapSettings, QgsMapRendererParallelJob,
                        )

from qgis.PyQt.QtGui import (QColor
                                )

from qgis.PyQt.QtCore import (QSize
                                )

# Other import modules
from glob import glob
import os

# Find all rainfall dataset
folder_glob_key = r"C:\Users\richmond\Downloads\testing\data\rainfall_daily\rainfall_day_*.tif"
rainfalls = glob(folder_glob_key)

'''
======================= QGIS Processing =======================

1. Load each raster as a QgsRasterLayer
2. Apply a color ramp
3. Save as PNG

'''
for day, rainfall in enumerate(rainfalls):
    # Load as QgsRasterLayer
    rlayer = QgsRasterLayer(rainfall, 'rainfall')

    # Apply a color ramp
    fcn = QgsColorRampShader()
    fcn.setColorRampType(QgsColorRampShader.Interpolated)
    lst = [ QgsColorRampShader.ColorRampItem(0, QColor(0,0,0)),
        QgsColorRampShader.ColorRampItem(10, QColor(102,255,178)),
        QgsColorRampShader.ColorRampItem(1000, QColor(255,178,102)),
        ]
    fcn.setColorRampItemList(lst)
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(fcn)
    renderer = QgsSingleBandPseudoColorRenderer(rlayer.dataProvider(), 1, shader)
    rlayer.setRenderer(renderer)

    # Save as PNG
    ms = QgsMapSettings()
    ms.setLayers([rlayer])
    ms.setExtent(rlayer.extent())
    ms.setOutputSize(QSize(800, 600))
    ms.setOutputDpi(300)

    job = QgsMapRendererParallelJob(ms)
    job.start()
    job.waitForFinished()

    img = job.renderedImage()
    save_folder_name = r"C:\Users\richmond\Downloads\testing\results\rainfall_day13"
    fname = os.path.join(save_folder_name,f"day_{day}.png")
    img.save(fname)

# exit QGIS
qgs.exitQgis()
