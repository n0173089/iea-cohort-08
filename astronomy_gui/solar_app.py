#!/usr/bin/env python3
from flask import Flask, redirect, request, url_for
import requests
import datetime
import logging
import sys

ASTRONOMYAPI_ID="9433cef6-d2ff-487c-a6fa-fb2841bd28e1"
ASTRONOMYAPI_SECRET="bc1928716fc215ea69c6b62ab2c11b4e95103664a7d7098e220e504def4d9553009107e337dc9c00b3aa70f466db2adba45ab94771452700c8841105bb34ee8b5faf491d5a0d3c02e58a8de48217a72bd4d19dc55af1b80e8b2cad017dc09bd4fb9f415205bf6f7473caa6416cef19fb"

logging.basicConfig(stream=sys.stdout, format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

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

astro_data = ['', '', '', '', '', '', '', '', '', '']
body_color = 'white'
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
body_image = 'https://images-assets.nasa.gov/image/PIA03153/PIA03153~thumb.jpg'
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
body_video = 'https://www.youtube.com/embed/libKVRa01L8'
body_videos = {"Sun": "https://www.youtube.com/embed/2HoTK_Gqi2Q", 
                "Moon": "https://www.youtube.com/embed/6AviDjR9mmo", 
                "Mercury": "https://www.youtube.com/embed/0KBjnNuhRHs", 
                "Venus": "https://www.youtube.com/embed/BvXa1n9fjow", 
                "Mars": "https://www.youtube.com/embed/D8pnmwOXhoY", 
                "Jupiter": "https://www.youtube.com/embed/PtkqwslbLY8", 
                "Saturn": "https://www.youtube.com/embed/epZdZaEQhS0", 
                "Uranus": "https://www.youtube.com/embed/m4NXbFOiOGk", 
                "Neptune": "https://www.youtube.com/embed/NStn7zZKXfE", 
                "Pluto": "https://www.youtube.com/embed/-iZio70bd-M",
                "System": "https://www.youtube.com/embed/libKVRa01L8",
                "Fail": "https://www.youtube.com/embed/kdOPBP9vuZA"
                }
astro_bodies = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")


@app.route('/', methods=['GET'])
def index():
    html = """
    <h1>Astrometrics Database</h1>
    <body bgcolor="black">
    <body text="white">
    <font face="verdana, sans-serif">
    <form action="/astro_data" method="post">
        Enter 'Sun', 'Moon', or a planet in our solar system: <input type="text" name="astro_body"><br>
        (Optional) Enter a date in YYYY-MM-DD format: <input type="text" name="date_entered"><br>
        (Optional) If a date was entered above, please enter a time in HH:MM:SS format: <input type="text" name="time_entered"><br>
        (Optional) Enter a latitude: <input type="text" name="latitude"><br>
        (Optional) If a latitude was entered above, please enter a longitude: <input type="text" name="longitude"><br>
        <input type="submit" value="Submit">
    </form>
    Lookup Results: <br />
    <br />
    <p><img src="%(body_image)s" alt="This is where an image would display if you had followed the directions!" width="300" height="300", style="float:right"> 
    <iframe width="300" height="300" src="%(body_video)s" title="YouTube video player" frameborder="0" allow="accelerometer; 
    autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="float:right">
    </iframe></p>
    <br />
    </font>
    <p> 
    <font face="verdana, sans-serif" color="%(body_color)s">
    %(astro_body)s
    </p>
    </font>
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <br />
    <div align="right" >
    *All images courtesy of images.nasa.gov
    </div>

    <br /> <br />
    """   
    user_data = "<br />".join(astro_data)
    return html % {"body_color": body_color, "body_image": body_image, "body_video": body_video, "astro_body": user_data, "date_entered": user_data, 
                "time_entered": user_data, "azimuth": user_data, "altitude": user_data, "from_earth": user_data, "magnitude": user_data, 
                "latitude": user_data, "longitude": user_data}


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
    global body_video
    if astro_body.capitalize() not in astro_bodies:
        body_image = body_images['System']
        body_color = 'white'
        body_video = body_videos['System']
        astro_data[0] = 'You must enter "Sun", "Moon", or a planet within our solar system!'
        for i in range(1, len(astro_data)):
            astro_data[i] = ''
    else:
        try:
            astro_body = astro_body.capitalize()
            body_color = body_colors[astro_body]
            body_image = body_images[astro_body]
            body_video = body_videos[astro_body]
            astro_data[0] = f'Solar system body = {astro_body}'
            if date_entered == '' and time_entered == '':
                astro_data[1] = f'Current Local Date = {current_date}'
                astro_data[2] = f'Current Local Time = {current_time}'
            else:
                astro_data[1] = f'Date Entered = {date_entered}'
                astro_data[2] = f'Time Entered = {time_entered}'
                current_date = date_entered
                current_time = time_entered
            if latitude_entered == '' and longitude_entered == '':
                latitude, longitude = get_observer_location()
                astro_data[3] = f'Your Latitude = {latitude}'
                astro_data[4] = f'Your Longitude = {longitude}'
            else:
                astro_data[3] = f'Latitude Entered = {float(latitude_entered)}'
                astro_data[4] = f'Longitude Entered = {float(longitude_entered)}'
                latitude = latitude_entered
                longitude = longitude_entered
            elevation = get_observer_elevation(latitude, longitude)
            azimuth, altitude, from_earth, magnitude = get_body_position(latitude, longitude, elevation, astro_body, current_date, current_time)
            magnitude = round(float(magnitude), 2)
            from_earth = '{:,}'.format(round(float(from_earth)))
            astro_data[5] = f'Azimuth = {azimuth}'
            astro_data[6] = f'Altitude = {altitude}'
            astro_data[7] = f'Elevation = {elevation} m'
            astro_data[8] = f'Distance from Earth = {from_earth} km'
            astro_data[9] = f'Magnitude = {magnitude}'
        except:
            body_image = ''
            body_color = 'white'
            body_video = body_videos['Fail']
            astro_data[0] = 'You entered invalid data in one or more of the optional fields. Please try again!'
            for i in range(1, len(astro_data)):
                astro_data[i] = ''
    return redirect(url_for('index'))

if __name__ == "__main__": 
    app.run(host='0.0.0.0', port=8080)
