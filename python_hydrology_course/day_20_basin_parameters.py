# Import modules
from whitebox_workflows import WbEnvironment, show
import geopandas as gpd
import matplotlib.pyplot as plt
import tempfile
import os

class CurveNumberLookUp:
    def __init__(self):
        self.cn_look_up =  {
            "Built-up": {
                "Clay Loam": 98,
                "Sandy Clay Loam": 98,
                "Silty Clay Loam": 98,
                "Undifferentiated": 98
            },
            "Brush/Shrubs": {
                "Clay Loam": 86,
                "Sandy Clay Loam": 82,
                "Silty Clay Loam": 82,
                "Undifferentiated": 86
            },
            "Open/Barren": {
                "Clay Loam": 94,
                "Sandy Clay Loam": 91,
                "Silty Clay Loam": 91,
                "Undifferentiated": 94
            },
            "Inland Water": {
                "Clay Loam": 98,
                "Sandy Clay Loam": 98,
                "Silty Clay Loam": 98,
                "Undifferentiated": 98
            },
            "Annual Crop": {
                "Clay Loam": 91,
                "Sandy Clay Loam": 88,
                "Silty Clay Loam": 88,
                "Undifferentiated": 91
            },
            "Grassland": {
                "Clay Loam": 88,
                "Sandy Clay Loam": 83,
                "Silty Clay Loam": 83,
                "Undifferentiated": 88
            },
            "Closed Forest": {
                "Clay Loam": 87,
                "Sandy Clay Loam": 83,
                "Silty Clay Loam": 83,
                "Undifferentiated": 87
            },
            "Perennial Crop": {
                "Clay Loam": 89,
                "Sandy Clay Loam": 84,
                "Silty Clay Loam": 84,
                "Undifferentiated": 89
            },
            "Open Forest": {
                "Clay Loam": 86,
                "Sandy Clay Loam": 82,
                "Silty Clay Loam": 82,
                "Undifferentiated": 86
            }
        }

    def get_cn_value(self, land_cover, soil_layer):
        """
        Returns value fo curve number for a defined CN Look Up table
        Throws back an error if land cover / soil layer does not exists in the table
        """
        try:
            return int(self.cn_look_up[land_cover][soil_layer])
        except KeyError:
            print(f"Warning: Soil type '{soil_layer}' not found for land cover '{land_cover}'. Assigning default CN = 30.")
            return int(30)     


class WatershedDelineation:
    def __init__(self):
        # Initialize variable
        self.cn_lookup = CurveNumberLookUp()
        self.min_size = None
        self.raster = None
        self.outlet = None
        self.land_cover = None
        self.lc_layer_name = None
        self.soil_layer = None
        self.sl_layer_name = None
        self.terrain_analysis_results = None
        self.watershed_characterization_results = None

        # Initialize Temporaty Working Directory
        self.working_directory = tempfile.TemporaryDirectory()

        # Initialize WbEnvironment
        self.wbe = WbEnvironment()
        self.wbe.working_directory = self.working_directory.name
        

    def load_data(self, raster, outlet, min_size=10000):
        # Define object
        self.min_size = min_size
        self.raster = self.wbe.read_raster(raster)
        self.outlet = self.wbe.read_vector(outlet)

    def terrain_analysis(self):
        """
        This prepares the DEM for any hydrologic anlaysis
        """
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
        return {
                'filled_dem': filled_dem,
                'd8_flow_direction' : d8_flow_direction,
                'snapped_point' : snapped_point,
                'streams_vec' : streams_vec,
                'snapped_point' : snapped_point
                    }
    
    def delineate_watershed(self):
        """
        This function delineates the watershed based on prepared DEM 
        and vectorizes the basin itself
        """
        # Watershed delineation
        basin = self.wbe.watershed(d8_pointer = self.terrain_analysis['d8_flow_direction'],
                                   pour_points = self.terrain_analysis['snapped_point']
                                   )
        basin_vec = self.wbe.raster_to_vector_polygons(basin)
        self.wbe.write_vector(basin_vec, 'basin_vec.shp')

        return {
                'basin' : basin,
                'basin_vec' : basin_vec,
                    }
    
    def subbasins(self):
        """
        Computes and plots the subbasins within a given watershed.
        """
        return None
    
    def assign_cn_value(self, land_cover, lc_layer_name, soil_layer, sl_layer_name):
        """
        Clip the land cover and soil layer to the basin file
        Intersects the land cover with the soil layer.
        From the intersections, assign a curve number (CN) from a look-up table.
        """
        # Sets layer name for reading file
        self.lc_layer_name = lc_layer_name
        self.sl_layer_name = sl_layer_name
        basic_vec_path = os.path.join(self.working_directory, 'basin_vec.shp')

        # Read filepaths -- only accepts SHP files
        crs = 'EPSG:32651'
        land_cover = gpd.read_file(land_cover, layer=self.lc_layer_name).to_crs(crs=crs)
        soil_layer = gpd.read_file(soil_layer, layer=self.sl_layer_name).to_crs(crs=crs)
        basic_vec = gpd.read_file(basic_vec).to_crs(crs=crs) # Read basin vector file

        # Clip land cover and soil layer
        land_cover = gpd.clip(land_cover, basic_vec, keep_geom_type=True)
        clip_soil_layer = gpd.clip(soil_layer, basic_vec, keep_geom_type=True)

        # Intersect layers
        self.intersected = land_cover.sjoin(soil_layer)
        self.intersected['curve_number'] = self.intersected.apply(lambda x: self.cn_lookup.get_cn_value(land_cover=x['class_name'], soil_layer=x['type']), axis=1)

        return self.intersected

    def compute_weighted_cn(self):
        """
        Computes the weighted curve number
        """
        self.layer = self.intersected

        # Compute the area in sq.m
        area = self.layer.geometry.area
        self.layer['wt_cn'] = area * self.layer['curve_number'] 
        weighted_cn = self.layer['wt_cn'].sum() / area.sum()

        return weighted_cn
    
    def scs_lag(self):
        

    def watershed_characterization(self):
        # Determine longest flow path
        longest_flowpath = self.wbe.longest_flowpath(self.terrain_analysis_results['filled_dem'], 
                                                     self.terrain_analysis_results['basin'])
        # Get flow length
        flow_length = longest_flowpath.get_attribute_value(record_index=0,
                                                         field_name='LENGTH')
        flow_length = flow_length.get_value_as_f64()

        # Compute basin averaged slope
        ave_slope = longest_flowpath.get_attribute_value(record_index=0,
                                                         field_name='AVG_SLOPE')
        ave_slope = ave_slope.get_value_as_f64()

        # Area-Weighted Curve Number

        # Compute lag time (SCS)

        return {
            'longest_flowpath' : longest_flowpath,
            'flow_length' : flow_length,
            'ave_slope' : ave_slope
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
                                            color='blue', 
                                            label='Snapped Outlet', 
                                            marker='^', 
                                            s=43, 
                                            zorder=5)

        ax.set_title("Watershed Delineation")
        ax.legend()
        return ax
    
    def close(self):
        self.working_directory.cleanup()


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
            ws = WatershedDelineation()
            ws.load_data(raster, shp_tmp_path, min_size=10000)
            ws.terrain_analysis()
            basin_vec = ws.delineate_watershed()
            print(basin_vec)
            # show(basin_vec)
#             print(f'Basin average slope: {ws.watershed_characterization_results['ave_slope']} , in decimal.')
#             ws.plot_results(ax=axes[idx])
        except Exception as e:
            print(f"Failed on outlet {idx}: {e}")

plt.tight_layout()
plt.show()





