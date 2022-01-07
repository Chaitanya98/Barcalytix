import pandas as pd
import matplotlib.pyplot as plt
import mplsoccer
import numpy as np
from highlight_text import fig_text
from matplotlib.patches import Polygon
from mplsoccer.scatterutils import football_hexagon_marker
from sklearn import preprocessing



def keyPassExtractor(sat_event_list):
    for x in sat_event_list:
        if 'passKey' in x:
            return True
        else:
            continue
        return False
    
def DeadBallExtractor(qual_list):
    for x in qual_list:
        if x['type'] == 'FreekickTaken':
            return True
        elif x['type'] == 'CornerTaken':
            return True
        else:    
            continue
        return False
    
def isProgressivePass(x,y,endX,endY):
    x = x*1.05
    y = y*0.68
    endX = endX*1.05
    endY = endY*0.68
    
    initDistanceFromGoal = np.sqrt(np.square(105-x)+np.square(34-y))
    finalDistanceFromGoal = np.sqrt(np.square(105-endX)+np.square(34-endY))
    
    if (x<=52.5 and endX<=52.5):
        if initDistanceFromGoal - finalDistanceFromGoal > 30:
            return True
    elif (x<=52.5 and endX>52.5):
        if initDistanceFromGoal - finalDistanceFromGoal > 15:
            return True
    elif (x>52.5 and endX>52.5):
        if initDistanceFromGoal - finalDistanceFromGoal > 10:
            return True
    return False

def plotProgPasses(playerPassData,
                   fig,
                   ax,
                   openPlay=False,
                   assistsOn=False,
                   allPasses=True,
                   orientation='Vertical',
                   pitchType='opta',
                   pitchColor='black',
                   lineColor='white',
                   nodeColor='white',
                   faceColor='black',
                   EPV=True,
                   legendSize=15,
                   legendLoc='lower right', 
                   minNodeSize=80,
                   maxNodeSize=200,
                   Legend=False,
                   apColor='#69bbdb',
                   ppColor='red',
                   kpColor='#ffee00'):
    
    if EPV == True:
        MinMaxScaler = preprocessing.MinMaxScaler(feature_range=(0,1))
        playerPassData['EPV'] = MinMaxScaler.fit_transform(playerPassData['EPV'].values.reshape(-1,1))
        
    
    if openPlay == True:
        playerPassData['DeadBall'] = [DeadBallExtractor(x) for x in playerPassData['qualifiers']]
        playerPassData = playerPassData[playerPassData['DeadBall']!=True]
        playerPassData.reset_index(inplace=True,drop=True)
    
    
#     # Calculating Initial and Final Distance from Goal
    
    
#     playerPassData['initDistanceFromGoal'] = np.sqrt(np.square(100-playerPassData['x']) + np.square(50-playerPassData['y']))
#     playerPassData['finDistanceFromGoal'] = np.sqrt(np.square(100-playerPassData['endX']) + np.square(50-playerPassData['endY']))
    
    # Creating a Successful Passes DataFrame
    playerSuccPasses = playerPassData[playerPassData['outcomeType']=='Successful']
    playerSuccPasses.reset_index(drop=True,inplace=True)
    
    # Creating a Progressive Pass Column
    playerPassData['Progressive'] = playerPassData.apply(lambda row: isProgressivePass(row['x'],row['y'],row['endX'],row['endY']),axis=1)
    
    # Creating a Successful Forward Progressive Pass DataFrame
    playerProgPasses = playerPassData[playerPassData['Progressive']]
    playerSuccProgPasses = playerProgPasses[playerProgPasses['outcomeType']=='Successful']
    playerSuccProgPasses = playerSuccProgPasses[playerSuccProgPasses['x']<playerSuccProgPasses['endX']]
    playerSuccProgPasses = playerSuccProgPasses[playerSuccProgPasses['endX']>=66.67]
    playerSuccProgPasses.reset_index(inplace=True,drop=True)
    
    # Creating a Key Pass Column
    playerPassData['keyPass'] = [keyPassExtractor(x) for x in playerPassData['satisfiedEventsTypes']]
    # Creating a Key Pass DataFrame
    playerKeyPasses = playerPassData[playerPassData['keyPass']==True]
    playerKeyPasses.reset_index(drop=True,inplace=True)
    
    # Creating an Assist DataFrame
    playerAssists = playerPassData[playerPassData['assist']==True]
    playerAssists.reset_index(drop=True,inplace=True)
    
    
    if orientation=='Vertical':
        # Drawing the pitch 
        pitch = mplsoccer.VerticalPitch(pitch_type=pitchType,pitch_color=pitchColor,line_color=lineColor,half=True,pad_bottom=7,figsize=(15,15), goal_type='box')
        pitch.draw(ax=ax)
        # Overlapping with a patch to plot pass legend
        ax.add_patch(Polygon([[0,0],[100,0],
                             [100,49.75],[0,49.75]],lw=5,closed=True,color=pitchColor,zorder=7))
        
        ax2 = fig.add_axes([0.7,0.805,0.175,0.07])
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_facecolor(faceColor)
        ax2.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.set_xlim(0,100)
        ax2.set_ylim(0,100)
        
        fig.set_facecolor(faceColor)
        
        # Plot end locations of all passes
        if allPasses == True:
            pass_lines = pitch.lines(playerSuccPasses['x'],playerSuccPasses['y'],
                                       playerSuccPasses['endX'],playerSuccPasses['endY'],comet=True,
                                       color=apColor,lw=3,alpha_end=0.2,alpha_start=0.05,transparent=True,
                                       zorder = 1, 
                                       ax=ax)
            if EPV == True:
                ap_nodes = pitch.scatter(playerSuccPasses['endX'],playerSuccPasses['endY'],
                                         alpha=0.6,s=playerSuccPasses['EPV']*maxNodeSize,
                                         zorder=1,ax=ax,linewidth=2,color=pitchColor,edgecolor=apColor)
            else:
                ap_nodes = pitch.scatter(playerSuccPasses['endX'],playerSuccPasses['endY'],
                                         alpha=0.6,s=minNodeSize,
                                         zorder=1,ax=ax,linewidth=2,color=pitchColor,edgecolor=apColor)
        # Plotting Progressive Passes    
        prog_lines = pitch.lines(playerSuccProgPasses['x'],playerSuccProgPasses['y'],
                                 playerSuccProgPasses['endX'],playerSuccProgPasses['endY'],comet=True,
                                 color=ppColor,lw=4,alpha_end=0.7,alpha_start=0.1,transparent=True,
                                 zorder = 2, 
                                 ax=ax)
        if EPV == True:
            prog_nodes = pitch.scatter(playerSuccProgPasses['endX'],playerSuccProgPasses['endY'],s=playerSuccProgPasses['EPV']*maxNodeSize,
                                       alpha=1,color=pitchColor,zorder=3,ax=ax,linewidth=2,label='Progressive Pass',
                                       edgecolor=ppColor)
        else:
            prog_nodes = pitch.scatter(playerSuccProgPasses['endX'],playerSuccProgPasses['endY'],s=maxNodeSize,
                                       alpha=1,color=pitchColor,zorder=3,ax=ax,linewidth=2,label='Progressive Pass',
                                       edgecolor=ppColor)
        # Plotting Key Passes    
        kp_lines = pitch.lines(playerKeyPasses['x'],playerKeyPasses['y'],
                               playerKeyPasses['endX'],playerKeyPasses['endY'],comet=True,
                               color=kpColor,lw=4,alpha_end=0.7,alpha_start=0.1,transparent=True,
                               zorder = 3, 
                               ax=ax)
        if EPV == True:
            kp_nodes = pitch.scatter(playerKeyPasses['endX'],playerKeyPasses['endY'],
                                     alpha=1,s=playerKeyPasses['EPV']*maxNodeSize,color=pitchColor,zorder=3,ax=ax,linewidth=2,
                                     edgecolor=kpColor,label='Key Pass')
        else:
            kp_nodes = pitch.scatter(playerKeyPasses['endX'],playerKeyPasses['endY'],
                                     alpha=1,s=maxNodeSize,color=pitchColor,zorder=3,ax=ax,linewidth=2,
                                     edgecolor=kpColor,label='Key Pass')
        # Plotting assists
        if assistsOn:
            if EPV == True:
                assist_nodes = pitch.scatter(playerAssists['endX'],playerAssists['endY'],
                                             s=playerAssists['EPV']*(maxNodeSize+1000),marker='football',zorder=3,ax=ax,alpha=1)
            else:
                assist_nodes = pitch.scatter(playerAssists['endX'],playerAssists['endY'],
                                             s=maxNodeSize,marker='football',zorder=3,ax=ax,alpha=0.8)

        pitch.lines(47.5,70,47.5,30,comet=True,ax=ax,color='white',lw=5,alpha_end=0.7,alpha_start=0.1,transparent=True,zorder=8)
        pitch.scatter(47.5,30,edgecolor='white',color=pitchColor,ax=ax,linewidth=2,s=300,zorder=8)
        pitch.annotate('Start\nLocation',(46.5,75.5),xytext=(46.5,75.5),ax=ax,color='white',ha='center',fontsize=15,zorder=8)
        pitch.annotate('End\nLocation',(46.5,22.5),xytext=(46.5,22.5),ax=ax,color='white',ha='center',fontsize=15,zorder=8)
        
        # Writing credits
        ax.text(0,51,'@barcalytix', ha='right',va='baseline',fontsize=18, color='gray', alpha=0.5, weight='bold')
        
        if EPV:
            ax2.scatter(4,41,edgecolors='white',s=80, c='#2b2b2b',lw=2)
            ax2.scatter(13,41,edgecolors='white',s=200, c='#2b2b2b',lw=2)
            ax2.scatter(25,41,edgecolors='white',s=400, c='#2b2b2b',lw=2)
            ax2.text(32,34,'Possession Value',color='white',fontsize=15)
            
        if assistsOn:
            ax2.scatter(25,80,s=400,c='w',edgecolor='black',marker=football_hexagon_marker)
            ax2.text(32,70,'Assist',color='white',fontsize=15)
            
    
        
    if orientation=='Horizontal':
         # Drawing the pitch 
        pitch = mplsoccer.Pitch(pitch_type=pitchType,pitch_color=pitchColor,line_color=lineColor,line_zorder=1, figsize=(20,10), goal_type='box')
        pitch.draw(ax=ax)
        
        # Overlapping with a patch to plot pass legend
        ax.add_patch(Polygon([[0,-1.5],[100,-1.5],
                     [100,-100],[0,-100]],lw=5,closed=True,color=faceColor))
        
        ax2 = fig.add_axes([0.65,0.86,0.15,0.07])
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)
        ax2.set_facecolor(faceColor)
        ax2.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        
        ax2.set_xlim(0,100)
        ax2.set_ylim(0,100)
        
        fig.set_facecolor(faceColor)
        
        if allPasses == True:
            pass_lines = pitch.lines(playerSuccPasses['x'],playerSuccPasses['y'],
                                       playerSuccPasses['endX'],playerSuccPasses['endY'],comet=True,
                                       color=apColor,lw=3,alpha_end=0.2,alpha_start=0.05,transparent=True,
                                       zorder = 1, 
                                       ax=ax)
            if EPV == True:
                ap_nodes = pitch.scatter(playerSuccPasses['endX'],playerSuccPasses['endY'],
                                      alpha=0.6,s=playerSuccPasses['EPV']*maxNodeSize,zorder=1,ax=ax,linewidth=2,color=pitchColor,edgecolor=apColor)
            else:
                ap_nodes = pitch.scatter(playerSuccPasses['endX'],playerSuccPasses['endY'],
                                      alpha=0.6,s=minNodeSize,zorder=1,ax=ax,linewidth=2,color=pitchColor,edgecolor=apColor)
            
        prog_lines = pitch.lines(playerSuccProgPasses['x'],playerSuccProgPasses['y'],
                                 playerSuccProgPasses['endX'],playerSuccProgPasses['endY'],comet=True,
                                 color=ppColor,lw=4,alpha_end=0.7,alpha_start=0.1,transparent=True,
                                 zorder = 2, 
                                 ax=ax)
        if EPV == True:
            pp_nodes = pitch.scatter(playerSuccProgPasses['endX'],playerSuccProgPasses['endY'],s=playerSuccProgPasses['EPV']*maxNodeSize,
                                       alpha=1,color=pitchColor,zorder=3,ax=ax,linewidth=2,label='PV',
                                       edgecolor=ppColor)
        else:
            pp_nodes = pitch.scatter(playerSuccProgPasses['endX'],playerSuccProgPasses['endY'],s=maxNodeSize,
                                       alpha=1,color=pitchColor,zorder=3,ax=ax,linewidth=2,label='PV',
                                       edgecolor=ppColor)
            
        kp_lines = pitch.lines(playerKeyPasses['x'],playerKeyPasses['y'],
                               playerKeyPasses['endX'],playerKeyPasses['endY'],comet=True,
                               color=kpColor,lw=4,alpha_end=0.7,alpha_start=0.1,transparent=True,
                               zorder = 3, 
                               ax=ax)
        if EPV == True:
            kp_nodes = pitch.scatter(playerKeyPasses['endX'],playerKeyPasses['endY'],
                                     alpha=1,s=playerKeyPasses['EPV']*maxNodeSize,color=pitchColor,zorder=3,ax=ax,linewidth=2,
                                     edgecolor=kpColor,label='PV')
        else:
            kp_nodes = pitch.scatter(playerKeyPasses['endX'],playerKeyPasses['endY'],
                                     alpha=1,s=maxNodeSize,color=pitchColor,zorder=3,ax=ax,linewidth=2,
                                     edgecolor=kpColor,label='PV')
            
         # Plotting assists
        if assistsOn:
            if EPV == True:
                assist_nodes = pitch.scatter(playerAssists['endX'],playerAssists['endY'],
                                                 s=playerAssists['EPV']*maxNodeSize,marker='football',zorder=3,ax=ax,alpha=0.8)
            else:
                assist_nodes = pitch.scatter(playerAssists['endX'],playerAssists['endY'],
                                                 s=maxNodeSize,marker='football',zorder=3,ax=ax,alpha=0.8)
            
        
        pitch.lines(30,-2.5,70,-2.5,comet=True,ax=ax,color='white',lw=6,alpha_end=0.7,alpha_start=0.1,transparent=True,zorder=5)
        pitch.scatter(70,-2.5,edgecolor='white',color=faceColor,ax=ax,linewidth=2,s=200,zorder=5)
        pitch.annotate('Start Location',(21,-3),xytext=(21,-3),ax=ax,color='white',ha='left',fontsize=13)
        pitch.annotate('End Location',(82,-3),xytext=(82,-3),ax=ax,color='white',ha='right',fontsize=13)
                
        # Writing credits
        ax.text(100,0.5,'@barcalytix', ha='right',va='baseline',fontsize=18, color='gray', alpha=0.5, weight='bold')
        
        if EPV:
            ax2.scatter(8,25,edgecolors='white',s=80, c=faceColor,lw=2)
            ax2.scatter(16,25,edgecolors='white',s=200, c=faceColor,lw=2)
            ax2.scatter(26,25,edgecolors='white',s=400, c=faceColor,lw=2)
            ax2.text(33,15,'Possession Value',color='white',fontsize=14)
            
        if assistsOn:
            
            ax2.scatter(26,80,s=400,c='w',edgecolor='black',marker=football_hexagon_marker)
            ax2.text(33,70,'Assist',color='white',fontsize=14)
            

        
        
        