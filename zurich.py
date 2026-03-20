from skyfield.api import load, wgs84
from datetime import datetime, timezone
import requests
import pytz
import os

# Location setup for Zurich
latitude = 47.3769
longitude = 8.5417
elevation = 558

# Get ISS passes over Zurich in the next 7 days
def get_iss_passes(days=7):
    ts = load.timescale()
    now = datetime.now(timezone.utc)
    location = wgs84.latlon(latitude, longitude, elevation_m=elevation)

    # Load live satellite data for the ISS
    satellites = load.tle_file('http://celestrak.org/NORAD/elements/stations.txt')  # returning a list of Earth satellites
    iss = next(sat for sat in satellites if 'ISS' in sat.name)

    passes = []

    for day_offset in range(days):
        t0 = ts.utc(now.year, now.month, now.day + day_offset)
        t1 = ts.utc(now.year, now.month, now.day + day_offset + 1)

        # Find rise, culmination, and set events for ISS above 10° elevation
        times, events = iss.find_events(location, t0, t1, altitude_degrees=10.0)

        pass_data = []
        for ti, event in zip(times, events):
            label = ('rise above 10°', 'culminate', 'set below 10°')[event]  # Label the event
            pass_data.append((label, ti.utc_datetime()))  # Store label and UTC time
        
        # check that the list is not empty
        if pass_data:
            passes.append(pass_data)

    return passes

# Get weather forecast (cloud coverage %) for a specific UTC time
def get_weather_forecast(dt_utc):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        raise RuntimeError("Missing OPENWEATHER_API_KEY environment variable." "Please set it before running zurich.py")

        
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': API_KEY,
        'units': 'metric'
    }

    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        forecast = response.json()
    except requests.RequestException as e:
        print(f"Weather API request failed: {e}")
        return None

    if "list" not in forecast or not forecast["list"]:
        print("Weather API returned no forecast data.")
        return None

    # Find the forecast entry closest to the target hour
    target_hour = dt_utc.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)  # Rounds it down to the nearest whole hour
    closest_entry = min(
        forecast['list'],
        key=lambda item: abs(datetime.fromtimestamp(item['dt'], timezone.utc) - target_hour)  # Converts item['dt'] (a UNIX timestamp) into a datetime in UTC
    )

    return closest_entry['clouds']['all']  # cloud percentage (0–100)

# Filter and return only visible passes (low cloud cover)
def visible_passes():
    all_passes = get_iss_passes() # all passes over zurich within a week by default
    visible = []
    invisible = []

    for iss_pass in all_passes:
        # Use the culmination time to check visibility
        mid_event = next((e for e in iss_pass if e[0] == 'culminate'), None)
        if mid_event:
            cloud_cover = get_weather_forecast(mid_event[1])  # [label, time]
            if cloud_cover is not None and cloud_cover < 30:
                visible.append((iss_pass, cloud_cover))
            else:
                invisible.append((iss_pass, cloud_cover))
        
    return visible, invisible

# Print passes in clean readable format
def print_passes(passes, bad_weather):
    local_tz = pytz.timezone('Europe/Zurich') # Convert the UTC time of culmination to local time
    #print(type(local_tz))

    print("\n📡 Upcoming Visible ISS Passes in Zurich:\n")

    for iss_pass, cloud in passes:
        mid_event = next((e for e in iss_pass if e[0] == 'culminate'), None)
        if mid_event:
            dt_local = mid_event[1].astimezone(local_tz)
            date_str = dt_local.strftime("%a, %b %d")  # get a better format for time
            time_str = dt_local.strftime("%H:%M")
            print(f"🛰️  {date_str} at {time_str} (Cloud cover: {cloud}%)    ✔️ ")

    print("\n📡 Invisible ISS Passes in Zurich:\n")

    for iss_pass, cloud in bad_weather:
        mid_event = next((e for e in iss_pass if e[0] == 'culminate'), None)
        dt_local = mid_event[1].astimezone(local_tz)
        date_str = dt_local.strftime("%a, %b %d")  # get a better format for time
        time_str = dt_local.strftime("%H:%M")
        print(f"🛰️  {date_str} at {time_str} (Cloud cover: {cloud}%)    ❌ ")


# Run the program
if __name__ == '__main__':
    result, bad_weather = visible_passes()
    print_passes(result, bad_weather)
