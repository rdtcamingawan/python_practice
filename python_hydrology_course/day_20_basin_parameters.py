# Import modules
from whitebox_workflows import WbEnvironment, show
import geopandas as gpd
import matplotlib.pyplot as plt
import tempfile
import os

class WatershedDelineation:
    def __init__(self, raster , outlet, min_size):
        # Intialize WbEnvironment
        self.wbe = WbEnvironment()

        # Define object
        self.raster = self.wbe.read_raster(raster)
        self.min_size = min_size
        self.outlet = self.wbe.read_vector(outlet)

        # Run analysis and store results
        self.terrain_analysis_results = self.terrain_analysis()
        self.watershed_characterization_results = self.watershed_characterization()

    def terrain_analysis(self):
        # Filled depression
        # filled_dem = self.wbe.fill_depressions(self.raster)
        filled_dem = self.wbe.breach_depressions_least_cost(self.raster)
        
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

        return {
                'filled_dem' : filled_dem,
                'basin' : basin,
                'basin_vec' : basin_vec,
                'streams_vec' : streams_vec,
                'snapped_point' : snapped_point
                    }
    
    def subbasins(self):
        """
        Computes and plots the subbasins within a given watershed.
        """
        return None


    def watershed_characterization(self):
        # Determine longest flow path
        longest_flowpath = self.wbe.longest_flowpath(self.terrain_analysis_results['filled_dem'], 
                                                     self.terrain_analysis_results['basin'])
        # Compute basin averaged slope -- based on longest flow path / dH
        # Area-Weighted Curve Number
        # Compute lag time (SCS)
        return {
            'longest_flowpath' : longest_flowpath
        }
    
    def plot_results(self, ax=None):
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(10, 10), sharey=True)

        # Plot layers
        show(self.raster, ax=ax, cmap='terrain', alpha=0.7, label='DEM', zorder=1)
        show(self.terrain_analysis_results['basin_vec'],  ax=ax, 
                                            color=(1.0, 1.0, 0, 1), 
                                            edgecolor=(1.0, 0, 1.0, 0.5), 
                                            linewidth=2.0, label='Watershed', 
                                            zorder=2)
        show(self.terrain_analysis_results['streams_vec'], ax=ax, color='red', 
                                            linewidth=1.2, 
                                            label='Streams',
                                            zorder=3)
        show(self.watershed_characterization_results['longest_flowpath'], ax=ax,
                                            linewidth= 2.0,
                                            label= 'Longest Flow Path',
                                            color = 'black',
                                            zorder = 4
                                            )
        show(self.terrain_analysis_results['snapped_point'], ax=ax, 
                                            color='red', 
                                            label='Snapped Outlet', 
                                            marker='^', 
                                            s=43, 
                                            zorder=5)

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

        # Run delineation
        try:
            ws = WatershedDelineation(raster, shp_tmp_path, min_size=10000)
            ws.plot_results(ax=axes[idx])
        except Exception as e:
            print(f"Failed on outlet {idx}: {e}")

plt.tight_layout()
plt.show()

