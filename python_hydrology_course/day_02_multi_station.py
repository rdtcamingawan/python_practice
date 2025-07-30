def check_rainfall(station_name, rainfall_mm):
    print(f"\n📊 Analyzing: {station_name}")
    print(f"Rainfall: {rainfall_mm} mm")

    if rainfall_mm >= 150:
        print("🚨 RED ALERT: Extreme rainfall – High flood risk!")
    elif rainfall_mm >= 100:
        print("🟡 YELLOW ALERT: Significant rainfall – Check runoff")
    else:
        print("🟢 GREEN: Low flood risk")

stations = [
    ["Mandya Station", 145.0],
    ["Mysuru Station", 89.0],
    ["Chamrajnagar Station", 167.0],
    ["Krishnarajapura Station", 45.0],
    ["Ramanagara Station", 112.0]
]

for station in stations:
    check_rainfall(station[0], station[1])
    print("\n")

