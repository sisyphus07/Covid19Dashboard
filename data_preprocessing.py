# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import requests
from sqlalchemy import create_engine
import pymysql
import pandas as pd
import sys




df = pd.read_csv("veriler/covid_19_data.csv")

df = df.rename(columns = {"Country/Region" : "Country" ,  "ObservationDate" : "Date"})
df.drop(columns = ["SNo","Province/State","Last Update"],inplace = True)




ulke = df[df["Country"] == "Turkey"]
#gunluk vaka
new_cases = pd.read_csv("veriler/new_cases.csv")
new_deaths = pd.read_csv("veriler/new_deaths.csv")

ulke1 = "Turkey"
ulke = new_cases.loc[:,["date",ulke1]]
print(ulke.iloc[:,1])



df['Country'] = df['Country'].replace('Mainland China', 'China')
ulkeler = df["Country"].unique()

#yeni kolonlar
us = df[df.Country == "US"].groupby('Date')[['Confirmed','Deaths','Recovered']].sum()
cin = df[df.Country == "China"].groupby('Date')[['Confirmed','Deaths','Recovered']].sum()
uk = df[df.Country == "UK"].groupby('Date')[['Confirmed','Deaths','Recovered']].sum()
fr = df[df.Country == "France"].groupby('Date')[['Confirmed','Deaths','Recovered']].sum()
aust = df[df.Country == "Australia"].groupby('Date')[['Confirmed','Deaths','Recovered']].sum()

df = df[(df.Country != "US") & (df.Country != "UK") & (df.Country != "China") & (df.Country != "France") & (df.Country != "Australia")]

us_ad = []
uk_ad = []
aust_ad = []
fr_ad = []
cin_ad = []

for i in range(len(us.index)):
    i = "US"
    us_ad.append(i)

for i in range(len(cin.index)):
    i = "China"
    cin_ad.append(i)    
    
for i in range(len(uk.index)):
    i = "UK"
    uk_ad.append(i)
    
for i in range(len(fr.index)):
    i = "France"
    fr_ad.append(i)
    
for i in range(len(aust.index)):
    i = "Australia"
    aust_ad.append(i)


#isimleri ekle 
    
    


us["Country"] = us_ad 
uk["Country"] = uk_ad
cin["Country"] = cin_ad
fr["Country"] = fr_ad
aust["Country"] = aust_ad


us.reset_index(inplace=True)
uk.reset_index(inplace=True)
cin.reset_index(inplace=True)
fr.reset_index(inplace=True)
aust.reset_index(inplace=True)


#orijinal verilere ekle 


df = pd.concat([us,uk,cin,fr,aust,df],axis = 0)


#yas cinsiyet verisi
yas_cinsiyet = pd.read_csv("veriler/COVID19_line_list_data.csv")
yas_cinsiyet = yas_cinsiyet.loc[:,["gender","age","death"]]

#vaka
vaka_yas_cinsiyet = yas_cinsiyet[yas_cinsiyet["death"] == "0" ]

#olen
olen_yas_cinsiyet = yas_cinsiyet[yas_cinsiyet["death"] == "1" ]


#veri temizleme 




#iylesenleri topla 
recovered_df = df.groupby(["Country"]).sum()
recovered_df.reset_index(inplace = True)
recovered_df.drop(["Confirmed","Deaths"],axis = 1,inplace = True)



#konum verisi
df_location = requests.get("https://coronavirus-tracker-api.herokuapp.com/v2/locations")
df_location = pd.DataFrame(df_location.json()["locations"])






lon = []
lat = []

for i in df_location["coordinates"]:
    lon.append(i["longitude"])
    lat.append(i["latitude"])
    
df_location["lon"] = pd.DataFrame(lon)
df_location["lat"] = pd.DataFrame(lat)


confirmed = []
confirmed_size = []
deaths = []
deaths_size = []
recovered_size = recovered_df["Recovered"]/10000



for i in df_location["latest"]:
    confirmed.append(i["confirmed"])
    confirmed_size.append(int(i["confirmed"])/2000)
    deaths.append(i["deaths"])
    deaths_size.append(int(i["deaths"])/1000)
    
    


    
df_location["confirmed"] = pd.DataFrame(confirmed)
df_location["confirmed_size"] = pd.DataFrame(confirmed_size)
df_location["deaths"] = pd.DataFrame(deaths)
df_location["deaths_size"] = pd.DataFrame(deaths_size)
#df_location["recovered_size"] = pd.DataFrame(recovered_size)
#recovered verilerini ekleme 
#df_location["recovered"] = recovered_df



#eksi degerleri silme 

df_location =df_location[(df_location['confirmed'] > 0)]
df_location =df_location[(df_location['deaths'] > 0)]

df_location = df_location.loc[:,["country","lon","lat","confirmed","confirmed_size","deaths","deaths_size"]]


#gunleri duzeltme 

ulkeler1 = df["Country"].unique()

df_ulkeler = []

for i in ulkeler1:
    ulke = df[df["Country"] == i]
    df_ulkeler.append(ulke)
    

frames = []

for i in df_ulkeler:
    i.reset_index(inplace = True)
    i["Days Since"] = i.index
    frames.append(i)
    

df = pd.concat(frames)











#vertabanına donusturme  df,df_location,vaka_yas_cinsiyet,olen_yas_cinsiyet

tableName = "kumulatif_veriler"
sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/koronavirus', pool_recycle=3600)
dbConnection = sqlEngine.connect()

try:

    frame = df.to_sql(tableName, dbConnection, if_exists='fail');

except ValueError as vx:

    print(vx)

except Exception as ex:   

    print(ex)

else:

    print("Table %s created successfully."%tableName);   

finally:

    dbConnection.close()



dict1 = {'m': 2, 'n': 4,"k" : 5}
dict2 = {'n': 3, 'm': 1,"y" : 8}

def mergeDicts(dict1,dict2):
    d = {}
    for c in dict1.keys():
        if c in dict2.keys():
            d[c] = dict1[c],dict2[c]
        else:
            d[c] = dict1[c]
    return d
            


mergeDicts(dict1,dict2)


d = {5:3}
key = 5
value = 12

d[5]


def multiAdd(d,key,value):
    d[key] = value
    c = {}

    for i in d:
        for j in i:
            if j in c:
                c[j] += {}


multiAdd(d,key,value)














