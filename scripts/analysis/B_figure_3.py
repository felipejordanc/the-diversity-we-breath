#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 12:52:39 2024

@author: felipe
"""

import pandas as pd
import os

data_path = r'/Users/felipe/Dropbox/Gas Leaks and Local Cooperation/2024/data'
save_path = data_path+r'/processed'

data = pd.read_csv(os.path.join(save_path,'leaksAsObs','LeaksData_Radio_500.csv'))
data = data.loc[data.Grade.eq(3)]
data.loc[data.Town.eq('CAMBRIDGE'),'City'] = 'Cambridge'
data.loc[data.Town.ne('CAMBRIDGE'),'City'] = 'Boston'

d=data.ethno_racial_frac.describe(percentiles=[.1, .5, .9])
print(d)
import matplotlib.pyplot as plt
import seaborn as sns

# Group the data by City and plot the distribution of ethno_racial_frac
fig, ax = plt.subplots(figsize=(9, 6))
sns.histplot(data=data, x='ethno_racial_frac', ax=ax,bins=20)
ax.axvline(d['mean'], linestyle='--',color='red')
ax.axvline(d['10%'], linestyle='--',color='black')
ax.axvline(d['90%'], linestyle='--',color='black')
ax.text(d['mean'] + 0.01, ax.get_ylim()[1] * 0.9, 'Mean', fontsize=14, color='red')
ax.text(d['10%'] + 0.01, ax.get_ylim()[1] * 0.9, '$1^{st}$ decile', fontsize=14, color='black')
ax.text(d['90%'] + 0.01, ax.get_ylim()[1] * 0.9, '$9^{th}$ decile', fontsize=14, color='black')


# Set plot title and axis labels
ax.set_xlabel('Ethno-Racial Fractionalization', fontsize=14)
ax.set_ylabel('Frequency', fontsize=14)

# Adjust legend and display the plot
fig.tight_layout()
fig.savefig(os.path.join('results','ERF_hist.png'),dpi=300)