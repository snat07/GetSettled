import pandas as pd
import stringdist
import telluric as tl
from sklearn import preprocessing
from Idealista import Idealista
from Geofinder import Geofinder

class Ranking:

    def __init__(self):
        self.distance_weight = 0
        self.availability_weight = 0
        self.security_weight = 0
        self.fc = tl.FileCollection.open("../barris_geo.json")
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
        self.get_distance_ranking(address, distance)
        self.get_availability_ranking(min_price, max_price)

        self.aliases = self.alias_dictionary([i[0] for i in self.distance_ranking],[i[0] for i in self.availability_ranking], 0.25)

        return self.get_ranking_list(self.create_ranking_df(self.aliases), n_neighbourhood).index.values


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
        df = pd.DataFrame(distance_values, index=self.real_list(aliases), columns=['Distance'])
        df['Availability'] = available_values
        df['Security'] = self.get_security_ranking(aliases)
        return df


    def get_security_ranking(self, aliases):
        security_df = pd.read_csv('security_ranking.csv', index_col='name_neighbourhood', usecols=['name_neighbourhood','zscore'])
        sec_dic = self.alias_dictionary(self.real_list(aliases),list(security_df.index), 0.45)
        return security_df.loc[self.alias_list(sec_dic)].values

    def get_ranking_values(self, aliases):
        distance_values = []
        available_values = []
        for neighborood in self.real_list(aliases):
            for item in self.distance_ranking:
                if item[0] == neighborood:
                    distance_values.append(item[1])
                    break
            for item in self.availability_ranking:
                if item[0] == aliases[neighborood].text:
                    available_values.append(item[1])
                    break
        
        return distance_values, available_values

    def alias_dictionary(self, a1, a2, treshold = 0.6):
        aliases = {}
        for nei in a1:
            alias = String_conversion()
            alias.text = nei
            aliases[nei] = alias
            for bar in a2:
                distance = stringdist.levenshtein_norm(nei.lower(),bar.lower())
                if distance < alias.value and distance <= treshold:
                    alias.value = distance
                    alias.text = bar
                    aliases[nei] = alias                
        return aliases   

    def alias_list(self, aliases):
        alias = []
        for key in aliases:
            if aliases[key].value < 1:
                alias.append(aliases[key].text)
        return alias

    def real_list(self, aliases):
        real = []
        for key in aliases:
            if aliases[key].value < 1:
                real.append(key)
        return real

    def alias_values(self, aliases):
        for key in aliases:
            if aliases[key].value >= 0:
                print(key + ' ---- ' + aliases[key].text + ' ----- ' + str(aliases[key].value))

    def show_in_map(self, neighborhoods):
        geo_alias = self.alias_dictionary(neighborhoods,list(self.fc.get_values("N_Barri")))
        return tl.FeatureCollection(barri for barri in self.fc if barri['N_Barri'] in self.alias_list(geo_alias))
    
    

class String_conversion:
    text = ''
    value = 1
