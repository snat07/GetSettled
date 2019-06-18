import csv
import time
from collections import Counter
import json
import telluric as tl
from telluric.constants import WGS84_CRS, WEB_MERCATOR_CRS
from geopy.geocoders import Nominatim, Here


class Geofinder:
    
    here = None
    osm = None

    def __init__(self):
        with open('../accounts.json') as json_file:  
            data = json.load(json_file)
        app_code = data['accounts']['Here']['app_code']
        app_id = data['accounts']['Here']['app_id']
        user_agent = data['accounts']['Here']['user_agent']
        self.here = Here(app_code=app_code, app_id=app_id,user_agent=user_agent)
        self.osm = Nominatim(user_agent="get_setlled")

    
    def get_neighborhoods(self, address, distance=1000, weight=3):
        if 'barcelona' not in address.lower():
            address += ', Barcelona'
        self.location = self.here.geocode(address)
        coordinates = self.get_circles_locations(self.location.point, distance, weight)
        pizza_coordinates = []
        for coordinate in coordinates:
            for i in range(4,65,4):
                coord = coordinate[i]
                pizza_coordinates.append([coord[::-1][0],coord[::-1][1]])

        pizza_coordinates.insert(0,[self.location.point.latitude,self.location.point.longitude])
        self.export_coords_to_csv(pizza_coordinates, address)
        pizza_addresses = []
        for coord in pizza_coordinates:
            pizza_addresses.append(self.here.reverse(coord))

        neighborhouds = []
        for suburb in pizza_addresses:
            neighborhouds.append(suburb.raw['Location']['Address']['District'])

        return Counter(neighborhouds).most_common()

        
    def export_coords_to_csv(self, coordinates, name):
        coordinates_copy = coordinates.copy()
        coordinates_copy.insert(0,['lat_dms','lon_dms'])
        with open("../GeoFinder_coords/" + name + ".csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(coordinates_copy)
    
    def get_cirlce_location(self, location, distance):
        return (tl.GeoVector.point(location.longitude, location.latitude)
            .reproject(WEB_MERCATOR_CRS)
            .buffer(distance)
            .to_record(WGS84_CRS)['coordinates'][0]
        )

    def get_circles_locations(self, location, distance, weight):
        weight = 9 - weight
        distance += weight * 120
        coordinates = []
        while distance > 0:
            coordinates.append(self.get_cirlce_location(location, distance))
            distance -= 300
        return coordinates
