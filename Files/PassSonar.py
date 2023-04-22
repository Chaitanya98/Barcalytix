import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval


def PassAngleExtractor(qual_list):
    qual_list = eval(qual_list)
    for x in qual_list:
        if x['type'] == 'Angle':
            angle = float(x['value'])+(np.pi/2)
            if angle > np.pi :
                return angle - 2*np.pi
            else:
                return angle

def PassLengthExtractor(qual_list):
    qual_list = eval(qual_list)
    for x in qual_list:
        if x['type'] == 'Length':
            return x['value']

def plotSonar(playerPassData,
              ax,
              nbins=20,
              colorMap=plt.cm.hot_r,
              background='black',
              Width=0.3):
    
    playerPassData['PassAngle'] = [PassAngleExtractor(x) for x in list(playerPassData['qualifiers'])]
    playerPassData['PassAngle'] = playerPassData['PassAngle'].astype(float)
    playerPassData['PassLength'] = [PassLengthExtractor(x) for x in list(playerPassData['qualifiers'])]
    playerPassData['PassLength'] = playerPassData['PassLength'].astype(float)
    
    sonar_df = playerPassData[['PassAngle','PassLength']]
    
    bins = np.linspace(sonar_df['PassAngle'].min(), sonar_df['PassAngle'].max(), nbins)
    
    sonar_df['binned'] = pd.cut(playerPassData['PassAngle'],bins,include_lowest=True)
    sonar_df['Bin_Mids'] = sonar_df['binned'].apply(lambda x: x.mid)
    
    x = sonar_df.groupby('Bin_Mids',as_index=False)['PassLength'].mean()
    y = sonar_df.groupby('Bin_Mids',as_index=False)['Bin_Mids'].count()
    y.columns = ['nPasses']
    
    norm = plt.Normalize(vmin=y['nPasses'].min(), vmax=y['nPasses'].max())
    colors = colorMap(norm(y['nPasses']))
    
#     ax = plt.subplot(111,projection='polar')
    theta = x["Bin_Mids"]
    radii = x["PassLength"]
    bars = ax.bar(theta, radii, width=Width, bottom=0.0,color=colors)
    ax.set_xticklabels([])
    ax.set_yticks([])
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    ax.spines['polar'].set_visible(False)
    for r, bar in zip(theta, bars):
            bar.set_alpha(1)

    ax.set_facecolor(background)
