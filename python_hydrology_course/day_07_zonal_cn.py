import geopandas as gpd
import pandas as pd

# File paths - local
sub_basins_path = r"C:\Users\richmond\Downloads\testing\sub_basins.geojson"
land_cover_path = r"C:\Users\richmond\Downloads\testing\land_cover.geojson"
land_cover_cn_path = r"C:\Users\richmond\Downloads\testing\land_cover_cn.csv"

# Read files
subbasins = gpd.read_file(sub_basins_path)
land_cover = gpd.read_file(land_cover_path)
cn_table = pd.read_csv(land_cover_cn_path).set_index('land_cover')

# Overlay geojsons
gdf_overlay = gpd.overlay(subbasins, land_cover, how='intersection').to_crs(epsg=32643)

# Define CN calc function
def weighted_avg(group):
    return (group['area'] * group['cn']).sum() / group['area'].sum()

# Calculate CN
gdf_overlay['area'] = gdf_overlay.geometry.area
# gdf_total_area = gdf_overlay.groupby(by=['basin_id']).area.agg('sum')
gdf = gdf_overlay.merge(cn_table['cn_group_c'], left_on=['land_cover'], right_index=True)
gdf = gdf.rename(columns={'cn_group_c': 'cn'})
result = gdf.groupby(by='basin_id').apply(weighted_avg).round(2)

# Add basin names back if needed
basin_names = subbasins.set_index('basin_id')['name'].to_dict()
result = result.to_frame(name='avg_cn')
result['basin_name'] = result.index.map(basin_names)

# Print
print("\n📊 AREA-WEIGHTED AVERAGE CN PER SUB-BASIN")
print(result)