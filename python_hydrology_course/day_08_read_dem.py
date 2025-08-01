import rasterio
import numpy as np
from matplotlib import pyplot as plt

# File paths - local
raster_path = r"C:\Users\richmond\Downloads\testing\srtm.tif"
save_path = r"C:\Users\richmond\Downloads\testing\srtm_output.png"

with rasterio.open(raster_path, 'r') as src:
    print("📊 DEM METADATA")
    print("==============")
    print(f"Raster CRS is: {src.crs}")
    print(f"Raster resolution is: {src.res}")
    print(f"Raster shape is: {src.shape}")
    print(f"Raster bounds is: {src.bounds}")
    print(f"Raster data type is: {src.dtypes[0]}")
    print(f"Raster nodata is: {src.nodata}")
    array = src.read(1)
    print(f"Elevation range: {array.min():.2f} m to {array.max():.2f} m")
    plt.imshow(array, cmap='terrain')
    plt.colorbar(label='Elevation (m)')
    plt.title('DEM: Synthetic SRTM')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    