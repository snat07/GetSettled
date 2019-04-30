import pandas as pd
import requests
import base64
import json


class Idealista:
    
    search_authorization = ''
    price = 'price'
    propertyType = 'propertyType'
    operation = 'operation'
    rooms = 'rooms'
    neighborhood = 'neighborhood'
    latitude = 'latitude'
    longitude = 'longitude'
    distance = 'distance'
    priceByArea = 'priceByArea'
    neighborhoods = {}

   

    def create(self):
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
        print(r)
        access_token = r.json()['access_token']
        token_type = r.json()['token_type']
        self.search_authorization =  token_type + ' ' + access_token
        


#    country = 'es'
#    operation = 'rent'
#    propertyType = 'homes' # 'bedrooms' is other option
#    center = '41.38621,2.15487',
#    locale = 'en'
#    distance = 1300
#    locationId = '0-EU-ES-28' # ver qu es esto
#    maxItems = 50 # 50 as maximun allowed
#    maxPrice = 1000


    def request_idealista(self,locale, maxItems, center, distance, propertyType):

        params = {
            'locale':locale,
            'maxItems':maxItems,
            'operation':'rent',
            'propertyType':propertyType,
            'apikey':self.apikey,
            'center' :center,
            'distance' :distance
        }
        
        search = requests.post('https://api.idealista.com/3.5/es/search',
                          headers={'Authorization': self.search_authorization},
                          params=params)
        return search.json().get('elementList')

    
    def add_item_to_dict(self,home):
        item = { self.price:home[self.price],
                self.propertyType:home[self.propertyType],
                self.operation:home[self.operation],
                self.rooms:home[self.rooms],
                self.latitude:home[self.latitude],
                self.longitude:home[self.longitude],
                self.distance:home[self.distance],
                self.priceByArea:home[self.priceByArea]
            }

        if home[self.neighborhood] not in self.neighborhoods:
            self.neighborhoods[home[self.neighborhood]] = []

        self.neighborhoods[home[self.neighborhood]].append(item)


    
    def load_homes(self, center, distance, locale='en', maxItems=50):
        homes = self.request_idealista(locale, maxItems, center, distance, 'homes')
        bedrooms = self.request_idealista(locale, maxItems, center, distance, 'bedrooms')
        for home in homes:
            self.add_item_to_dict(home)
        for bedroom in bedrooms:
            self.add_item_to_dict(bedroom)

            
    def price_of_neighborhoods(self):
        neighs_price = {}
        for key in self.neighborhoods.keys():
            neighs_price[key] = self.price_per_neighborhood(key)
        return neighs_price
    
    def price_per_neighborhood(self,key):
        price_per_neighborhood = 0
        total_number_of_rooms = 0
        for appartment in self.neighborhoods[key]:
            if appartment[self.propertyType] == 'room':
                price_per_neighborhood += appartment[self.price]
                total_number_of_rooms += 1
            else:
                number_of_rooms = appartment[self.rooms] if appartment[self.rooms] > 0 else 1
                price_per_neighborhood += appartment[self.price] / number_of_rooms
                total_number_of_rooms += appartment[self.rooms]
        return (price_per_neighborhood / len(self.neighborhoods[key]), total_number_of_rooms)

