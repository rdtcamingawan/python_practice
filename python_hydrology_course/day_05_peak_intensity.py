# Import modules
import pandas as pd

# File paths - local
file_path = r"C:\Users\richmond\Downloads\testing\rainfall_hourly.csv"
save_path = 1

# read CSV
df = pd.read_csv(file_path)

# Convert timestamp column to datetime format 
df['timestamp'] = pd.to_datetime(df['timestamp'], yearfirst=True)

# Set ad index
df.set_index('timestamp', inplace=True)

# Compute for the rolling 3hr cumulative rainfall
df_3hr_cum = df['rainfall_mm'].rolling(window=3, min_periods=1).sum()

# Compute for the 6hr cumulative rainfall
df_6hr_cum = df['rainfall_mm'].rolling(window=6, min_periods=1).sum()

# Find peaks
max_3hr = df_3hr_cum.max()
max_6hr = df_6hr_cum.max()
max_3hr_timestamp = df_3hr_cum.idxmax()
max_6hr_timestamp = df_6hr_cum.idxmax()

# Calculate start time before peak rainfall
peak_3hr_start = max_3hr_timestamp - pd.Timedelta(hours=2)
peak_3hr_end = max_3hr_timestamp

peak_6hr_start = max_6hr_timestamp - pd.Timedelta(hours=5)
peak_6hr_end = max_6hr_timestamp

# Print Statements

print(f"Peak 3-hr rainfall: {max_3hr:.1f} mm ({peak_3hr_start} to {peak_3hr_end})")
print(f"Peak 6-hr rainfall: {max_6hr:.1f} mm ({peak_6hr_start} to {peak_6hr_end})")
