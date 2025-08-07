# Import modules
import os
import tempfile
import whitebox_workflows as wbw
from whitebox_workflows import show
import geopandas as gpd
from matplotlib import pyplot as plt

# Initialize WhiteboxTools environment
wbe = wbw.WbEnvironment()

# File paths - local
dem_path = r"C:\Users\richmond\Downloads\testing\data\srtm.tif"
point_save_path = r"C:\Users\richmond\Downloads\testing\data\shps\pour_point.shp"

# Temporary Directory
temp_dir = tempfile.TemporaryDirectory()
print(temp_dir)

# Read raster
dem = wbe.read_raster(dem_path)

# Create a pour point
point_geom = gpd.points_from_xy(x=[76.04], y=[12.91], crs='EPSG:32643')
point = gpd.GeoDataFrame(geometry=point_geom)
point.to_file(point_save_path, driver='ESRI ShapeFile')

# =======================================================================
# Perform hydrologic functions
# =======================================================================


# 1. Depressionless DEM
dem_no_deps = wbe.fill_depressions(dem, flat_increment=0.001)

# 2. Flow accumulation
channel_threshold = 25
flow_accum = wbe.qin_flow_accumulation(dem_no_deps, 
                                       out_type='cells',
                                       convergence_threshold=channel_threshold, 
                                       log_transform=True
                                       )
temp_flow_accum = os.path.join(temp_dir.name, 'wbt_flow_accum.tif')
print(temp_flow_accum)
wbe.write_raster(flow_accum, temp_flow_accum)

# 3. Map the streams by thresholding
streams = flow_accum > channel_threshold

# 4. Snap point to streams
point = wbe.read_vector(point_save_path)
point = wbe.jenson_snap_pour_points(point, streams, 5.0)

# 5. D8 Pointer
d8_pntr = wbe.d8_pointer(dem_no_deps)

# 6. Extract watershed
watershed = wbe.watershed(d8_pointer=d8_pntr, pour_points=point)
watershed_vec = wbe.raster_to_vector_polygons(watershed) # vectorize
watershed_vec = wbe.smooth_vectors(watershed_vec, filter_size=5)  # smooths

temp_watersched_vec = os.path.join(temp_dir.name, 'wbt_watershed_vsc.gpkg')
wbe.write_vector(watershed_vec, temp_watersched_vec) # save to file

# 7. Extract streams inside the watershed
streams = streams * watershed
streams_vec = wbe.raster_streams_to_vector(streams, d8_pntr)
streams_vec, tmp1, tmp2, tmp3 = wbe.vector_stream_network_analysis(streams_vec, dem_no_deps)

temp_streams_vec = os.path.join(temp_dir.name, 'wbt_streams_vec.gpkg')
wbe.write_vector(streams_vec, temp_streams_vec) # save to file

# Extract streams based on Strahler order
strahler_streams = wbe.strahler_stream_order(d8_pntr=d8_pntr, 
                                             streams_raster=streams)
strahler_streams_vec = wbe.raster_streams_to_vector(strahler_streams, d8_pntr)


fig, ax = plt.subplots()

ax = show(dem, ax=ax, label = 'DEM')
ax = show(point, ax=ax, label= 'outlet')
ax = show(watershed_vec, ax=ax, label= 'watershed')
ax = show(strahler_streams_vec, ax=ax, label='stream network')

ax.set_xlabel('long')
ax.set_ylabel('lat')

plt.title('Watershed Delineation')
plt.legend()
plt.tight_layout()
# plt.savefig(fig_save_path)

plt.show()

temp_dir.cleanup()
