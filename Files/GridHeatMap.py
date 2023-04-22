import pandas as pd
import mplsoccer
import matplotlib.pyplot as plt
import scipy

def plotGridHeatMap(playerData,
                    fig,
                    ax,
                    orientation='Vertical',
                    pitchType='opta',
                    figSize=(16,8),
                    faceColor='black',
                    pitchColor='black',
                    lineColor='white',
                    bins=(30,30),
                    colorMap='hot',
                    colorBar=True,
                    credits=True,
                   creditSize=15):
    if orientation=='Vertical':
        pitch = mplsoccer.VerticalPitch(pitch_type=pitchType, line_zorder=2,
                                        pitch_color=pitchColor,line_color=lineColor)
        pitch.draw(ax=ax)
        fig.set_facecolor(faceColor)
        bin_statistic = pitch.bin_statistic(x=playerData['x'],y=playerData['y'],
                                            statistic='count',bins=bins)
        bin_statistic['statistic'] = scipy.ndimage.gaussian_filter(bin_statistic['statistic'],1)
        pitch_hm = pitch.heatmap(bin_statistic,ax=ax,cmap=colorMap,edgecolors=pitchColor)
            
        if colorBar==True:
            cbar = fig.colorbar(pitch_hm,ax=ax,orientation='horizontal',shrink=0.5,pad=0.015)
            cbar.outline.set_edgecolor('white')
            cbar.ax.xaxis.set_tick_params(color='white',labelsize=13)
            cbar.set_ticks([0,bin_statistic['statistic'].max()])
            cbar.set_ticklabels(['Low Density\nOf Actions','High Density\nOf Actions'])
            plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color='white')
        if credits == True:
            ax.text(1,1,'@barcalytix', ha='right',va='bottom',fontsize=creditSize, color='gray', alpha=0.5, weight='bold')
        fig.show()
        
    if orientation=='Horizontal':
        pitch = mplsoccer.Pitch(pitch_type=pitchType, line_zorder=2,
                                pitch_color=pitchColor,line_color=lineColor)
        pitch.draw(ax=ax)
        fig.set_facecolor(faceColor)
        bin_statistic = pitch.bin_statistic(x=playerData['x'],y=playerData['y'],
                                            statistic='count',bins=bins)
        bin_statistic['statistic'] = scipy.ndimage.gaussian_filter(bin_statistic['statistic'],1)
        pitch_hm = pitch.heatmap(bin_statistic,ax=ax,cmap='hot',edgecolors='black')

        if colorBar==True:
            cbar = fig.colorbar(pitch_hm,ax=ax,orientation='horizontal',shrink=0.5,pad=0.015)
            cbar.outline.set_edgecolor('white')
            cbar.ax.xaxis.set_tick_params(color='white',labelsize=15)
            cbar.set_ticks([0,bin_statistic['statistic'].max()])
            cbar.set_ticklabels(['Low Density\nOf Actions','High Density\nOf Actions'])
            plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color='white')
            
        if credits == True:
            ax.text(100,0,'@barcalytix',va='bottom',ha='right',fontsize=creditSize, color='gray', alpha=0.5,weight='bold')

        ax.arrow(25,102.5,50,0,width=0.25, head_width=2.95, head_length=2, overhang=1, color='white')

        fig.show()
