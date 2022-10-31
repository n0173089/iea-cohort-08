#!/usr/bin/env python3
import os
from flask import Flask, redirect, request, url_for
import logging
import sys
import requests
import datetime
import argparse

parser = argparse.ArgumentParser(description='Find distance of planet or the Sun from current location')
parser.add_argument('--at', type=datetime.datetime.fromisoformat, default=datetime.datetime.now().isoformat(timespec = 'seconds'), 
                    help='''Date and Time, given in YYYY-MM-DD, and HH:MM:SS 24 hour format, separated by a "T", i.e. 2022-10-01T20:30:00''')
#parser.add_argument('--from', action='store_true', help='You must follow "--from" with a "lat" and "lon" argument')
#subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', help='sub-command help')
parser.add_argument('--lat', type=float, default=0.0, help='enter a latitude')
parser.add_argument('--long', type=float, default=0.0, help='enter a longitude')
parser.add_argument('body', default="Sun", nargs='?', help='enter an astronomical body')

args = parser.parse_args()
date = args.at
date_entered = date.strftime("%Y-%m-%d")
time = args.at
time_entered = time.strftime("%H:%M:%S")
user_lat = args.lat
user_lon = args.long
astro_body = args.body.capitalize()

ASTRONOMYAPI_ID="9433cef6-d2ff-487c-a6fa-fb2841bd28e1"
ASTRONOMYAPI_SECRET="bc1928716fc215ea69c6b62ab2c11b4e95103664a7d7098e220e504def4d9553009107e337dc9c00b3aa70f466db2adba45ab94771452700c8841105bb34ee8b5faf491d5a0d3c02e58a8de48217a72bd4d19dc55af1b80e8b2cad017dc09bd4fb9f415205bf6f7473caa6416cef19fb"

logging.basicConfig(stream=sys.stdout, format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

signatures = []

app = Flask(__name__)

# configurations
font = os.environ.get('DISPLAY_FONT')

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


def print_position(astro_body, azimuth, altitude, from_earth, magnitude, latitude, longitude):
    """Prints the distance, magnitude, and position of the body in the sky using the supplied coordinates"""
    from_earth = '{:,}'.format(round(float(from_earth)))
    magnitude = round(float(magnitude), 2)
    print(f'''At {time_entered} on {date_entered} from lat: {latitude}, long: {longitude}:

    {astro_body}:
        Distance from Earth: {from_earth} km
        Magnitude: {magnitude}
        Position:
            Azimuth: {azimuth}
            Altitude: {altitude}''')

@app.route('/', methods=['GET'])
def index():
    html = """
    <form action="/signatures" method="post">
        Enter an astronomical body: <input type="text" name="message"><br>
        <input type="submit" value="Submit">
    </form>
    <br />
    <br />
    Lookup Results: <br />
    <font face="%(font)s" color="red">
        %(messages)s
    </font>

    <br /> <br />
    """
    messages_html = "<br />".join(signatures)
    return html % {"font": font, "messages": messages_html}

@app.route('/signatures', methods=['POST'])
def write():
    message = request.form.get('message')
    signatures.append(message)

    return redirect(url_for('index'))

if __name__ == "__main__":
    latitude, longitude = get_observer_location()
    if user_lat != 0.0:
        latitude = user_lat
    if user_lon != 0.0:
        longitude = user_lon
    elevation = get_observer_elevation(latitude, longitude)
    azimuth, altitude, from_earth, magnitude = get_body_position(latitude, longitude, elevation, astro_body, date_entered, time_entered)
    print_position(astro_body, azimuth, altitude, from_earth, magnitude, latitude, longitude)
    app.run(host='0.0.0.0', port=8080)
