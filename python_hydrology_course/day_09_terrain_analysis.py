import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
import numpy as np
import richdem as rd
from matplotlib import pyplot as plt

# File paths - local
raster_path = r"C:\Users\richmond\Downloads\testing\srtm.tif"
slope_path = r"C:\Users\richmond\Downloads\testing\slope.tif"
flow_dir_path = r"C:\Users\richmond\Downloads\testing\flow_dir.tif"

# Target CRS
dst_crs = 'EPSG:32643'

with rasterio.open(raster_path, 'r') as src:
    # Calculate reprojection parameters
    transform, width, height = calculate_default_transform(
        src.crs, # from
        dst_crs, # to
        src.width, # orignal width
        src.height, # original height
        *src.bounds # unpack left, bottom, up, right
    )

    # Copy metadata and update for new CRS and shape
    kwargs = src.meta.copy()
    kwargs.update({
        'crs' : dst_crs,
        'transform': transform,
        'width': width,
        'height' : height
    })

    # Read source data
    elevation = src.read(1).astype('float32')

    # Create empty array for reprojected DEM
    reprojected_dem = np.empty((height, width), dtype='float32')

    # Reproject
    reproject(
        source=elevation,
        destination = reprojected_dem,
        src_transform = src.transform,
        src_crs = src.crs,
        dst_transform = transform,
        dst_crs = dst_crs,
        resampling = Resampling.bilinear
    )
    
    # Terrain Analysis
    dem = rd.rdarray(reprojected_dem, no_data=-9999)
    slope = rd.TerrainAttribute(dem, attrib='slope_degrees')
    rd.rdShow(slope, axes=False, cmap='jet', figsize=(8,5.5))

    rd.FillDepressions(dem, epsilon=True, in_place=True)
    accum_d8 = rd.FlowAccumulation(dem, method='D8')
    d8_fig = rd.rdShow(accum_d8, zxmin=450, zxmax=550, zymin=550, zymax=450, figsize=(8,5.5), axes=False, cmap='jet')

with rasterio.open(slope_path, 'w', **kwargs) as dst:
    dst.write(slope, 1)

with rasterio.open(flow_dir_path, 'w', **kwargs) as dst:
    dst.write(accum_d8, 1)
