import pandas as pd
import mplsoccer
import matplotlib.pyplot as plt
import scipy

def plotKDEHeatMap(playerData,
                   fig,
                   ax,
                   orientation='Vertical',
                   pitchType='opta',
                   figSize=(16,8),
                   faceColor='black',
                   pitchColor='black',
                   lineColor='white',
                   nLevels=400,
                   colorMap='hot',
                   colorBar=True,
                   credits=True,
                   creditSize=15):
    if orientation=='Vertical':
        pitch = mplsoccer.VerticalPitch(pitch_type=pitchType, line_zorder=1,
                                        pitch_color=pitchColor,line_color=lineColor,figsize=figSize)
        pitch.draw(ax=ax)

        ax.set_facecolor(faceColor)

        kde = pitch.kdeplot(playerData['x'],playerData['y'],statistic='count',
                                ax=ax,cmap=colorMap,shade=True,shade_lowest=False,
                                n_levels=nLevels,line_width=3,alpha=1,zorder=0.99)
        if credits == True:
            ax.text(1,1,'@barcalytix', ha='right',va='bottom',fontsize=creditSize, color='gray', alpha=0.5, weight='bold')
        
    
    if orientation=='Horizontal':
        pitch = mplsoccer.Pitch(pitch_type=pitchType, line_zorder=1,
                                        pitch_color=pitchColor,line_color=lineColor)
        pitch.draw(ax=ax)

        ax.set_facecolor(faceColor)

        kde = pitch.kdeplot(playerData['x'],playerData['y'],statistic='count',
                                ax=ax,cmap=colorMap,shade=True,shade_lowest=False,
                                n_levels=nLevels,line_width=3,alpha=1,zorder=0.99)
        if credits == True:
            ax.text(100,0,'@barcalytix',va='bottom',ha='right',fontsize=creditSize, color='gray', alpha=0.5,weight='bold')
    
