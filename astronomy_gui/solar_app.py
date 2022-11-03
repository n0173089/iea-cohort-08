#!/usr/bin/env python3
import os
from flask import Flask, redirect, request, url_for
import logging
import sys
import requests
import datetime
# import argparse

# parser = argparse.ArgumentParser(description='Find distance of planet or the Sun from current location')
# parser.add_argument('--at', type=datetime.datetime.fromisoformat, default=datetime.datetime.now().isoformat(timespec = 'seconds'), 
                    # help='''Date and Time, given in YYYY-MM-DD, and HH:MM:SS 24 hour format, separated by a "T", i.e. 2022-10-01T20:30:00''')
# parser.add_argument('--lat', type=float, default=0.0, help='enter a latitude')
# parser.add_argument('--long', type=float, default=0.0, help='enter a longitude')
# parser.add_argument('body', default="Sun", nargs='?', help='enter an astronomical body')

# args = parser.parse_args()
# date = args.at
# date_entered = date.strftime("%Y-%m-%d")
# time = args.at
# time_entered = time.strftime("%H:%M:%S")
# user_lat = args.lat
# user_lon = args.long
# astro_body = args.body.capitalize()

ASTRONOMYAPI_ID="9433cef6-d2ff-487c-a6fa-fb2841bd28e1"
ASTRONOMYAPI_SECRET="bc1928716fc215ea69c6b62ab2c11b4e95103664a7d7098e220e504def4d9553009107e337dc9c00b3aa70f466db2adba45ab94771452700c8841105bb34ee8b5faf491d5a0d3c02e58a8de48217a72bd4d19dc55af1b80e8b2cad017dc09bd4fb9f415205bf6f7473caa6416cef19fb"

#logging.basicConfig(stream=sys.stdout, format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


app = Flask(__name__)

# configurations
font = os.environ.get('DISPLAY_FONT')
astro_body = "Sun"
planet_colors = {"Sun": "orange", "Mercury": "maroon", "Venus": "yellow", "Mars": "red", "Jupiter": "brown", "Saturn": "olive", "Uranus": "teal",
                "Neptune": "navy", "Pluto": "grey"}
font_color = planet_colors[astro_body]
current_date = datetime.datetime.now()
date_entered = current_date.strftime("%Y-%m-%d")
time_entered = current_date.strftime("%H:%M:%S")


def get_observer_location():
    """Returns the longitude and latitude for the geolocation of this machine, based on its IP address."""
    response = requests.get(f'http://ip-api.com/json/?fields=lat,lon')
    data = response.json()
    latitude = data['lat']
    longitude = data['lon']
    return latitude, longitude


def get_observer_elevation(latitude, longitude):
    """Returns the elevation for the latitude and longitude previously entered."""
    response = requests.get(f'https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}')
    data = response.json()
    elevation = data['results'][0]['elevation']
    return elevation


def get_body_position(latitude, longitude, elevation, astro_body, date_entered, time_entered):
    """Returns the current position of the body in the sky at the specified location and date/time entered."""
    params = {"longitude": longitude, "latitude": latitude, "elevation": elevation, "from_date": {date_entered}, 
            "to_date": {date_entered}, "time": {time_entered}
    }
    response = requests.get(f'https://api.astronomyapi.com/api/v2/bodies/positions/{astro_body}/', 
                            auth=(ASTRONOMYAPI_ID, ASTRONOMYAPI_SECRET), params=params)
    data = response.json()
    altitude = data['data']['table']['rows'][0]['cells'][0]['position']['horizontal']['altitude']['string']
    azimuth = data['data']['table']['rows'][0]['cells'][0]['position']['horizontal']['azimuth']['string']
    from_earth = data['data']['table']['rows'][0]['cells'][0]['distance']['fromEarth']['km']
    magnitude = data['data']['table']['rows'][0]['cells'][0]['extraInfo']['magnitude']
    return azimuth, altitude, from_earth, magnitude

astro_data = ['']
    
@app.route('/', methods=['GET'])
def index():
    html = """
    <form action="/astro_data" method="post">
        Enter an astronomical body: <input type="text" name="astro_body"><br>
        (Optional) Enter a date in YY-MM-DD format: <input type="text" name="date_entered"><br>
        (Optional) Enter a time in HH:MM:SS format: <input type="text" name="time_entered"><br>
        (Optional) Enter a latitude: <input type="text" name="latitude"><br>
        (Optional) Enter a longitude: <input type="text" name="longitude"><br>
        <input type="submit" value="Submit">
    </form>
    <br />
    <br />
    Lookup Results: <br />
    <font face="%(font)s" color="%(font_color)s">
        <p> Astronomical body = %(astro_body)s </p>
        <p> Azimuth = %(azimuth)s </p>
        <p> Altitude = %(altitude)s </p>
        <p> Distance from Earth = %(from_earth)s </p>
        <p> Magnitude = %(magnitude)s </p>
        <p> Latitude = %(latitude)s </p>
        <p> Longitude = %(longitude)s </p>
    </font>

    <br /> <br />
    """
    astro_body = "<br />".join(astro_data)
    return html % {"font": font, "font_color": font_color, "astro_body": astro_body, "azimuth": azimuth, 
                "altitude": altitude, "from_earth": '{:,}'.format(round(float(from_earth))), "magnitude": round(float(magnitude), 2), 
                "latitude": latitude, "longitude": longitude}


@app.route('/astro_data', methods=['POST'])
def write():
    astro_body = request.form.get('astro_body')
    date_entered = request.form.get('date_entered')
    time_entered = request.form.get('time_entered')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    astro_data[0] = astro_body
    return redirect(url_for('index'))


if __name__ == "__main__": 
    latitude, longitude = get_observer_location()
    elevation = get_observer_elevation(latitude, longitude)
    azimuth, altitude, from_earth, magnitude = get_body_position(latitude, longitude, elevation, astro_body, date_entered, time_entered)
    app.run(host='0.0.0.0', port=8080)
