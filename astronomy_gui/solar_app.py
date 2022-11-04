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

ASTRONOMYAPI_ID="9433cef6-d2ff-487c-a6fa-fb2841bd28e1"
ASTRONOMYAPI_SECRET="bc1928716fc215ea69c6b62ab2c11b4e95103664a7d7098e220e504def4d9553009107e337dc9c00b3aa70f466db2adba45ab94771452700c8841105bb34ee8b5faf491d5a0d3c02e58a8de48217a72bd4d19dc55af1b80e8b2cad017dc09bd4fb9f415205bf6f7473caa6416cef19fb"

#logging.basicConfig(stream=sys.stdout, format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


app = Flask(__name__)


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


def get_body_position(latitude, longitude, elevation, astro_body, current_date, current_time):
    """Returns the current position of the body in the sky at the specified location and date/time entered."""
    params = {"longitude": longitude, "latitude": latitude, "elevation": elevation, "from_date": {current_date}, 
            "to_date": {current_date}, "time": {current_time}
    }
    response = requests.get(f'https://api.astronomyapi.com/api/v2/bodies/positions/{astro_body}/', 
                            auth=(ASTRONOMYAPI_ID, ASTRONOMYAPI_SECRET), params=params)
    data = response.json()
    altitude = data['data']['table']['rows'][0]['cells'][0]['position']['horizontal']['altitude']['string']
    azimuth = data['data']['table']['rows'][0]['cells'][0]['position']['horizontal']['azimuth']['string']
    from_earth = data['data']['table']['rows'][0]['cells'][0]['distance']['fromEarth']['km']
    magnitude = data['data']['table']['rows'][0]['cells'][0]['extraInfo']['magnitude']
    return azimuth, altitude, from_earth, magnitude

astro_data = ['', '', '', '', '', '', '', '', '']
body_color = ''
body_colors = {"Sun": "orange", 
                "Moon": "grey", 
                "Mercury": "maroon", 
                "Venus": "yellow", 
                "Mars": "red", 
                "Jupiter": "brown", 
                "Saturn": "olive", 
                "Uranus": "teal", 
                "Neptune": "navy", 
                "Pluto": "purple"
                }
body_image = ''
body_images = {"Sun": "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e001435/GSFC_20171208_Archive_e001435~orig.jpg", 
                "Moon": "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e001861/GSFC_20171208_Archive_e001861~thumb.jpg", 
                "Mercury": "https://images-assets.nasa.gov/image/PIA11245/PIA11245~thumb.jpg", 
                "Venus": "https://images-assets.nasa.gov/image/PIA00271/PIA00271~thumb.jpg", 
                "Mars": "https://images-assets.nasa.gov/image/PIA00407/PIA00407~thumb.jpg", 
                "Jupiter": "https://images-assets.nasa.gov/image/PIA00343/PIA00343~thumb.jpg", 
                "Saturn": "https://images-assets.nasa.gov/image/PIA00400/PIA00400~thumb.jpg", 
                "Uranus": "https://images-assets.nasa.gov/image/PIA18182/PIA18182~thumb.jpg", 
                "Neptune": "https://images-assets.nasa.gov/image/PIA00046/PIA00046~thumb.jpg", 
                "Pluto": "https://images-assets.nasa.gov/image/PIA19952/PIA19952~thumb.jpg",
                "System": "https://images-assets.nasa.gov/image/PIA03153/PIA03153~thumb.jpg"
                }
astro_bodies = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
    
@app.route('/', methods=['GET'])
def index():
    html = """
    <body bgcolor="black">
    <body text="white">
    <font face="verdana, sans-serif">
    <form action="/astro_data" method="post">
        Enter an astronomical body: <input type="text" name="astro_body"><br>
        (Optional) Enter a date in YYYY-MM-DD format: <input type="text" name="date_entered"><br>
        (Optional) Enter a time in HH:MM:SS format: <input type="text" name="time_entered"><br>
        (Optional) Enter a latitude: <input type="text" name="latitude"><br>
        (Optional) Enter a longitude: <input type="text" name="longitude"><br>
        <input type="submit" value="Submit">
    </form>
    <br />
    <br />
    <img src="%(body_image)s" alt="All images courtesy of images.nasa.gov" width="400" height="400", style="float:right"> 
    Lookup Results: <br />
    
    </font>
    <p> 
    <font face="verdana, sans-serif" color="%(body_color)s">
    
    %(astro_body)s
    </font>
    </p>
    <br /> <br />
    """   
    user_data = "<br />".join(astro_data)
    return html % {"body_color": body_color, "astro_body": user_data, "date_entered": user_data, "time_entered": user_data, "azimuth": user_data, 
                "altitude": user_data, "from_earth": user_data, "magnitude": user_data, 
                "latitude": user_data, "longitude": user_data, "body_image": body_image}


@app.route('/astro_data', methods=['POST'])
def write():
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")
    astro_body = request.form.get('astro_body')
    date_entered = request.form.get('date_entered')
    time_entered = request.form.get('time_entered')
    latitude_entered = request.form.get('latitude')
    longitude_entered = request.form.get('longitude')
    global body_image
    global body_color
    if astro_body.capitalize() not in astro_bodies:
        body_image = body_images['System']
        body_color = ''
        astro_data[0] = 'You must enter an astronomical body within our solar system!'
        for i in range(1, len(astro_data)):
            astro_data[i] = ''
    else:
        astro_body = astro_body.capitalize()
        body_color = body_colors[astro_body]
        body_image = body_images[astro_body]
        astro_data[0] = f'Astronomical body = {astro_body}'
        if date_entered == '':
            astro_data[1] = f'Date entered = {current_date}'
        else:
            astro_data[1] = f'Date entered = {date_entered}'
            current_date = date_entered
        if time_entered == '':
            astro_data[2] = f'Time entered = {current_time}'
        else:
            astro_data[2] = f'Time entered = {time_entered}'
            current_time = time_entered
        if latitude_entered == '':
            latitude, longitude = get_observer_location()
            astro_data[3] = f'Latitude = {latitude}'
        else:
            astro_data[3] = f'Latitude = {latitude_entered}'
            latitude = latitude_entered
        if longitude_entered == '':
            latitude, longitude = get_observer_location()
            astro_data[4] = f'Longitude = {longitude}'
        else:
            astro_data[4] = f'Longitude = {longitude_entered}'
            longitude = longitude_entered
        elevation = get_observer_elevation(latitude, longitude)
        azimuth, altitude, from_earth, magnitude = get_body_position(latitude, longitude, elevation, astro_body, current_date, current_time)
        magnitude = round(float(magnitude), 2)
        from_earth = '{:,}'.format(round(float(from_earth)))
        astro_data[5] = f'Azimuth = {azimuth}'
        astro_data[6] = f'Altitude = {altitude}'
        astro_data[7] = f'Distance from Earth = {from_earth}'
        astro_data[8] = f'Magnitude = {magnitude}'
    return redirect(url_for('index'))

if __name__ == "__main__": 
    app.run(host='0.0.0.0', port=8080)
