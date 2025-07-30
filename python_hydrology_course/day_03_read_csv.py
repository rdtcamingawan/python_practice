import csv

url = r'C:\Users\richmond\Downloads\testing\rainfall_data.csv'

with open(url, 'r') as file:
    reader = csv.reader(file)
    next(reader)

    high_risk_stations = []

    for row in reader:
        station_id = row[0]
        station_name = row[1]
        latitude = float(row[2])
        longitude = float(row[3])
        rainfall = float(row[4])

        print(f"\n📊 Processing: {station_name} ({station_id})")
        print(f"Location: {latitude:.4f}, {longitude:.4f}")
        print(f"24-hr Rainfall: {rainfall} mm")

        if rainfall >= 150:
            print("🚨 RED ALERT: Extreme rainfall – Prioritize for HEC-HMS")            
        elif rainfall >= 100:
            print("🟡 YELLOW ALERT: High rainfall – Check runoff potential")
            high_risk_stations.append({
                'id': station_id,
                'name': station_name,
                'lat': latitude,
                'lon': longitude,
                'rainfall': rainfall
            })
        else:
            print("🟢 GREEN: Low flood risk")

for station in high_risk_stations:
    print(f"{station['name']} ({station['id']}): {station['rainfall']} mm")

