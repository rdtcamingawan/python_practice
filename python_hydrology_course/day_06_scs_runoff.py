# Import modules
import pandas as pd
import numpy as np

# File paths - local
file_path = r"C:\Users\richmond\Downloads\testing\land_cover_cn.csv"

# Read the lookup CSV
df = pd.read_csv(file_path).set_index('land_cover')

def calculate_runoff(rainfall_mm, land_cover, soil_group):
    # Returns runoff depth, in mm

    # Column name
    column = f"cn_group_{soil_group.lower()}"
    
    # Parameters calculation
    cn = df.loc[land_cover, column]
    S = (25400 / cn) - 254

    # Discharge logic
    if rainfall_mm > 0.2 * S:
        discharge = (rainfall_mm - 0.2*S)**2 / (rainfall_mm + 0.8*S)
    else:
        discharge = 0

    return discharge, cn


rainfall_mm = 60.8
discharge, cn = calculate_runoff(rainfall_mm, 'Agriculture', 'B')

print("🌾 Runoff Calculation")
print("=" * 32)
print(f"""
Land Cover : Agriculture
Soil Group : C
Curve Number : {cn}
Runoff Depth : {discharge:.2f} mm
      """)