# Import modules
import rasterio
from rasterio import features
import numpy as np
from shapely.geometry import shape
import geopandas as gpd

from matplotlib import pyplot as plt

# File paths - local
flow_accum_path = r"C:\Users\richmond\Downloads\testing\flow_accum.tif"
streams_path = r"C:\Users\richmond\Downloads\testing\stream.gpkg"
save_plot = r"C:\Users\richmond\Downloads\testing\day_10.png"

# Read the raster using rasterio
with rasterio.open(flow_accum_path, 'r') as src:
    flow_accum = src.read(1)
    transform = src.transform
    crs = src.crs
    stream_network = (flow_accum > 100) * 1

mask = stream_network != 0
shapes = features.shapes(stream_network.astype('int32'), mask=mask, transform=transform)

# Convert raster to GeoJSON format
stream_features = [
    {'geometry': shape(geom), 'value': value}
    for geom, value in shapes
    if value == 1  # only stream pixels
]

# Convert to GeoDataFrame, plot and save
gdf_streams = gpd.GeoDataFrame(stream_features, crs=crs)
gdf_streams.to_file(streams_path, driver="GPKG")

# Plot
plt.figure(figsize=(10, 8))
gdf_streams.plot(color="blue", linewidth=1.2)
plt.title("Stream Network")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.savefig(save_plot, dpi=150)
plt.show()