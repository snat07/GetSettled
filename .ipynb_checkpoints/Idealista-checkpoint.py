import requests
import base64
import json
import time
import datetime

class Idealista:
    
    search_authorization = ''
    price = 'price'
    propertyType = 'propertyType'
    operation = 'operation'
    rooms = 'rooms'
    neighborhood = 'neighborhood'
    latitude = 'latitude'
    longitude = 'longitude'
    priceByArea = 'priceByArea'
    url = 'url'
    address = 'address'
    thumbnail = 'thumbnail'
    neighborhoods = {}

    def __init__(self):
        #Getting credentials
        with open('../accounts.json') as json_file:
            data = json.load(json_file)


        self.apikey = data['accounts']['Idealista']['apikey']
        secret = data['accounts']['Idealista']['secret']
        access_token = ''
        token_type = ''
        encoded_string = self.apikey + ":" + secret
        encoded = base64.b64encode(encoded_string.encode())

        r = requests.post('http://api.idealista.com/oauth/token',
                      headers={'Authorization': 'Basic ' + encoded.decode()},
                      params={'grant_type':'client_credentials'})
        access_token = r.json()['access_token']
        token_type = r.json()['token_type']
        self.search_authorization =  token_type + ' ' + access_token

    def request_idealista(self, property_type, min_price, max_price, num_page=1):
        params = {
            'locationId':'0-EU-ES-08-13-001-019',
            'locale':'ca',
            'maxItems':50,
            'operation':'rent',
            'propertyType':property_type,
            'apikey':self.apikey,
            'minPrince':min_price,
            'maxPrice':max_price,
            'numPage':num_page
        }
        
        search = requests.post('https://api.idealista.com/3.5/es/search',
                          headers={'Authorization': self.search_authorization},
                          params=params)

        with open(str(datetime.datetime.now().date()) + '_idealista_' + str(num_page) + '.json', 'w') as fp:
            json.dump(search.json(), fp)
        return search.json().get('elementList')

    
    def load_homes(self, property_type='bedrooms', min_price=100, max_price=1500):
        for i in range(1,5):
            homes = self.request_idealista(property_type, min_price, max_price, i)
            time.sleep(1)
            for home in homes:
                if self.neighborhood in home:
                    self.add_item_to_dict(home)
                
                
    def add_item_to_dict(self,home):
        item = { self.price:home[self.price],
                self.propertyType:home[self.propertyType],
                self.operation:home[self.operation],
                self.rooms:home[self.rooms],
                self.latitude:home[self.latitude],
                self.longitude:home[self.longitude],
                self.priceByArea:home[self.priceByArea],
                self.url:home[self.url],
                self.address:home[self.address],
                self.thumbnail:home[self.thumbnail]
            }

        if home[self.neighborhood] not in self.neighborhoods:
            self.neighborhoods[home[self.neighborhood]] = []

        self.neighborhoods[home[self.neighborhood]].append(item)

    def price_of_neighborhoods(self):
        neighs_price = {}
        for key in self.neighborhoods.keys():
            neighs_price[key] = self.price_per_neighborhood(key)
        return neighs_price
    
    def price_per_neighborhood(self,key):
        price_per_neighborhood = 0
        total_number_of_rooms = 0
        for appartment in self.neighborhoods[key]:
            price_per_neighborhood += appartment[self.price]
            total_number_of_rooms += 1
        return (price_per_neighborhood / len(self.neighborhoods[key]), total_number_of_rooms)
    
    def ranking_neighborhood(self):
        ranking = []
        for key in self.neighborhoods:
            ranking.append((key, len(self.neighborhoods[key])))
        return sorted(ranking, key=lambda tup: tup[1], reverse=True)
    
    def neighborhood_locations(self, neighborhood):
        locations = []
        for apt in self.neighborhoods[neighborhood]:
            locations.append((apt['latitude'],apt['longitude']))
        return locations

