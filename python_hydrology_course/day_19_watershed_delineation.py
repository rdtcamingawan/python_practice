# Import modules
from whitebox_workflows import WbEnvironment, show
import geopandas as gpd
import tempfile
import os
from matplotlib import pyplot as plt

class WatershedDelineation:
    def __init__(self, raster , outlet, min_size):
        # Intialize WbEnvironment
        self.wbe = WbEnvironment()

        # Define object
        self.raster = self.wbe.read_raster(raster)
        self.min_size = min_size
        self.outlet = self.wbe.read_vector(outlet)

        # Run analysis and store results
        self.basin_raster, self.basin_vector, self.streams_vector, self.snapped_point = self.terrain_analysis()

    def terrain_analysis(self):
        # Filled depression
        # filled_dem = self.wbe.fill_depressions(self.raster)
        filled_dem = self.basin_raster
        
        # D8 Pointer
        d8_flow_direction = self.wbe.d8_pointer(filled_dem)

        # D8 Flow Accumulation
        d8_flow_accumulation = self.wbe.d8_flow_accum(filled_dem)

        # Extract Streams
        streams = self.wbe.extract_streams(d8_flow_accumulation, self.min_size)
        streams_vec = self.wbe.raster_to_vector_lines(streams)

        # Snap point to streams
        snapped_point = self.wbe.jenson_snap_pour_points(self.outlet, 
                                                         streams,
                                                         snap_dist = 10
                                                         )

        # Watershed delineation
        basin = self.wbe.watershed(d8_pointer = d8_flow_direction,
                                   pour_points = snapped_point
                                   )
        basin_vec = self.wbe.raster_to_vector_polygons(basin)

        return basin, basin_vec, streams_vec, snapped_point
    
    def plot_results(self, ax=None):
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Plot layers
        show(self.raster, ax=ax, cmap='terrain', alpha=0.7, label='DEM', zorder=1)
        show(self.basin_vector, ax=ax, color='blue', linewidth=2, label='Watershed', zorder=2)
        show(self.streams_vector, ax=ax, color='red', linewidth=1.2, label='Streams',zorder=3)
        show(self.snapped_point, ax=ax, color='yellow', label='Snapped Outlet', marker='^', s=43, zorder=4)

        ax.set_title("Watershed Delineation")
        ax.legend()
        return ax

# File paths
raster = r"C:\Users\richmond\Downloads\testing\data\IfSAR Clipped 05.05.25.tif"
outlets = r"C:\Users\richmond\Downloads\testing\data\shps\amacan_outlets.shp"
with tempfile.TemporaryDirectory() as tmpdir:
    shp_tmp_path = os.path.join(tmpdir, 'point.shp')
    print(shp_tmp_path)

    # Read outlet to GeoDataFram
    gdf = gpd.read_file(outlets)

    fig, axes = plt.subplots(1, 2, figsize=(12, 10))  # 2x2 grid
    axes = axes.flatten()  # Convert 2x2 array to [ax0, ax1, ax2, ax3]

    for idx, row in gdf.iterrows():
        ax = axes[idx]
        point = gpd.GeoDataFrame([row], geometry='geometry', crs= gdf.crs)
        point.to_file(shp_tmp_path)
        
        basin = WatershedDelineation(raster=raster, outlet=shp_tmp_path, min_size=50000)

        # Run delineation
        try:
            ws = WatershedDelineation(raster, shp_tmp_path, min_size=50000)
            ws.plot_results(ax=axes[idx])
        except Exception as e:
            print(f"Failed on outlet {idx}: {e}")

plt.tight_layout()
plt.show()
