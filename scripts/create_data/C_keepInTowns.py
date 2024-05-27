#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Felipe Jordán

DESRIPTION: This script cuts gas leak data to Boston and Cambrdige

INPUTS:
    - data/raw/TownBounderies/TOWNSSURVEY_POLY.shp: Shapefile with town boundaries, obtained from Mass Gov website
    - data/intermediate/GasLeaks_Final.shp: Shapefile with georeferenced gas leaks
        
OUTPUTS:
    - data/final/GasLeaks_Final_SEL.shp: Shapefile with georeferenced gas leaks, only within Boston and Cambridge
    
"""

import pandas as pd
import geopandas as gpd
import os

data_path_raw = os.path.join('data','raw')
data_path_int = os.path.join('data','intermediate')
save_path = os.path.join('data','final')

TownBounderies = gpd.read_file(os.path.join(data_path_raw,'TownBounderies','TOWNSSURVEY_POLY.shp'))
TownBounderies = TownBounderies[TownBounderies.TOWN.isin(['BOSTON','CAMBRIDGE'])]
TownBounderies = TownBounderies[['TOWN','geometry']]
TownBounderies = TownBounderies.dissolve(by='TOWN')
TownBounderies = TownBounderies.to_crs(epsg=3585)
TownBounderies.crs={'init':'epsg:3585'}
towns_area =  TownBounderies.geometry.unary_union #1km buffer

leaks = gpd.read_file(os.path.join(data_path_int,'address_shape','GasLeaks_Final.shp'))
leaks = leaks.loc[leaks.within(towns_area)]
leaks.to_file(os.path.join(save_path,'GasLeaks_Final_SEL.shp'))