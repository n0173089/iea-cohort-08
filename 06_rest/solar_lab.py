#!/usr/bin/env python3
import requests
import datetime

today = datetime.date.today()
time = datetime.datetime.now()
current_time = time.strftime("%H:%M:%S")
ASTRONOMYAPI_ID="9433cef6-d2ff-487c-a6fa-fb2841bd28e1"
ASTRONOMYAPI_SECRET="bc1928716fc215ea69c6b62ab2c11b4e95103664a7d7098e220e504def4d9553009107e337dc9c00b3aa70f466db2adba45ab94771452700c8841105bb34ee8b5faf491d5a0d3c02e58a8de48217a72bd4d19dc55af1b80e8b2cad017dc09bd4fb9f415205bf6f7473caa6416cef19fb"


def get_observer_location():
    """Returns the longitude and latitude for the location of this machine."""
    response = requests.get('http://ip-api.com/json/136.35.192.52?fields=lat,lon')
    data = response.json()
    latitude = data['lat']
    longitude = data['lon']
    return latitude, longitude


def get_observer_elevation(latitude, longitude):
    """Returns the elevation for the location of this machine."""
    response = requests.get(f'https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}')
    data = response.json()
    elevation = data['results'][0]['elevation']
    return elevation


def get_sun_position(latitude, longitude, elevation):
    """Returns the current position of the sun in the sky at the specified location"""
    params = {"longitude": longitude, "latitude": latitude, "elevation": elevation, "from_date": today, 
            "to_date": today, "time": current_time
    }
    response = requests.get('https://api.astronomyapi.com/api/v2/bodies/positions/sun/', 
                            auth=(ASTRONOMYAPI_ID, ASTRONOMYAPI_SECRET), params=params)
    data = response.json()
    altitude = data['data']['table']['rows'][0]['cells'][0]['position']['horizontal']['altitude']['degrees']
    azimuth = data['data']['table']['rows'][0]['cells'][0]['position']['horizontal']['azimuth']['degrees']
    return azimuth, altitude


def print_position(azimuth, altitude):
    """Prints the position of the sun in the sky using the supplied coordinates"""

    print("The Sun is currently at:", azimuth, 'degrees azimuth,', altitude, 'degrees altitude')


if __name__ == "__main__":
    latitude, longitude = get_observer_location()
    elevation = get_observer_elevation(latitude, longitude)
    azimuth, altitude = get_sun_position(latitude, longitude, elevation)
    print_position(azimuth, altitude)