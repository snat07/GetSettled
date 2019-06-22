import pandas as pd
import telluric as tl
from sklearn import preprocessing
from Idealista import Idealista
from Geofinder import Geofinder
from Utils import *
from Map import draw_map

class Ranking:

    def __init__(self):
        self.distance_weight = 0
        self.availability_weight = 0
        self.security_weight = 0
        self.idealista = Idealista()
        self.geofinder = Geofinder()
    
    def get_ranking(self, address, distance, min_price, 
        max_price, distance_weight=3, 
        availability_weight=3, security_weight=3, n_neighbourhood=3):
        
        # Saving weights 
        self.distance_weight = distance_weight
        self.availability_weight= availability_weight
        self.security_weight = security_weight

        # Getting ranknings
        self.get_distance_ranking(address, distance*83)
        self.get_availability_ranking(min_price, max_price)

        self.aliases = alias_dictionary([i[0] for i in self.distance_ranking],[i[0] for i in self.availability_ranking], 0.25)
        ranking = self.get_ranking_list(self.create_ranking_df(self.aliases), n_neighbourhood).index.values

        return ranking


    def get_ranking_list(self, df, count=3):
        min_max_scaler = preprocessing.MinMaxScaler()
        print(df)
        distance = df[['Distance']].values.astype(float)
        availability = df[['Availability']].values.astype(float)
        security = df[['Security']].values.astype(float)

        distance_normalized = min_max_scaler.fit_transform(distance)
        availability_normalized = min_max_scaler.fit_transform(availability)
        security_normalized = min_max_scaler.fit_transform(security)
        self.df_normalized = pd.DataFrame(index=df.index)
        self.df_normalized['Distance'] = distance_normalized
        self.df_normalized['Availability'] = availability_normalized
        self.df_normalized['Security'] = security_normalized
        self.df_normalized['Ranking'] = self.df_normalized.apply(lambda x: (x['Distance'] * self.distance_weight) + (x['Availability'] * self.availability_weight)
         + (x['Security'] * self.security_weight * -1), axis=1)
        self.df_normalized = self.df_normalized.sort_values('Ranking', ascending=False)
        print(self.df_normalized)
        return self.df_normalized.head(count)

    def get_distance_ranking(self, address, distance):
        self.distance_ranking = self.geofinder.get_neighborhoods(address, distance, self.distance_weight)

    def get_availability_ranking(self, min_price, max_price):
        self.idealista.load_homes(min_price=min_price, max_price=max_price)
        self.availability_ranking = self.idealista.ranking_neighborhood()

    def create_ranking_df(self, aliases):
        distance_values, available_values = self.get_ranking_values(aliases)
        df = pd.DataFrame(distance_values, index=real_list(aliases), columns=['Distance'])
        df['Availability'] = available_values
        df['Security'] = self.get_security_ranking(aliases)
        return df


    def get_security_ranking(self, aliases):
        security_df = pd.read_csv('security_ranking.csv', index_col='name_neighbourhood', usecols=['name_neighbourhood','overall_score'])
        sec_dic = alias_dictionary(real_list(aliases),list(security_df.index), 0.45)
        return security_df.loc[alias_list(sec_dic)].values

    def get_ranking_values(self, aliases):
        distance_values = []
        available_values = []
        for neighborood in real_list(aliases):
            for item in self.distance_ranking:
                if item[0] == neighborood:
                    distance_values.append(item[1])
                    break
            for item in self.availability_ranking:
                if item[0] == aliases[neighborood].text:
                    available_values.append(item[1])
                    break
        
        return distance_values, available_values


    def appartments_locations(self, neighborhoods):
        points = []
        for key in self.aliases:
            if key in neighborhoods:
                points.extend(self.idealista.neighborhood_locations(self.aliases[key].text))
        return points


