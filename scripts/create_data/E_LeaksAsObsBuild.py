# -*- coding: utf-8 -*-
"""
Author:         Felipe Jordan

DESCRIPTION: This code builds for each radio in the radios list a database that construct the independent variables within
a buffer of the each leak.

INPUTS:
    - data/raw/BlocksCensusData/: Census data
    - data/raw/nhgis0004_csv_originalACSdata/: American Community Survey data
    - data/intermediate/MassCensusGeographies: Census geographies
    - data/raw/BostonCambridgeNeighborhoods/: Shapefiles with neighborhoods of Cambridge and Boston
    - data/raw/BNS/bns2008_2010_blockgroups.csv: Boston Neighbohood Survey data
    - data/final/GasLeaks_Final_SEL.shp: Shapefile with leaks
    
OUTPUTS:
    - data/final/leaksAsObs/: Directories with datasets that have leaks as observations for different radii
"""
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import math
from scipy.spatial.distance import cdist

# PREAMBLE ##################################################################################################
# Switches
radios_for_tables = [500]  # Only for this radios the BNS Data is merged, and alternative indexes calculated (takes more time)
radios = range(50,1050,50)

#Paths
data_path = 'data'
save_path = os.path.join(data_path,'intermediate')
save_final = os.path.join(data_path,'final')
block_data_path = os.path.join(data_path,'raw','BlocksCensusData','nhgis0006_ds172_2010_block.csv')
block_data_path_2000 = os.path.join(data_path,'raw','BlocksCensusData','nhgis0007_ds147_2000_block.csv')
block_geography = os.path.join(save_path,'MassCensusGeographies','MA_block_2010.shp')
block_geography_2000 = os.path.join(save_path,'MassCensusGeographies','MA_block_2000.shp')

geography_data = os.path.join(data_path,'raw','nhgis0004_csv_originalACSdata','nhgis0004_ds215_20155_2015_blck_grp.csv')
geography_path = os.path.join(save_path,'MassCensusGeographies','MA_blockGrps_2010.shp')
geography_path_2000 = os.path.join(save_path,'MassCensusGeographies','MA_blockGrps_2000.shp')

CambridgeNeighborhoods = os.path.join(data_path,'raw','BostonCambridgeNeighborhoods','BOUNDARY_CDDNeighborhoods.shp')
BostonNeighborhoods    = os.path.join(data_path,'raw','BostonCambridgeNeighborhoods','boston_regions_planning_districts_bra_1xz.shp')

bns_data = os.path.join(data_path,'raw','BNS','bns2008_2010_blockgroups.csv')

# Towns we are interested in (to define the BG within Cambridge and Boston) #######################################################################
TownBounderies = gpd.read_file(os.path.join(data_path,'raw','TownBounderies','TOWNSSURVEY_POLY.shp'))
TownBounderies = TownBounderies[TownBounderies.TOWN.isin(['BOSTON','CAMBRIDGE'])]
TownBounderies = TownBounderies[['TOWN','geometry']]
TownBounderies = TownBounderies.dissolve(by='TOWN')
TownBounderies = TownBounderies.to_crs(epsg=3585)
TownBounderies.crs={'init':'epsg:3585'}
area =  TownBounderies.geometry.unary_union
    
# Neighborhoods of towns we are interested in (for estimations with fixed effects)
cambridge = gpd.read_file(CambridgeNeighborhoods)
cambridge['geometry'] = cambridge['geometry'].to_crs(epsg=3585)
cambridge.crs={'init':'epsg:3585'}
cambridge = cambridge.loc[:,['NAME','geometry']]
cambridge.columns = ['name','geometry']
cambridge['town']='Cambridge'

boston    = gpd.read_file(BostonNeighborhoods)
boston['geometry'] = boston['geometry'].to_crs(epsg=3585)
boston.crs={'init':'epsg:3585'}
boston = boston.loc[:,['PD','geometry']]
boston.columns = ['name','geometry']
boston['town']='Boston'

OfficialNeighborhoods = cambridge.append(boston,ignore_index=True)

# Geography we are interested in ###############################################################################
geography = gpd.read_file(geography_path)

# Import rest of the data
geo_data = pd.read_csv(geography_data)
variables_abs = ['ADNFE002','ADNFE001', 
                 'ADNCE001','ADNCE002', 'ADNCE003', 'ADNCE006', 'ADNCE009', 'ADNCE012',
                 'ADNCE004','ADNCE007','ADNCE010','ADNCE013'] + list(geo_data.loc[:,'ADMZE001':'ADMZE025'])  # Variables that are cumm stat of each geography
variables_summstat = ['ADOLM001','ADNKM001','ADQTE001'] #Variables that are absolute values of each geography
sel_col = ['GISJOIN']+variables_abs+variables_summstat
geo_data = geo_data[sel_col]

#Coding Educational Levels
geo_data['POP_OVER_25']   = geo_data.loc[:,'ADMZE001']
geo_data['E_DROPOUTS']    = geo_data.loc[:,'ADMZE002':'ADMZE016'].sum(axis=1)
geo_data['E_HIGHSCHOOL']  = geo_data.loc[:,'ADMZE017':'ADMZE018'].sum(axis=1)
geo_data['E_SOMECOLLEGE'] = geo_data.loc[:,'ADMZE019':'ADMZE020'].sum(axis=1)
geo_data['E_ASSOCIATES'] = geo_data.loc[:,'ADMZE021']
geo_data['E_BACHELLORS'] = geo_data.loc[:,'ADMZE022']
geo_data['E_GRADUATE'] = geo_data.loc[:,'ADMZE023':'ADMZE025'].sum(axis=1)

geo_data.drop(list(geo_data.loc[:,'ADMZE001':'ADMZE025']),axis=1,inplace=True)
geo_data.columns=['GISJOIN','FAM_BELOW_POVERTY','TOTAL_FAM',
                  'TOTAL_HH_LENG','LENG1','LENG2','LENG3','LENG4','LENG5',
                  'LENG2_LIM','LENG3_LIM','LENG4_LIM','LENG5_LIM',
                  'PC_INCOME','MEDIAN_HH_INCOME','MEDIAN_CONSTRUCTION_YEAR',
                  'POP_OVER_25','E_DROPOUTS','E_HIGHSCHOOL','E_SOMECOLLEGE','E_ASSOCIATES','E_BACHELLORS','E_GRADUATE']
variables_abs = ['FAM_BELOW_POVERTY','TOTAL_FAM',
                 'TOTAL_HH_LENG','LENG1','LENG2','LENG3','LENG4','LENG5',
                 'LENG2_LIM','LENG3_LIM','LENG4_LIM','LENG5_LIM',
                 'POP_OVER_25','E_DROPOUTS','E_HIGHSCHOOL','E_SOMECOLLEGE','E_ASSOCIATES','E_BACHELLORS','E_GRADUATE'] 
variables_summstat = ['PC_INCOME','MEDIAN_HH_INCOME','MEDIAN_CONSTRUCTION_YEAR'] 
geography = geography.merge(geo_data,how='left',left_on='GISJOIN',right_on='GISJOIN')
geography.set_index('GISJOIN',inplace=True)

# Boston neighborhoods data ###############################################################################
neighborhood = gpd.read_file(geography_path_2000)
neighborhood['gisjoin'] = neighborhood.FIPSSTCO + neighborhood.TRACT + neighborhood.GROUP
neighborhood['gisjoin'] = neighborhood['gisjoin'].astype(np.int64)
# Import rest of the data
n_data = pd.read_csv(bns_data)
neighborhood = neighborhood.merge(n_data,how='inner',left_on='gisjoin',right_on='BG_ID_00')
neighborhood.set_index('GISJOIN',inplace=True)
# BNS VARS
bns_var = ['soccon_0810', 'soccoh_0810', 'SocNet_0810', 'RecipExch_0810', 'IntgenClos_0810', 'ns2', 'NbhdInv_0810']


# Block 2010 geography ###########################################################################################################
block = gpd.read_file(block_geography) 

# Merge with block data:
block_data = pd.read_csv(block_data_path)
keep_columns = ['GISJOIN',
                'H7V001', 
                'H7X002','H7X003','H7X004','H7X005','H7X006','H7X007','H7X008',
                'H7Y002','H7Y003',
                'H7Z003','H7Z004','H7Z005','H7Z006','H7Z007','H7Z008','H7Z009','H7Z010','H7Z001',
                'IFE001','IFE002','IFE003',
                'IFF002','IFF003','IFF004',
                'H76002','H76026']+list(block_data.loc[:,'H76003':'H76025'])+list(block_data.loc[:,'H76027':'H76049'])
block_data = block_data[keep_columns]

#Create age ranges
age_ranges = ['A_0_4','A_5_9','A_10_14','A_15_17','A_18_19','A_20','A_21','A_22_24','A_25_29','A_30_34',
              'A_35_39','A_40_44','A_45_49','A_50_54','A_55_59','A_60_61','A_62_64','A_65_66',
              'A_67_69','A_70_74','A_75_79','A_80_84','A_85_']
i=0
for x in range(3,26):
   if x<10:
       name_m = 'H7600'+str(x)
   else:
       name_m = 'H760'+str(x)
   name_f = 'H760'+str(x+24) 
   block_data[age_ranges[i]]=block_data[name_m]+block_data[name_f] 
   i+=1
block_data.drop(list(block_data.loc[:,'H76003':'H76025'])+list(block_data.loc[:,'H76027':'H76049']),axis=1,inplace=True)
block_data.columns = [ 'GISJOIN',
                       'TOT_POP', 
                       'WHITE','BLACK','NATIVE','ASIAN','HAWAIIAN','OTHER','MULTIPLE',
                       'LATINO','NOT_LATINO',
                       'NL_WHITE','NL_BLACK','NL_NATIVE','NL_ASIAN','NL_HAWAIIAN','NL_OTHER','NL_MULTIPLE','NL_LATINO','NL_TOTAL',
                       'TOT_HOUSE','OCCU_HOUSE','VAC_HOUSE',
                       'OWNED_MORG','OWNED_CLEAN','RENT',
                       'MALE','FEMALE']+age_ranges
block_variables_abs= block_data.columns[1:]
block = block.merge(block_data,how='left',left_on='GISJOIN',right_on='GISJOIN')
block['GISJOIN_blkGroup']=[x[:15] for x in block.GISJOIN]  #Note that 15 is specific to blockgroup data!!!!


# Block geography 2000 ###########################################################################################################
block2000 = gpd.read_file(block_geography_2000)
# Merge with block data:
block_data_2000 = pd.read_csv(block_data_path_2000)
keep_columns = ['GISJOIN','FXS001']
block_data_2000 = block_data_2000[keep_columns]
block_data_2000.columns = [ 'GISJOIN','TOT_POP']
block_data_2000 = block2000.merge(block_data_2000,how='left',left_on='GISJOIN',right_on='GISJOIN')
block_data_2000['GISJOIN_blkGroup']=[x[:15] for x in block_data_2000.GISJOIN]  #Note that 15 is specific to blockgroup data!!!!

########################################## ONE OBSERVATION PER LEAK ######################################
# Importing Leaks Data
leaks = gpd.read_file(os.path.join(save_final,'GasLeaks_Final_SEL.shp'))
leaks['Grade'] = leaks['Grade'].map({'1':1,'1.0':1,'2':2,'2.0':2,'2A':2,'3':3,'3.0':3})
# Before looping through the radios, we calculate some data that is independet of the radio
IndData=pd.DataFrame(index=leaks.index,columns=['CloserGrade1','BlockGroupID','TractID','NeighborhoodName','TownName'])
for leak_index in leaks.loc[leaks.Grade.eq(3)].index:
    #Point
    leak_c = leaks.loc[leak_index,'geometry']
        
    #(1) BG and Census Tract
    #What is the code of the BlockGroup that contains this leak?
    blockGrp_index = geography.loc[geography.geometry.contains(leak_c)].index.values
    #If a block group was identified, save the information
    if len(blockGrp_index)>0:
        IndData.loc[leak_index,'BlockGroupID'] = str(blockGrp_index[0])[:15]
        IndData.loc[leak_index,'TractID'] = str(blockGrp_index[0])[:14]
    else:
        IndData.loc[leak_index,'BlockGroupID'] = np.nan
        IndData.loc[leak_index,'TractID'] = np.nan
            
    #(2) Neighborhood    
    #What is the name of the neighborhood contains the leak?
    contains = OfficialNeighborhoods.loc[OfficialNeighborhoods.geometry.contains(leak_c),['name','town']]
    #If a BG was identified, assign
    if contains.empty:
        IndData.loc[leak_index,['NeighborhoodName','TownName']]  = ['Not Within Neighborhood','Not Within Town']
    else:
        IndData.loc[leak_index,['NeighborhoodName','TownName']] = contains.iloc[0].tolist()
    IndData.loc[2875,['NeighborhoodName','TownName']]    = ['West Cambridge','Cambridge'] # Correction of one leak that falls barely outside
    #(4) #What is the closes grade 1 leak, exluding the leak itself
    grade1_leaks = leaks.loc[leaks.Grade==1 & ~np.isin(leaks.index.values,leak_index),'geometry']
    # leak as simple point 
    point = (leak_c.x,leak_c.y)
    # grade1 leaks as simple points
    Points = [(point.x,point.y) for point in grade1_leaks.tolist() ]
    # min distance
    min_distance = cdist([point],Points).min()
    IndData.loc[leak_index,'CloserGrade1'] = min_distance

race_groups=['NL_WHITE','NL_BLACK','NL_NATIVE','NL_ASIAN','NL_HAWAIIAN','NL_OTHER','NL_MULTIPLE','NL_LATINO']        
from scipy.spatial import distance_matrix
for radio in radios:
    # Buffer for each leak
    buffers = leaks['geometry'].buffer(radio)
    
    # First, form the block data we construct the variable for each leak as the sum of the variables for the blocks
    # that intersect with the buffer. If the block is not entirely contained within the buffer,
    # the variable is assigned proportionally to de area covered by the buffer within the block. This is done in
    # the calculateWeights.py file and here we import the relevant result.
    
    W=pd.read_csv(os.path.join(save_path,'weights','b2010_'+str(radio)+'r.csv'),index_col='Index')
    W.columns = W.columns.values.astype(int)
    
    # With this weights the data at the block level is constructed 
    FinalDataBlocks = pd.DataFrame(columns=block_variables_abs.to_list()+['ENT_IDX','DIS_IDX','ISO_IDX','SPP_IDX','CON_IDX'],index=leaks.index)
    for leak_index in buffers.index:
       # geographic weights
       w = W.loc[leak_index].dropna()
       local_geographies = block.loc[w.index.values,block_variables_abs.to_list()+['geometry']]
       # If the dataframe is empty, then it means leak is outside the area and there is no overlap...
       if pd.DataFrame(local_geographies).empty:
           FinalDataBlocks.loc[leak_index]=['No Overlap' for x in range(len(block_variables_abs)+1)]
       else:    
           local_geographies['w'] = w
           for col in block_variables_abs:
               local_geographies[col]=local_geographies[col].astype(float)*local_geographies['w']
           local_geographies['AREA'] = local_geographies.area*local_geographies['w']
           local_geographies = local_geographies.sort_values('AREA')
           local_geographies_sum = local_geographies.sum()
           
           ## ADD data
           FinalDataBlocks.loc[leak_index,block_variables_abs]=local_geographies_sum[block_variables_abs]
           
           ## ONLY FOR 500 meter
           if radio in radios_for_tables:
               SHARES = local_geographies_sum[race_groups] / local_geographies_sum['NL_TOTAL']
               I = (SHARES*(1-SHARES)).sum()
               
               ### Entropy, Dissimilarity, isolation & residential clustering
               local_geographies.loc[local_geographies['NL_TOTAL'].gt(0),'racial_entropy'] = 0
               Dis=0 #Dissimilarity
               Clu=0 #CLustering
               Iso=0 #Isolation
               Con=0 #Concentration
               
               
               # Distance matrix for residential clustering
               xy = [[x,y] for x,y in zip(local_geographies.geometry.centroid.x,local_geographies.geometry.centroid.y)] 
               D = np.exp(-distance_matrix(xy,xy))
               v = 'NL_TOTAL'
               a=   local_geographies[v][:,np.newaxis]
               sc_t = (a.dot(a.T)*D/local_geographies_sum[v]**2).sum()
               
               for v in race_groups:
                   p = local_geographies[v] / local_geographies['NL_TOTAL']
                   #dissimilarity
                   Dis+=(np.abs(p-SHARES[v])*local_geographies['NL_TOTAL']).sum()/(2*I*local_geographies_sum['NL_TOTAL'])
                   #isolation
                   if (local_geographies_sum[v]>0) and (v!='NL_WHITE'):
                       Iso+=(SHARES[v]/SHARES[1:].sum())*(p*(local_geographies[v]/local_geographies_sum[v])).sum()
                   #entropy
                   p = p.loc[(p>0) & local_geographies['NL_TOTAL'].gt(0)]
                   local_geographies.loc[(p>0) & local_geographies['NL_TOTAL'].gt(0),'racial_entropy'] = local_geographies.loc[(p>0) & local_geographies['NL_TOTAL'].gt(0),'racial_entropy']-p*np.log(p)
                   #clustering
                   if local_geographies_sum[v]>0:
                       a=   local_geographies[v][:,np.newaxis]
                       sc_v = (a.dot(a.T)*D/local_geographies_sum[v]**2).sum()
                       Clu+=(local_geographies_sum[v]*sc_v)/(local_geographies_sum['NL_TOTAL']*sc_t)
                       
                   #Concentration
                   if (local_geographies_sum[v]>0) and (v!='NL_WHITE'):
                       n1=np.where(local_geographies['NL_TOTAL'].cumsum()>=local_geographies_sum[v])[0][0]
                       n2=len(local_geographies['NL_TOTAL'])-np.where(np.flip(local_geographies['NL_TOTAL'].cumsum())>=local_geographies_sum['NL_WHITE'])[0][0] #This is ambiguous in the paper. The correct n2 must be using the mayority to get a consistent estimate with what is described
                       Con+=(((local_geographies[v]*local_geographies['AREA']/local_geographies_sum[v]).sum() / (local_geographies['NL_WHITE']*local_geographies['AREA']/local_geographies_sum['NL_WHITE']).sum()-1) / ((local_geographies[0:n1+1]['NL_TOTAL']*local_geographies[0:n1+1]['AREA']/local_geographies[0:n1+1]['NL_TOTAL'].sum()).sum()/(local_geographies[n2-1:]['NL_TOTAL']*local_geographies[n2-1:]['AREA']/local_geographies[n2-1:]['NL_TOTAL'].sum()).sum()-1)) * (SHARES[v]/SHARES[1:].sum())
                       
               e=0
               for v in race_groups:
                   p = local_geographies_sum[v] / local_geographies_sum['NL_TOTAL']
                   if p>0:
                       e = e-p*np.log(p)
               ENT_IDX= local_geographies['NL_TOTAL']*(e-local_geographies['racial_entropy'])/(e*local_geographies_sum['NL_TOTAL'])
           
           
               FinalDataBlocks.loc[leak_index,'ENT_IDX']     = ENT_IDX.sum()
               FinalDataBlocks.loc[leak_index,'DIS_IDX']     = Dis
               FinalDataBlocks.loc[leak_index,'SPP_IDX']     = Clu
               FinalDataBlocks.loc[leak_index,'ISO_IDX']     = Iso
               FinalDataBlocks.loc[leak_index,'CON_IDX']     = Con
    
    # Second, for the variables AT THE BLOCK GROUP LEVEL that are absolute numbers for which summary statistics can be calculated (e.g: total number
    # of poor families), the total number on the buffer is calculated as sum of the total number of each geography that intersects the buffer weigthed 
    # by the attributed population in the intersection over the total population of the geometry. This weights do not sum up to 1.
    
    #First we will need to calculated the total population in each geography form the block data:
    pop_by_geography = pd.DataFrame(block.TOT_POP.groupby(block['GISJOIN_blkGroup']).sum())     
    geography2 = geography.merge(pop_by_geography,how='left',left_index=True,right_index=True)
    # Now we get the population weight for each geography
    weights=[]
    for leak_index in buffers.index:
        # geographic weights
        w = W.loc[leak_index].dropna()
        # population to be considered from each block
        pop = block.loc[w.index.values,'TOT_POP']*w
        #aggregate population by blockgroup
        pop_blkGrp = pd.DataFrame(pop.groupby(block.loc[w.index.values,'GISJOIN_blkGroup']).sum())
        pop_blkGrp.columns=['POP_INTER']
        #total population of each blockgroup
        total_pop_blkGrp = pd.DataFrame(geography2.loc[pop_blkGrp.index.values,'TOT_POP'])
        POP = pop_blkGrp.merge(total_pop_blkGrp,how='left',left_index=True,right_index=True)
        #The final weights:
        weights.append(POP.POP_INTER/POP.TOT_POP)
     
    FinalDataBlkGr_abs = pd.DataFrame(columns=variables_abs,index=leaks.index)
    for leak_index in buffers.index:
        local_geographies = geography2.loc[weights[leak_index].index.values,variables_abs]
        # If the dataframe is empty, then it means leak is well outside the area and there is no overlap...
        if pd.DataFrame(local_geographies).empty:
            FinalDataBlkGr_abs.loc[leak_index]=['No Overlap' for x in range(len(variables_abs))]
        else:    
            local_geographies['w'] = weights[leak_index]
            for col in variables_abs:
                local_geographies[col]=local_geographies[col].astype(float)*local_geographies['w']
            local_geographies = local_geographies.sum()
            FinalDataBlkGr_abs.loc[leak_index]=local_geographies[variables_abs]   
        
        
    # Third, for the variables that are a summary statistic in each geography (e.g. median income),
    # we determine which are the geometries that intersect with the buffer and calculate weights based on 
    # the total population of the intersection between the buffer and the geometry as a fraction of the total population in the buffer. 
    # This weights sum up to 1. 
            
    weights=[]
    for leak_index in buffers.index:
        # geographic weights
        w = W.loc[leak_index].dropna()
        # population to be considered from each block
        pop = block.loc[w.index.values,'TOT_POP']*w   
        #aggregate population by blockgroup
        pop_blkGrp = pd.DataFrame(pop.groupby(block.loc[w.index.values,'GISJOIN_blkGroup']).sum())
        pop_blkGrp.columns=['POP_INTER']
        #total population in the buffer
        total = pop_blkGrp.POP_INTER.sum()
        #The final weights:
        weights.append(pop_blkGrp.POP_INTER/total)    
                
    #Variables that are going to be constructed for each leak    
    FinalDataBlkGr_sum = pd.DataFrame(columns=variables_summstat,index=leaks.index)
    for leak_index in buffers.index:
        local_geographies = geography2.loc[weights[leak_index].index.values,variables_summstat]
        # If the dataframe is empty, then it means leak is well outside the area and there is no overlap...
        if pd.DataFrame(local_geographies).empty:
            FinalDataBlkGr_sum.loc[leak_index]=['No Overlap' for x in range(len(variables_summstat))]
        else:    
            local_geographies['w'] = weights[leak_index]
            for col in variables_summstat:
                local_geographies[col]=local_geographies[col].astype(float)*local_geographies['w']
            local_geographies = local_geographies.sum()
            FinalDataBlkGr_sum.loc[leak_index]=local_geographies[variables_summstat]
    
    # The same for the neigborhoods' boston data    
    if radio in radios_for_tables:
        W2000=pd.read_csv(os.path.join(save_path,'weights','b2000_'+str(radio)+'r.csv'),index_col='Index')
        W2000.columns = W2000.columns.values.astype(int)
        FinalNeigh = pd.DataFrame(columns=bns_var,index=leaks.index)
        for leak_index in buffers.index:
            # geographic weights
            w = W2000.loc[leak_index].dropna()
            # population to be considered from each block
            pop = block_data_2000.loc[w.index.values,'TOT_POP']*w
            #For each column in the BNS DATA, only consider block groups that are not null in the BNS Data
            for col in bns_var:
                # Which block groups are not empty
                bg_notnan = block_data_2000[block_data_2000.GISJOIN_blkGroup.isin(neighborhood[~neighborhood[col].isnull()].index.values)].index.values
                pop = pop[pop.index.isin(bg_notnan)]
                #aggregate population by blockgroup
                pop_blkGrp = pd.DataFrame(pop.groupby(block_data_2000.loc[w.index.values,'GISJOIN_blkGroup']).sum())
                pop_blkGrp.columns=['POP_INTER']
                #total population in the buffer
                total = pop_blkGrp.POP_INTER.sum()
                #The final weights:
                weight = (pop_blkGrp.POP_INTER/total) 
                #Import the geography
                local_geographies = neighborhood.loc[weight.index.values,col]
                # If the dataframe is empty, then it means leak does not overlapp with a not empty BNS BG...
                if pd.DataFrame(local_geographies).empty or weight.sum()==0:
                    FinalNeigh.loc[leak_index,col]=np.nan
                else:
                    local_geographies = local_geographies.astype(float)*weight
                    local_geographies = local_geographies.sum()/weight.sum()
                    FinalNeigh.loc[leak_index,col]=local_geographies


    # Fourth, we calculate the number of 1,2 and 3 leaks within the radio of the buffer
    DataFrameGrades=pd.DataFrame(index=leaks.index,columns=['Total1','Total2','Total3'])
    for leak_index in buffers.index:
        #The buffer of each leak
        leak = buffers[leak_index] 
        #What are the leaks that fall within that buffer
        leaks_within = leaks.geometry.intersects(leak)
        #Exlude the leak under itself
        leaks_within.loc[leak_index]=False
        #these are the grades of the leaks within the buffer
        grades = leaks.Grade[leaks_within].value_counts().sort_index()
        #Make sure there are zeros in the cases where there are not leaks of certain grade within the buffer
        final_grades=pd.DataFrame(index=[1,2,3]).merge(pd.DataFrame(grades),how='left',left_index=True,right_index=True).fillna(0)
        #Transform the pandas DataFrame into a list
        final_grades = [item for sublist in final_grades.values.tolist() for item in sublist]
        #Save in the database
        DataFrameGrades.loc[leak_index] = final_grades
            
    # We merge all the databases
    if radio in radios_for_tables:
        FinalData = leaks.merge(FinalDataBlocks,how='inner',left_index=True,right_index=True).merge(FinalDataBlkGr_abs,
                               how='inner',left_index=True,right_index=True).merge(FinalDataBlkGr_sum,how='inner',
                               left_index=True,right_index=True).merge(FinalNeigh,how='inner',left_index=True,
                               right_index=True).merge(DataFrameGrades,how='inner',left_index=True,
                               right_index=True).merge(IndData,how='inner',left_index=True,right_index=True)
    else:
        FinalData = leaks.merge(FinalDataBlocks,how='inner',left_index=True,right_index=True).merge(FinalDataBlkGr_abs,
                               how='inner',left_index=True,right_index=True).merge(FinalDataBlkGr_sum,how='inner',
                               left_index=True,right_index=True).merge(DataFrameGrades,how='inner',left_index=True,
                               right_index=True).merge(IndData,how='inner',left_index=True,right_index=True)
                           
    # Drop leaks that do not overlap with any census geography or have zero population:
    FinalData = FinalData[FinalData.TOT_POP!='No Overlap']
    FinalData = FinalData[FinalData.TOT_POP>0]  
    
    #Create Covarietes of interest:
    #1. Ethinc fractionalization index
    ethnic_frac=[]
    for index, row in FinalData.iterrows():
        squares=[]
        for ethnic in ['WHITE', 'BLACK', 'NATIVE', 'ASIAN', 'HAWAIIAN', 'OTHER','MULTIPLE']:
           squares.append((row[ethnic]/row['TOT_POP'])**2)
        frac = 1- np.array(squares).sum()
        ethnic_frac.append(frac) 
    FinalData['ethnic_frac']=ethnic_frac
    #1.2 Ethno-racial fractionalization index
    ethnic_frac=[]
    for index, row in FinalData.iterrows():
        squares=[]
        for ethnic in ['NL_LATINO','NL_WHITE', 'NL_BLACK', 'NL_NATIVE', 'NL_ASIAN', 'NL_HAWAIIAN', 'NL_OTHER','NL_MULTIPLE']:
           squares.append((row[ethnic]/row['NL_TOTAL'])**2)
        frac = 1- np.array(squares).sum()
        ethnic_frac.append(frac) 
    FinalData['ethno_racial_frac']=ethnic_frac  
    #2. Linguistic fractionalization index
    ling_frac=[]
    for index, row in FinalData.iterrows():
        if row['TOTAL_HH_LENG']>0:
            squares=[]
            for ethnic in ['LENG1', 'LENG2', 'LENG3', 'LENG4','LENG5']:        
                squares.append((row[ethnic]/row['TOTAL_HH_LENG'])**2)
            frac = 1- np.array(squares).sum()
            ling_frac.append(frac) 
        else:
            ling_frac.append(np.nan)
                
    FinalData['ling_frac']=ling_frac
    FinalData=FinalData[~FinalData.ling_frac.isnull()]

    #3. Dependent variable (repaired or not)
    FinalData['Repaired'] = FinalData.Repaired.map({'Yes':1,'No':0})
    #4. Porvery Rate
    FinalData['poverty_rate'] = [x/y if y>0 else np.nan for (x,y) in zip(FinalData.FAM_BELOW_POVERTY,FinalData.TOTAL_FAM)]
    #5. Black fraction
    FinalData['black_frac']   = FinalData.BLACK/FinalData.TOT_POP
    #6. latino fraction 
    FinalData['latino_frac']   = FinalData.LATINO/FinalData.TOT_POP
    #6.2 limited english fraction
    FinalData['lim_english'] = FinalData.loc[:,'LENG2_LIM':'LENG5_LIM'].sum(axis=1)/FinalData.TOTAL_HH_LENG
    #7. Occu frac. Note: The block with index 2506 has possitive population but no housing units. why?
    FinalData['occu_frac']   =  [x/y if y>0 else np.nan for (x,y) in zip(FinalData.OCCU_HOUSE,FinalData.TOT_HOUSE)]
    #8. Rent fran 
    FinalData['rent_frac']   =  [x/y if y>0 else np.nan for (x,y) in zip(FinalData.RENT,FinalData.OCCU_HOUSE)]
    #9. Log Income 
    FinalData['log_income']   =  FinalData.PC_INCOME.apply(lambda x: math.log(x))
    #10. Log Grade 1 
    FinalData['log_grade1']   =  FinalData.Total1.apply(lambda x: math.log(x+1))
    #11. TOT POPULATION
    FinalData['log_pop']   =  FinalData.TOT_POP.apply(lambda x: math.log(x+1))
    #12. TOT LEAKS
    FinalData['TOTAL_LEAKS']   =  FinalData.loc[:,'Total1':'Total3'].sum(axis=1)
    #13. Log Total Leaks
    FinalData['log_total_leaks']   =  FinalData.TOTAL_LEAKS.apply(lambda x: math.log(x+1))
    #14. average age
    middle_age=[2,7,12,16,18.5,20,21,23,27,32,37,42,47,52,57,60.5,63,65.5,68,72,77,82,89.44]
    FinalData['average_age']=0
    i=0
    for name in age_ranges:
       FinalData['average_age']=FinalData['average_age']+FinalData[name]*middle_age[i] 
       i+=1
    FinalData['average_age']=FinalData['average_age']/FinalData.TOT_POP
    #15. Fraction female
    FinalData['female_frac']   = FinalData.FEMALE/FinalData.TOT_POP
    #16 Fraction of different educational levels
    for edu in ['E_DROPOUTS', 'E_HIGHSCHOOL', 'E_SOMECOLLEGE','E_ASSOCIATES', 'E_BACHELLORS', 'E_GRADUATE']:
        FinalData[edu.lower()+'_frac'] = FinalData[edu]/FinalData['POP_OVER_25']
    #17 Log of closer distance to leak1   CloserGrade1
    FinalData['log_closer_g1']   = FinalData['CloserGrade1'].apply(lambda x: math.log(x+1))

    
    #Save csv data
    ExData =FinalData.copy()
    del ExData['geometry']
    ExData.to_csv(os.path.join(save_final,'leaksAsObs','LeaksData_Radio_'+str(radio)+'.csv'))  
    
    print('Leaks Data for radio '+ str(radio) +'Saved in '+ save_final)