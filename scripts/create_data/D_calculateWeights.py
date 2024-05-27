# -*- coding: utf-8 -*-
"""
@author: Felipe Jordán


DESRIPTION: For each radio around a leak, calculates area-based weights in blocks that intersect radio.
            Optionally, the code also clip the census geographies to the study area (useful for the first run).
            
INPUTS:
    - data/final/GasLeaks_Final_SEL.shp: Shapefile with georeferenced gas leaks, only within Boston and Cambridge
    - data/raw/MassCensusGeographies/: Directory containing shapefiles of different census geographies (block & block group), for 2000 y 2010 censuses
    
OUTPUTS:
    -data/intermediate/weights/: csvs with area-based weights for different buffers

"""
import pandas as pd
import geopandas as gpd
import os

# PREAMBLE ##################################################################################################
ClipBlockGeography = True # Set to True if clipping census geographies to Boston and Cambridge2. Should be done the first time that is run to save clipped data
w2000 = True
w2010 = True

# Radio of buffer around each leak
#old_rad = [x for x in range(50,525,25)]
#radios  = [x if (x in old_rad)==0 else 0 for x in range(55,505,10)]
#radios  = list(filter(lambda x: x!= 0, radios))
radios = range(50,1050,50)


#Paths
data_path    = os.path.join('data','raw') 
b_2010_path  = os.path.join(data_path,'MassCensusGeographies','MA_block_2010.shp')
b_2000_path  = os.path.join(data_path,'MassCensusGeographies','MA_block_2000.shp')
bg_2010_path = os.path.join(data_path,'MassCensusGeographies','MA_blck_grp_2010.shp')
bg_2000_path = os.path.join(data_path,'MassCensusGeographies','MA_blck_grp_2000.shp')
save_path = os.path.join('data','intermediate')

# Clipping block level data to study area
if ClipBlockGeography:
    # Towns we are interested in (to clip) #######################################################################
    TownBounderies = gpd.read_file(os.path.join(data_path,'TownBounderies','TOWNSSURVEY_POLY.shp'))
    TownBounderies = TownBounderies[TownBounderies.TOWN.isin(['BOSTON','CAMBRIDGE'])]
    TownBounderies = TownBounderies[['TOWN','geometry']]
    TownBounderies = TownBounderies.dissolve(by='TOWN')
    TownBounderies = TownBounderies.to_crs(epsg=3585)
    TownBounderies.crs={'init':'epsg:3585'}
    towns_area0 = TownBounderies.geometry.unary_union
    towns_area =  towns_area0.buffer(1000) #1km buffer
    
    #Select BGs that intersect with the area and define study area form blocks
    #2010
    if w2010:
        bg_2010 = gpd.read_file(bg_2010_path)
        bg_2010['geometry'] = bg_2010['geometry'].to_crs(epsg=3585)
        bg_2010.crs={'init':'epsg:3585'}
        bg_2010 = bg_2010[bg_2010.intersects(towns_area)]
        bg_2010.to_file(os.path.join(save_path,'MassCensusGeographies','MA_blockGrps_2010.shp'))
        bg_2010_area = bg_2010.geometry.unary_union
    #2000
    if w2000:
        bg_2000 = gpd.read_file(bg_2000_path)
        bg_2000['geometry'] = bg_2000['geometry'].to_crs(epsg=3585)
        bg_2000.crs={'init':'epsg:3585'}
        bg_2000 = bg_2000[bg_2000.intersects(towns_area)]
        bg_2000.to_file(os.path.join(save_path,'MassCensusGeographies','MA_blockGrps_2000.shp'))
        bg_2000_area = bg_2000.geometry.unary_union

    # Clipping Blocks
    #2010
    if w2010:
        b_2010 = gpd.read_file(b_2010_path)
        b_2010['geometry'] = b_2010['geometry'].to_crs(epsg=3585)
        b_2010.crs={'init':'epsg:3585'}
        b_2010 = b_2010[b_2010.centroid.within(bg_2010_area)]
        b_2010.to_file(os.path.join(save_path,'MassCensusGeographies','MA_block_2010.shp'))  
    #2000
    if w2000:
        b_2000 = gpd.read_file(b_2000_path)
        b_2000['geometry'] = b_2000['geometry'].to_crs(epsg=3585)
        b_2000.crs={'init':'epsg:3585'}
        b_2000 = b_2000[b_2000.centroid.within(bg_2000_area)]
        b_2000.to_file(os.path.join(save_path,'MassCensusGeographies','MA_block_2000.shp'))
    

if w2010:
    b_2010 = gpd.read_file(os.path.join(save_path,'MassCensusGeographies','MA_block_2010.shp'))
if w2000:
    b_2000 = gpd.read_file(os.path.join(save_path,'MassCensusGeographies','MA_block_2000.shp'))
    
    
# Importing Leak Data
leaks = gpd.read_file(os.path.join('data','final','GasLeaks_Final_SEL.shp'))

# For each leak, generate weights of each block. The weight is equal to the area of the block contained un the buffer
for radio in radios:
    buffers = leaks['geometry'].buffer(radio)
    # 2010
    if w2010:
        weights=[]
        for leak in buffers:
            #get the block that intersects the buffer
            inter_block = b_2010.loc[b_2010.intersects(leak),'geometry']
            #get the area of those geometries
            inter_block_area = inter_block.area
            #get the area of those geometries that intersects with the buffer 
            inter_block_inter_area = inter_block.intersection(leak).area
            #
            weights.append(inter_block_inter_area/inter_block_area)
        W=pd.DataFrame(weights)
        W.index.names=['Index']
        W.to_csv(os.path.join(save_path,'weights','b2010_'+str(radio)+'r.csv'))
        print ("2010 Blocks for radio "+str(radio)+" Weights Saved")
    # 2000
    if w2000:
        weights=[]
        for leak in buffers:
            #get the block that intersects the buffer
            inter_block = b_2000.loc[b_2000.intersects(leak),'geometry']
            #get the area of those geometries
            inter_block_area = inter_block.area
            #get the area of those geometries that intersects with the buffer 
            inter_block_inter_area = inter_block.intersection(leak).area
            #
            weights.append(inter_block_inter_area/inter_block_area)
        W=pd.DataFrame(weights)
        W.index.names=['Index']
        W.to_csv(os.path.join(save_path,'weights','b2000_'+str(radio)+'r.csv'))
        print ("2000 Blocks for radio "+str(radio)+" Weights Saved")
    
    
    
    
    