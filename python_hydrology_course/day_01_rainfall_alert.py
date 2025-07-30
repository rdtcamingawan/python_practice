# ==========================================
# DAY 1 PROJECT: RAINFALL ALERT SYSTEM
# For RIDF Stations | Pre-HEC-HMS Screening
# ==========================================

# Simulated incoming telemetered data
station_id = "RIDF_2089"
station_name = "Mandya District Rain Gauge"
date = "2025-04-05"
rainfall_24hr_mm = 160  # High monsoon rainfall
latitude = 12.5198
longitude = 76.8546

# HEC-HMS relevant thresholds
runoff_trigger = 50.0    # mm – likely runoff
flood_watch = 100.0      # mm – potential flash flood
flood_warning = 150.0    # mm – high risk

# Print report
print("\n🌧️  RIDF RAINFALL MONITORING REPORT")
print("=" * 45)
print(f"Station ID        : {station_id}")
print(f"Name              : {station_name}")
print(f"Location          : {latitude:.4f}°, {longitude:.4f}°")
print(f"Date              : {date}")
print(f"24-Hour Rainfall  : {rainfall_24hr_mm} mm")

# Decision logic for flood modeling prep
if rainfall_24hr_mm >= flood_warning:
    print("🚨 STATUS: FLOOD WARNING – HIGH RISK!")
    print("❗ Action: Prioritize for HEC-HMS event simulation")
elif rainfall_24hr_mm >= flood_watch:
    print("🟡 STATUS: FLOOD WATCH – MODERATE RISK")
    print("❗ Action: Flag for review and land cover analysis")
elif rainfall_24hr_mm >= runoff_trigger:
    print("✅ STATUS: Runoff Likely")
    print("➡️  Action: Include in baseflow estimation")
else:
    print("🟢 STATUS: Low runoff potential")
    print("➡️  Action: No immediate action needed")

print("=" * 45)

duration_hours = 12  # Assume peak 12-hour burst
intensity = rainfall_24hr_mm / duration_hours
print(f"Peak Intensity    : {intensity:.2f} mm/hr")

# Save report to file
with open("rainfall_alert_today.txt", "w") as f:
    f.write(f"Station: {station_name}\n")
    f.write(f"Rainfall: {rainfall_24hr_mm} mm\n")
    f.write(f"Status: {'FLOOD WARNING' if rainfall_24hr_mm >= 150 else 'WATCH' if rainfall_24hr_mm >= 100 else 'NORMAL'}\n")