#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 23:09:49 2024

@author: felipe
"""
##### DESRIPTIVE STATS OF TABLE 1
import pandas as pd
import geopandas as gpd
import os

save_path = os.path.join('data','final')

leaks = gpd.read_file(os.path.join(save_path,'GasLeaks_Final_SEL.shp'))
leaks['City'] = leaks.Town.eq('CAMBRIDGE').map({True:'CAMBRIDGE',False:'BOSTON'})
leaks['Grade_int'] = leaks.Grade.astype(str).map({'1':1,'2':2,'2A':2,'3':3,'1.0':1,'2.0':2,'3.0':3})
leaks_summ = pd.DataFrame(leaks[['City','Repaired','Grade_int']].groupby(['City','Grade_int','Repaired']).size())
