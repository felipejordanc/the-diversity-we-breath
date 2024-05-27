# -*- coding: utf-8 -*-
"""
@author: Felipe Jordán

DESRIPTION: This script loads gas leaks data and georeference the data using google API

INPUTS:
    - data/raw/gasLeaks/: Gas Leaks in Boston and Cambridge for 2016. KML files downloaded from HEET webpage
    - data/raw/gasLeaks_aux/: To auxiliary datasets used to georeference. 
        - find_type_of_road_DONE.xlsx provides the type of road (street, road, court) for intersections that did not have this information. This information was obtained manually on google maps
        - MISSING STREET TYPE - DONE.csv does the same for addresses (no intersection)
        
OUTPUTS:
    - data/intermediate/GasLeaks_Final.shp: Shapefile with georeferenced gas leaks
"""

from bs4 import BeautifulSoup
import pandas as pd
import re
import geopandas as gpd
from geopandas.tools import geocode
from time import sleep
import os

PATH_TO_KEY = ''  ### ADD PATH TO GOOGLE API KEY, NEEDED IN LINE 2015
georef      = False ### FALSE IF NO NEED TO GEOREFERENCE (USEFUL WHEN ADDRESSES HAVE ALREADY BEEN GEOREFERENCED)
rootDir     = os.path.join('data','raw','gasLeaks')
aux_dir     = os.path.join('data','raw','gasLeaks_aux')
save_path   = os.path.join('data','intermediate','address_shape')

##############################################################
# 1. Extract data from kml files
##############################################################
#CAMBRIDGE
#kmlFile = r'\Cambridge, MA - Eversource Reported Gas Leaks.kml' 
kmlFile = r'Cambridge, MA - Eversource Reported Gas Leaks.kml' 
with open(os.path.join(rootDir,kmlFile), encoding='utf8') as f:
    s = BeautifulSoup(f, 'xml')
folders = s.find_all('Folder')

#Leaks Repaired in 2016
repaired2016 = folders[7]
Repaired2016 = pd.DataFrame(index=range(len(repaired2016.find_all('Placemark'))),columns=['address','Town','State','Cross Street','Date','Grade','Note'])
i=0
for entry in repaired2016.find_all('Placemark'):
    address = str(entry.find('address').string)
    ext    = [str(x.find('value').string) for x in entry.find('ExtendedData').find_all('Data')]  
    Repaired2016.loc[i,'address']=address
    Repaired2016.loc[i,'Town':]=ext
    i+=1
    
#Leaks Unrepaired in 2016
unrepaired2016 = folders[8]
Unrepaired2016 = pd.DataFrame(index=range(len(unrepaired2016.find_all('Placemark'))),columns=['address','Cross Street','Town','State','Grade','Date'])
i=0
for entry in unrepaired2016.find_all('Placemark'):
    address = str(entry.find('address').string)
    ext    = [str(x.find('value').string) for x in entry.find('ExtendedData').find_all('Data')]  
    Unrepaired2016.loc[i,'address']=address
    Unrepaired2016.loc[i,'Cross Street':]=ext
    i+=1

Cambridge_r = Repaired2016
Cambridge_r['Repaired']='Yes'
Cambridge_u = Unrepaired2016
Cambridge_u['Repaired']='No'

#BOSTON
#kmlFile = r'\Boston (whole city), MA - National Grid & Eversource Reported Gas Leaks.kml' 
kmlFile = r'/Boston (whole city), MA - National Grid & Eversource Reported Gas Leaks.kml' 
with open(rootDir + kmlFile, encoding='utf8') as f:
    s = BeautifulSoup(f, 'xml')
folders = s.find_all('Folder') 

 #Leaks Repaired in 2016
repaired2016 = folders[5]
Repaired2016 = pd.DataFrame(index=range(len(repaired2016.find_all('Placemark'))),columns=['address','Leak ID','Cross Street','Town','State','Grade','Date','Note'])
i=0
for entry in repaired2016.find_all('Placemark'):
    address = str(entry.find('address').string)
    ext    = [str(x.find('value').string) for x in entry.find('ExtendedData').find_all('Data')]  
    Repaired2016.loc[i,'address']=address
    Repaired2016.loc[i,'Leak ID':]=ext
    i+=1
    
#Leaks Unrepaired in 2016
unrepaired2016 = folders[6]
Unrepaired2016 = pd.DataFrame(index=range(len(unrepaired2016.find_all('Placemark'))),columns=['address','Leak ID','Cross Street','Town','State','Date','Grade','Note'])
i=0
for entry in unrepaired2016.find_all('Placemark'):
    address = str(entry.find('address').string)
    ext    = [str(x.find('value').string) for x in entry.find('ExtendedData').find_all('Data')]  
    Unrepaired2016.loc[i,'address']=address
    Unrepaired2016.loc[i,'Leak ID':]=ext
    i+=1

Boston_r = Repaired2016
Boston_r['Repaired']='Yes'
Boston_u = Unrepaired2016
Boston_u['Repaired']='No'

## Consolidate
Data=pd.concat([Boston_r,Boston_u,Cambridge_r,Cambridge_u],ignore_index=True)
print("Initial leaks: ",Data.shape)

###################################
# 2. STANDARIZE ADDRESSES
###################################
from unicodedata import normalize
Data['address']=[normalize('NFKC',s) for s in Data.address]
Data['address']=Data['address'].str.upper().str.strip()
Data['address'] = [re.sub(' +',' ',s) for s in Data.address]

#### USE THE SAME ORDER IN ALL TOWNS
# Repaired leaks in Cambride have the name of the town first, correct
Data['Town']=Data['Town'].str.upper()
Data.loc[Data.Town.eq('CAMBRIDGE, 02139'),'Town'] = 'CAMBRIDGE'
Data.loc[Data.Town.eq('CAMBRIDGE') & Data.Repaired.eq('Yes'),'address'] = ['{} CAMBRIDGE MA'.format(s[13:]) for s in Data.loc[Data.Town.eq('CAMBRIDGE') & Data.Repaired.eq('Yes'),'address']]


##### Every address must have a numbers or a cross street (@,at,and,&). Detect and correct
Data['number'] = [bool(re.search('[0-9]',x)) for x in Data.address]
Data['AND'] = [bool(re.search(' (@|AT|AND|&) ',x)) for x in Data.address]

# This are the cases that need to be corrected. They have no number and no AT. We add the @
X = Data.loc[~Data.AND & ~Data.number,['address','Cross Street']]
X['n'] = [len(re.split('( ST | DR | PL | AVE? | RD | PKW?Y | CIRCUIT | WA?Y | SQR? | TER | BLVD | EXWY | HIGHWAY )',s)) for s in X.address]
def addat(s):
    l = re.split('( ST | DR | PL | AVE? | RD | PKW?Y | CIRCUIT | WA?Y | SQR? | TER | BLVD | EXWY | HIGHWAY )',s)
    l.insert(2,'@')
    return ' '.join(l)
X.loc[X.n.eq(5),'corrected_address'] = [addat(s) for s in X.loc[X.n.eq(5),'address']]
X.loc[X.address.eq('WASHINGTON ST ARBORWAY JAMAICA PLAIN MA'),'corrected_address'] =  'WASHINGTON ST @ ARBORWAY JAMAICA PLAIN MA'
X.loc[X.address.eq('HUNTINGTON AVE RIVERWAY ROXBURY MA'),'corrected_address'] =  'HUNTINGTON AVE @ RIVERWAY ROXBURY MA'

Data = Data.merge(X[['corrected_address']],left_index=True,right_index=True,how='left')
Data.loc[Data.AND | Data.number,'corrected_address'] = Data.loc[Data.AND | Data.number,'address']


print("Remove 25 becase they have no number or intersection: ",Data.corrected_address.isna().value_counts())
Data = Data.loc[~Data.corrected_address.isna()]


### REMOVE MA
Data.loc[[s[-2:]!='MA' for s in Data.corrected_address],'corrected_address'] = [s[:-9] for s in Data.loc[[s[-2:]!='MA' for s in Data.corrected_address],'corrected_address']]
Data.loc[[s[-2:]=='MA' for s in Data.corrected_address],'corrected_address'] = [s[:-3] for s in Data.loc[[s[-2:]=='MA' for s in Data.corrected_address],'corrected_address']]

#### Split address from town
towns = Data.Town.value_counts().index        
def addcomma(s):
    l = re.split('( '+'| '.join(towns)+')$',s) 
    return l[0].strip()
Data['corrected_address'] = Data.corrected_address.apply(addcomma)

####### Every address must indicate the type of street (RD, ST, AVE, etc)

## Correct the cases of cross street without type
z = Data.loc[Data.AND,'corrected_address']
corrected = pd.read_excel(os.path.join(aux_dir,'find_type_of_road_DONE.xlsx'),index_col=0)
corrected.fillna('',inplace=True)
corrected['corrected_address'] = corrected.corrected_address.apply(addcomma)
def addave(r):
    l = re.split(' (@|AT|AND|&) ',r['corrected_address'])
    l.insert(1,r['missing 1st'])
    l.append(r['missing 2nd'])  
    return re.sub(' +',' ',' '.join(l)).strip()
corrected['corrected_address'] = corrected.apply(addave,axis=1)
Data.loc[corrected.index,'corrected_address'] = corrected['corrected_address']

####### Cases with street number but no street type.
Data['M'] = [bool(re.search(' (ST E|ST S|ST N|ST W|ROW|CIR|ST|DR|PL|AVE?|RD|PKW?Y|CIRCUIT|WA?Y|SQR?|TER|BLVD|EXWY|HIGHWAY|BROADWAY|ARBORWAY|JAMAICAWAY|CT|PARK|PK|HWY|ROAD|TPKE|RIVERWAY)$',x)) for x in Data.corrected_address]
#F = Data.loc[~Data.M,['corrected_address','Town']]
#F["complete_address"] = F[['corrected_address','Town']].apply(", ".join, axis=1)
#F.to_excel(os.path.join(save_path,'find_type_of_road_all.xlsx'))
fillType = pd.read_csv(os.path.join(aux_dir,'MISSING STREET TYPE - DONE.csv'),index_col=0)

# Remove cases that are ambiguous: 7 cases
Data.drop(fillType.loc[fillType.NOTES.eq('DROP')].index.tolist(),inplace=True)
print('Drop 7 because have no street type and there are two or more streets with the same number (Av, Str); drop 1 in Logan International Airport', Data.shape)
fillType['TYPE'] = fillType['TYPE'].str.upper().fillna('')

### ADD ROAD TYPE WHEN MISSING
Data = Data.merge(fillType[['TYPE']],left_index=True,right_index=True,how='left',indicator=True)
Data.loc[Data._merge.eq('both'),'corrected_address'] = Data.loc[Data._merge.eq('both'),'corrected_address'] + ' ' + Data.loc[Data._merge.eq('both'),'TYPE']

# CORRECT ADDRESS FOR BETTER GEOREF
Data.at[3012,'corrected_address'] = 'BISHOP ALLEN DR @ COLUMBIA ST' 
Data.at[1276,'corrected_address'] = 'AVENUA LOUIS PASTEUR @ FENWAY'

# 9 ADDRESSES THAT ARE IN MATTAPAN, NOT DORCHESTER
Data.loc[(Data.corrected_address.str.contains('GREENFIELD') | Data.corrected_address.str.contains('ROSEWOOD') |
         Data.corrected_address.str.contains('COUNTRYSIDE') | Data.corrected_address.str.contains('DUKE') |
         Data.corrected_address.str.contains('ROCKINGHAM') | Data.corrected_address.str.contains('ALABAMA')) &
         Data.Town.isin(['DORCHESTER','HYDE PARK']),'Town'] = 'MATTAPAN'

### TADDRESSES THAT ARE IN BOSTON
Data.loc[[1114,2371,181,227,892,922],'Town'] = 'BOSTON'

### ADD TOWN, MA, USA
Data['corrected_address'] = Data['corrected_address'].str.strip()
Data['corrected_address'] = Data['corrected_address'] + ', ' + Data['Town'] + ', MASSACHUSETTS, USA'

### Final Correction of Addresses for correct georeferencing
C= pd.Series(['1 Guest St, Boston, MA',  # Does not work with Brighton
                   '33 Bay State Rd, Cambdridge, MA', # 23 does not work. 33 is the same building and works
                   '33 Bay State Rd, Cambdridge, MA',
                   'Hyde Square, Centre St #390-401, Jamaica Plain, MA 02130, United States',
                   '61 ROYAL ST, BOSTON, MASSACHUSETTS, USA',
                   '9 LINDEN ST, BOSTON, MASSACHUSETTS, USA',
                   '75 LINDEN ST, BOSTON, MASSACHUSETTS, USA',
                   '55 LINDEN ST, BOSTON, MASSACHUSETTS, USA',
                   '244 MANCHESTER ST, BOSTON, MASSACHUSETTS, USA'],
                  index=[1464,2700,2918,1980,1459,228,221,1496,429])
                  
Data.loc[C.index,'corrected_address'] = C.to_numpy()
                 
###################################
# 3. GEOREFERENCE
###################################
#### REPLACE WITH LOCAL PATH THAT HAS API KEY. GOOGLE API KEY MUST BE STORED AS GOOGLE_GEOREF_API_KEY=[API_KEY]
if georef:
    with open(PATH_TO_KEY,'r') as file:
        for l in file.readlines():
            k,v  = l.split('=')
            if k=='GOOGLE_GEOREF_API_KEY':
                api_key = v
                
    GC =pd.DataFrame(columns=['geometry','address'])
    for i,D in Data[['corrected_address']].groupby(Data.index//100):
        print(i*100)    
        while True:
            try:
                GC = pd.concat([GC,geocode(D['corrected_address'],provider='Google',api_key=api_key)])
                sleep(5)
                break
            except:
                sleep(5)
                continue
    GC=gpd.GeoDataFrame(GC,crs='epsg:4326')
    GC.to_file(os.path.join(save_path,'GasLeaks_geocoded_google_may24.shp'),index=False)
else:     
    GC = gpd.read_file(os.path.join(save_path,'GasLeaks_geocoded_google_may24.shp'))

## MERGE WITH GEOREFERENCED DATASET. NOTE THAT NEW GEOREFERENCING MIGHT BE DIFFERENT, USE MAY 2024 FILE VERSION (GasLeaks_geocoded_google_may24.shp) FOR REPLICATION
Data.reset_index(inplace=True)
Data2 = Data.merge(GC,left_index=True,right_index=True,how='left')
Data2.set_index('index',inplace=True)

###################################
# 4. CORRECTIONS
###################################

####### OK
#1112: OK, very short street
#1126: Ok, georef address is ambiguous, but coordinate falls in building
#2619: Ok, georef address is ambiguous, but coordinate falls in intersection
#713:  Ok, georef address is ambiguous, but coordinate falls in number
#2279: Ok, georef address is ambiguous, but coordinate falls in intersection
#892:  Ok, georef address is ambiguous, but coordinate falls in intersection
#2818: Ok, number is off but street is so short that does not make a difference

######## DROP ERRORS THAT PERSIST
# Intersections that do not exist
Data2.drop([1371,1517,2631],inplace=True)

# Number out of range of street
Data2.drop([1236,1400,1652,1618],inplace=True)

# Streets that do not exists in their towns
Data2.drop([2397,258],inplace=True)


###################################
# 5. REPROJECT, RENAME, AND SAVE
###################################
Data2.rename(columns={'address_x':'address','corrected_address':'addressStd','address_y':'addressGeo'},inplace=True)
del Data2['number'], Data2['AND'], Data2['M'], Data2['TYPE'], Data2['_merge']  
FinalData = gpd.GeoDataFrame(Data2)
FinalData.reset_index(inplace=True)
FinalData['longitude'] = FinalData.geometry.x
FinalData['latitude']  = FinalData.geometry.y
FinalData['geometry']  = FinalData['geometry'].to_crs(epsg=3585)
FinalData.crs='epsg:3585'
FinalData.to_file(os.path.join(save_path,'GasLeaks_Final.shp'))