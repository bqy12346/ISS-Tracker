import json
import turtle
import urllib.request
import webbrowser
import geocoder
import requests
from skyfield.api import load, EarthSatellite
import threading
import time

# === Astronauten-Info speichern ===
u = "http://api.open-notify.org/astros.json"
response = urllib.request.urlopen(u)
result = json.loads(response.read())
with open("iss.txt", "w") as file:
    file.write("There are currently " + str(result["number"]) + " astronauts on the ISS:\n")
    for p in result["people"]:
        file.write(p["name"] + " - on board\n")
    g = geocoder.ip("me")
    file.write("\nYour current lat / long is: " + str(g.latlng))
webbrowser.open("iss.txt")

# === Karte einrichten ===
screen = turtle.Screen()
screen.setup(1280, 720)
screen.setworldcoordinates(-180, -90, 180, 90)
screen.bgpic("static/map.gif")
screen.title("ISS Live Tracker")
screen.register_shape("static/iss.gif")

iss = turtle.Turtle()
iss.shape("static/iss.gif")
iss.setheading(45)
iss.penup()
iss.hideturtle()

predictor = turtle.Turtle()
predictor.color("green")
predictor.penup()
predictor.hideturtle()

# === Live-Tracking in Hintergrund-Thread ===
# def track_iss():
#     while True:
#         try:
#             u = "http://api.open-notify.org/iss-now.json"
#             response = urllib.request.urlopen(u)
#             result = json.loads(response.read())
#             lat = float(result['iss_position']['latitude'])
#             lon = float(result['iss_position']['longitude'])
#             print(f"Live Position – Latitude: {lat}, Longitude: {lon}")
#             iss.goto(lon, lat)
#             iss.showturtle()
#             iss.dot(4, "red")
#         except Exception as e:
#             print("Fehler beim Live-Tracking:", e)
#         time.sleep(3)

def track_iss():
    while True:
        try:
            # 获取 ISS 实时位置
            url = "http://api.open-notify.org/iss-now.json"
            response = urllib.request.urlopen(url)
            result = json.loads(response.read())
            lat = float(result['iss_position']['latitude'])
            lon = float(result['iss_position']['longitude'])

            # 打印到终端
            print(f"Live Position – Latitude: {lat}, Longitude: {lon}")

            # 更新 turtle 图形界面位置
            iss.goto(lon, lat)
            iss.showturtle()
            iss.dot(4, "red")

            # 写入网页读取用的 JSON 文件
            with open("static/iss_position.json", "w") as f:
                json.dump({"lat": lat, "lon": lon}, f)

        except Exception as e:
            print("❌ Error during ISS tracking:", e)

        time.sleep(3)  # 每3秒更新一次


    # 写入实时位置到 json 文件
    with open("static/iss_position.json", "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)

    


# === TLE-Daten laden und Vorhersage zeichnen ===
def draw_prediction():
    try:
        tle_url = 'https://celestrak.org/NORAD/elements/stations.txt'
        tle_data = requests.get(tle_url).text.splitlines()
        line1 = None
        line2 = None
        for i in range(len(tle_data)):
            if "ISS" in tle_data[i]:
                line1 = tle_data[i+1]
                line2 = tle_data[i+2]
                break
        if not line1 or not line2:
            raise ValueError("ISS TLE data not found.")

        satellite = EarthSatellite(line1, line2, "ISS")
        ts = load.timescale()
        t0 = ts.now()

        for mins in range(0, 91 * 60, 3):
            t = t0 + mins / (24 * 60 * 60)
            geo = satellite.at(t)
            lat = geo.subpoint().latitude.degrees
            lon = geo.subpoint().longitude.degrees
            predictor.goto(lon, lat)
            predictor.dot(4)
    except Exception as e:
        print("Vorhersage fehlgeschlagen:", e)

# === Starten ===
threading.Thread(target=draw_prediction, daemon=True).start()
threading.Thread(target=track_iss, daemon=True).start()
screen.mainloop()
