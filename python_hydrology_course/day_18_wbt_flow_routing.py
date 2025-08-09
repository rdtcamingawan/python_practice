# Import modules
from whitebox_workflows import WbEnvironment, show, WbPalette
import tempfile
from matplotlib import pyplot as plt

# # Intialized Whitebox Environment
wbe = WbEnvironment()

# # Define file paths
tmpdir = tempfile.TemporaryDirectory()
ifsar_path = r"C:\Users\richmond\Downloads\testing\data\IfSAR-32651.tif"

# Set Working directory
wbe_working_dir = wbe.working_directory = tmpdir.name
print(f'Working directry in: {wbe_working_dir}')

# Read files
raster = wbe.read_raster(ifsar_path)

# ---------- WhiteboxTools Workflows ----------

# Fill missing data
fill_missing_data = wbe.fill_missing_data(raster, 
                                          filter_size = 10,
                                          weight = 2.0
                                          )
print('Filled missing data')

# Fill Depressions
filled_dem = wbe.fill_depressions(fill_missing_data)
print('Filled depression')

# Flow Direction
d8_pointer = wbe.d8_pointer(filled_dem)
print('Calculated D8 POinter / flow direction')

# Qin Flow Accumulation
flow_accum = wbe.qin_flow_accumulation(filled_dem)
print('Calculated flow accumulation', '\n')
print('Plotting results!')

# Plot Rasters
fig, axs = plt.subplots(2,2)
# Plot filled missing data
show(fill_missing_data,
                ax = axs[0,0],
                cmap='terrain',
                title = 'Filled Missing Data'
                            )

# Plot filled depressions
show(filled_dem,
                ax = axs[0,1],
                cmap='terrain',
                title = 'Filled Depressions'
                            )

# Plot D8 Pointer
show(d8_pointer,
                ax = axs[1,0],
                cmap='terrain',
                title = 'D8 Pointer'
                            )

# Plot Flow Accumulation
show(flow_accum,
                ax = axs[1,1],
                cmap='terrain',
                title = 'Flow Accumulation'
                            )

plt.tight_layout()
plt.show()

tmpdir.cleanup()
print('clean up')