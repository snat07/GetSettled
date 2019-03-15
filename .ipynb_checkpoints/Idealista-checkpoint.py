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
                          headers={'authorization_header': self.search_authorization},
                          params=params)
        return search.json().get('elementList')



    def get_neighborhoods(self, center, distance, locale='en', maxItems=50, propertyType='homes'):
        print(center)
        homes = self.request_idealista(locale, maxItems, center, distance, propertyType)
        neighborhoods = {}
        for home in homes:
            item = { price:home[price],
                    propertyType:home[propertyType],
                    price:home[price],
                    operation:home[operation],
                    rooms:home[rooms],
                    latitude:home[latitude],
                    longitude:home[longitude],
                    distance:home[distance],
                    priceByArea:home[priceByArea]
                }

        if home[neighborhood] not in neighborhoods:
            neighborhoods[home[neighborhood]] = []
            
            neighborhoods[home[neighborhood]].append(item)
        return neighborhoods

#idealista = Idealista()
#idealista.create()
#print(idealista.get_neighborhoods(center='41.38621,2.15487',distance=1500))
