#!/usr/bin/env python3
import requests
import datetime
import argparse

parser = argparse.ArgumentParser(description='Find distance of planet from current location')
parser.add_argument('--at', default=datetime.datetime.now().isoformat(timespec = 'seconds'), type=datetime.datetime.fromisoformat, help='Date, given in YYYY-MM-DD format, followed by Time, given in HH:MM:SS format')
parser.add_argument('--from', action='store_true', help='You must follow "--from" with a "lat" and "lon" argument')
subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', help='sub-command help')

parser_lat = subparsers.add_parser('lat', help='lat help')
parser_lat.add_argument('--lat', type=float, help='lat help')

parser_lon = subparsers.add_parser('lon', help='lon help')
parser_lon.add_argument('--lon', type=float, help='lon hep')

parser_body = subparsers.add_parser('body', help='body help')
parser_body.add_argument('--body', default="Sun", help='body help')

sub_args = parser.parse_args(['--lat', '0', '--long', '0', '--body', 'sun'])
args = parser.parse_args()
date = args.at
date_entered = date.strftime("%Y:%m:%d")
time = args.at
time_entered = time.strftime("%H:%M:%S")
lat = args.lat
lon = args.lon
astro_body = args.body

ASTRONOMYAPI_ID="9433cef6-d2ff-487c-a6fa-fb2841bd28e1"
ASTRONOMYAPI_SECRET="bc1928716fc215ea69c6b62ab2c11b4e95103664a7d7098e220e504def4d9553009107e337dc9c00b3aa70f466db2adba45ab94771452700c8841105bb34ee8b5faf491d5a0d3c02e58a8de48217a72bd4d19dc55af1b80e8b2cad017dc09bd4fb9f415205bf6f7473caa6416cef19fb"

def get_observer_location():
    """Returns the longitude and latitude for the geolocation of this machine, based on its IP address."""
    response = requests.get(f'http://ip-api.com/json/?fields={lat},{lon},city,region')
    data = response.json()
    latitude = data['lat']
    longitude = data['lon']
    city = data['city']
    region = data['region']
    return latitude, longitude, city, region


def get_observer_elevation(latitude, longitude):
    """Returns the elevation for the location of this machine."""
    response = requests.get(f'https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}')
    data = response.json()
    elevation = data['results'][0]['elevation']
    return elevation


def get_body_position(latitude, longitude, elevation, astro_body, date_entered, time_entered):
    """Returns the current position of the body in the sky at the specified location"""
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


def print_position(city, region, azimuth, altitude, from_earth, magnitude):
    """Prints the position of the body in the sky using the supplied coordinates"""
    current_date = today.strftime('%B %d, %Y')
    current_time = time.strftime('%I:%M:%S %p')
    from_earth = '{:,}'.format(round(float(from_earth)))
    magnitude = round(float(magnitude), 2)
    print(f'''From {city}, {region} at {current_time} on {current_date}:

    {body}:
        Distance from Earth: {from_earth} km
        Magnitude: {magnitude}
        Position:
            Azimuth: {azimuth}
            Altitude: {altitude}''')


if __name__ == "__main__":
    latitude, longitude, city, region = get_observer_location()
    elevation = get_observer_elevation(latitude, longitude)
    azimuth, altitude, from_earth, magnitude = get_body_position(latitude, longitude, elevation, body)
    print_position(city, region, azimuth, altitude, from_earth, magnitude)