import pandas as pd

file_path = r"C:\Users\richmond\Downloads\testing\rainfall_data.csv"
save_path = r"C:\Users\richmond\Downloads\testing\rainfall_data_day_04.csv"

df = pd.read_csv(file_path)
df_filtered = df[df["rainfall_24hr_mm"] >= 100 ]
df_filtered.sort_values(by=["rainfall_24hr_mm"], inplace=True, ascending=False)
df_filtered.to_csv(save_path)

print(df_filtered.head())
