# -----------------------------------------------------
# Importing packages
# -----------------------------------------------------

import mplsoccer
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from FOTMOB_API import getFOTMOBShots
from highlight_text import fig_text, ax_text
from mplsoccer.scatterutils import scatter_football
import warnings
warnings.filterwarnings("ignore")


# -----------------------------------------------------
# Creating Helper functions to plot the Shot Map
# -----------------------------------------------------

def add_shot_legend_OT(ax, shotColor):
    """
    Add a shot legend to a Matplotlib axis object for on target shots.

    Parameters:
    ===========
        ax (matplotlib.axes.Axes): Matplotlib axis object to plot on.
        shotColor (str): Color of the shot marker.

    Returns:
    ========
        None
    """
    # Add a scatter plot marker and text for a shot with the given color
    ax.scatter(7.5,-1.05,c=shotColor,edgecolor='w',s=600,lw=3)
    ax.text(8.5,-1.4,'Shot',fontsize=28,c='w')
    
    # Add a football marker for a goal and text
    scatter_football(x=13,y=-1.05,s=800,ax=ax,c='white',edgecolors='black',zorder=5)
    ax.text(14,-1.4,'Goal',fontsize=28,c='w')
    
    # Add three scatter plot markers with no color with progressing sizes which repesent xG on Target
    ax.scatter(9.5-0.75,-3.25,s=280,c='None',edgecolor='w',lw=3)
    ax.scatter(10.75-0.75,-3.25,s=1000,c='None',edgecolor='w',lw=3)
    ax.scatter(12.5-0.75,-3.25,s=1700,c='None',edgecolor='w',lw=3)
    ax.text(13.5-0.75,-3.5,'xGOT',c='w',fontsize=28)
    
def plot_shots_on_target(ax, shotDataOT, color, width=24, height=8, shot_size=3000, goal_size=3500):
    """
    Plots shots on target for a given team on a mplsoccer pitch object.

    Parameters:
    ===========
        ax (matplotlib.axes.Axes): Matplotlib axis object to plot on.
        shotDataOT (pandas.Dataframe): The dataframe containing shots on target for a team
        color (str): The color of the team's shots
        width (float, optional): The width of the pitch. Defaults to 24.
        height (float, optional): The height of the pitch. Defaults to 8.
        shot_size (int, optional): The size of the marker for each shot. Defaults to 3000.
        goal_size (int, optional): The size of the marker for each goal. Defaults to 3500.
    
    Returns:
    ========
        None    
    """

    # Set axis properties
    ax.set_facecolor('red')
    ax.axis('equal')
    ax.axis('off')

    # Plot the goal post
    ax.plot([0,0],[0,height], color = 'w', lw = 8,zorder=3)
    ax.plot([0,width],[height,height], color = 'w', lw = 8,zorder=3)
    ax.plot([width,width],[0,height], color = 'w', lw = 8,zorder=3)

    # Plot the net in the goal post
    netWidth = 12
    for widthVal in np.linspace(0,width,netWidth+1):
        ax.plot([widthVal,widthVal],[0,height], color = '#bdbdbd', ls='-',alpha=0.5)

    netHeight = 6
    for heightVal in np.linspace(0,height,netHeight+1):
        ax.plot([0,width],[heightVal,heightVal], color = '#bdbdbd', ls = '-',alpha=0.5)

    # Plot the ground/grass
    ax.plot([-2,width + 2],[0,0], color = 'green', marker = 'None', lw = 8, zorder = 3)

    # Create new columns in the 'shotDataOT' dataframe for the scaled x and y coordinates of each shot location
    shotDataOT['onGoalXScaled'] = shotDataOT['onGoalX'] * width
    shotDataOT['onGoalYScaled'] = shotDataOT['onGoalY'] * height

    # Plot shots on target
    ax.scatter(shotDataOT['onGoalXScaled'], shotDataOT['onGoalYScaled'],
               s=shotDataOT['expectedGoalsOnTarget']*shot_size, color=color, edgecolor='w',
               lw=3, alpha=.75, zorder=5, ls='-')

    # Plot goals
    scatter_football(x=shotDataOT[shotDataOT['eventType']=='Goal']['onGoalXScaled'],
                     y=shotDataOT[shotDataOT['eventType']=='Goal']['onGoalYScaled'],
                     s=shotDataOT[shotDataOT['eventType']=='Goal']['expectedGoalsOnTarget']*goal_size,
                     ax=ax, c='white', edgecolors='black', zorder=5)


def plot_shot_map(FOTMOB_URL, home_color='#cf0622',away_color='#056ec4',savePath=None):
    """
    Plots a shot map for a given match URL from FOTMOB.

    Parameters:
    ===========
        FOTMOB_URL (str): The URL for the match on FOTMOB.
        home_color (str, optional): The color of the home team's shots. Defaults to '#cf0622'.
        away_color (str, optional): The color of the away team's shots. Defaults to '#056ec4'.
        savePath (str, optional): The path to save the generated plot. Defaults to None.

    Returns:
    ========
        None    
    """
    
    # -----------------------------------------------------
    # Feature Engineering & Preprocessing
    # -----------------------------------------------------
    
    # Define FontManager objects for the custom fonts
    robotoMed = mplsoccer.FontManager(('https://github.com/Chaitanya98/Barcalytix/blob/main/Fonts/Roboto-Medium.ttf?raw=True'))
    robotoBold = mplsoccer.FontManager(('https://github.com/Chaitanya98/Barcalytix/blob/main/Fonts/Roboto-Bold.ttf?raw=True'))

    # Add the custom fonts to MatPlotLib FontManagaer
    mpl.font_manager.fontManager.addfont(robotoMed.prop.get_file())
    mpl.font_manager.fontManager.addfont(robotoBold.prop.get_file())
    
    # Disable the minus sign unicode in the plot axes
    plt.rcParams['axes.unicode_minus'] = False
    
    # Set the default font family to 'Roboto'
    mpl.rc('font', family='Roboto')

    
    # Get the Shots Data using the FOTMOB_API file
    shotData, FOTMOB_JSON = getFOTMOBShots(FOTMOB_URL, returnJSON=True)

    # Split the data into home and away teams
    home_df = shotData[shotData['h_a'] == 'h'].reset_index(drop=True)
    away_df = shotData[shotData['h_a'] == 'a'].reset_index(drop=True)

    # Separate the goal events for each team
    home_goals = home_df[(home_df['eventType'] == 'Goal')&(home_df['isOwnGoal']==False)].reset_index(drop=True)
    away_goals = away_df[(away_df['eventType'] == 'Goal')&(away_df['isOwnGoal']==False)].reset_index(drop=True)

    # Define a dictionary of colors for each type of shot event
    colors = {'AttemptSaved': 'red', 'Blocked': 'yellow', 'Miss': '#16aed9', 'Post': 'white', 'Goal': 'black'}

    # Map the appropriate color for each event type and add a new column to the home and away dataframes
    home_df['shotColors'] = home_df['eventType'].map(colors)
    away_df['shotColors'] = away_df['eventType'].map(colors)

    # Create a new dataframe containing only the shots with xG on target
    shotDataOT = shotData[shotData['expectedGoalsOnTarget'].notna()]
                                
    # Split the 'shotDataOT' dataframe into two new dataframes, one for home team shots and one for away team shots
    shotDataOT_h = shotDataOT[shotDataOT['h_a'] == 'h']
    shotDataOT_a = shotDataOT[shotDataOT['h_a'] == 'a']

    # -----------------------------------------------------
    # Creating the Figure & Sub-plots
    # -----------------------------------------------------
    
    # Create a figure object and specify its size and layout
    fig = plt.figure(figsize=(30,30),constrained_layout=False)
    # Define a grid for the subplots, with two rows and two columns, and no horizontal or vertical spacing
    gs = fig.add_gridspec(nrows=2, ncols=2, hspace=0, wspace=0.0, height_ratios=[2,1])

    # Add the first subplot to the figure, spanning the top row and both columns
    ax1 = fig.add_subplot(gs[:-1, :])
    # Add the second subplot to the figure, occupying the bottom left cell of the grid
    ax2 = fig.add_subplot(gs[-1, :-1])
    # Add the third subplot to the figure, occupying the bottom right cell of the grid
    ax3 = fig.add_subplot(gs[-1, -1])

    # Set the facecolor of the entire figure to a dark grey
    fig.set_facecolor('#2b2b2b')
    # Set the facecolor of the first subplot to the same dark grey
    ax1.patch.set_facecolor('#2b2b2b')
    # Create a soccer pitch object using the mplsoccer library, with a UEFA-style pitch, white lines, and a box-style goal
    pitch = mplsoccer.Pitch(pitch_type='uefa', pitch_color='#2b2b2b', line_color='white', goal_type='box', line_zorder=2, linewidth=6)
    # Draw the soccer pitch on the first subplot
    pitch.draw(ax=ax1)
    # Invert the y-axis on the first subplot, so that the positive y-direction points upwards
    ax1.invert_yaxis()

    # -----------------------------------------------------
    # Plotting Shots on Target with xGOT
    # -----------------------------------------------------
    
    # Plot shots on target for home team
    plot_shots_on_target(ax2, shotDataOT_h, home_color)
    
    # Plot shots on target for away team
    plot_shots_on_target(ax3, shotDataOT_a, away_color)
    
    # Get colors for shots for home and away teams
    home_shot_colors = home_df['shotColors'].values
    away_shot_colors = away_df['shotColors'].values

    # -----------------------------------------------------
    # Plotting Shots and Goals with xG
    # -----------------------------------------------------
    
    # Home team shots and goals
    pitch.scatter(x=105-home_df['x'], y=home_df['y'], s=home_df['expectedGoals']*10000, c=home_shot_colors, ec='#2b2b2b', alpha=0.85, ax=ax1, zorder=3)
    pitch.scatter(x=105-home_goals['x'], y=home_goals['y'], s=home_goals['expectedGoals']*10000, marker='football', zorder=3, ax=ax1)

    # Away team own goals
    pitch.scatter(away_df[away_df['isOwnGoal']==True]['x'], 68-away_df[away_df['isOwnGoal']==True]['y'], s=3000, marker='football', zorder=3, c='red', ax=ax1)

    # Away team shots and goals
    pitch.scatter(x=away_df['x'], y=68-away_df['y'], s=away_df['expectedGoals']*10000, c=away_shot_colors, ec='#2b2b2b', alpha=0.85, ax=ax1, zorder=3)
    pitch.scatter(x=away_goals['x'], y=68-away_goals['y'], s=away_goals['expectedGoals']*10000, marker='football', zorder=3, ax=ax1)

    # Home team own goals
    pitch.scatter(105-home_df[home_df['isOwnGoal']==True]['x'], home_df[home_df['isOwnGoal']==True]['y'], s=3000, marker='football', zorder=3, c='red', ax=ax1)

    # -----------------------------------------------------
    # Plotting an Arcs for Mean Shot Distances
    # -----------------------------------------------------
    
    # Keyword arguments for Wedge patches
    wedge_kwargs = {'facecolor':'None', 'zorder':1, 'linestyle':'--', 'edgecolor':'cyan', 'linewidth':3, 'alpha':.75}

    # Compute the average shot distance from goal for the home team
    avgShotDistHome = home_df['distanceFromGoal'].mean()

    # Create a wedge patch for the home team's average shot distance and add it to the pitch subplot
    wedge1 = mpl.patches.Wedge((0, 34), r=avgShotDistHome, theta1=-90, theta2=90, **wedge_kwargs)
    ax1.add_patch(wedge1)

    # Compute the average shot distance from goal for the away team
    avgShotDistAway = away_df['distanceFromGoal'].mean()

    # Create a wedge patch for the away team's average shot distance and add it to the pitch subplot
    wedge2 = mpl.patches.Wedge((105, 34), r=avgShotDistAway, theta1=90, theta2=-90, **wedge_kwargs)
    ax1.add_patch(wedge2)

    # -----------------------------------------------------
    # Plotting Legends
    # -----------------------------------------------------
    
    # Add legend for shots on target for home team
    add_shot_legend_OT(ax2, home_color)
    
    # Add legend for shots on target for away team
    add_shot_legend_OT(ax3, away_color)

    # Create a new axis for shot markers legend
    ax4 = fig.add_axes([0.42, 0.85, 0.455, 0.06])
    # Hide axis ticks and set facecolor to None
    ax4.get_xaxis().set_visible(False)
    ax4.get_yaxis().set_visible(False)
    ax4.set_facecolor('None')
    # Remove spines
    for spine in 'right,top,bottom,left'.split(','):
        ax4.spines[spine].set_visible(False)
    # Set x and y limits
    ax4.set_xlim(0, 100)
    ax4.set_ylim(0, 100)

    # Shift the x position of the shot marker legend if there is an own goal
    x_offset = -16 if shotData['isOwnGoal'].sum() else 0
    # Define scatter plot parameters for markers in legend
    scatter_kwargs = {'edgecolors': 'white','lw': 3}

    # Add four scatter plot markers with no color with progressing sizes which repesent xG
    ax4.scatter(77 + x_offset, 72, s=200, c='#2b2b2b', **scatter_kwargs)
    ax4.scatter(80 + x_offset, 72, s=500, c='#2b2b2b', **scatter_kwargs)
    ax4.scatter(84 + x_offset, 72, s=1000, c='#2b2b2b', **scatter_kwargs)
    ax4.scatter(88.5 + x_offset, 72, s=1500, c='#2b2b2b', **scatter_kwargs)
    # Add text label for xG to the legend
    ax4.text(92 + x_offset, 65, 'xG', color='white', fontsize=28)

    # Add mean shot distance line and text label to the legend
    ax4.plot([39 + x_offset, 46 + x_offset], [72, 72], '--', color='cyan', lw=4)
    ax4.text(47 + x_offset, 65, 'Mean Shot Distance', color='white', fontsize=28)

    # Add marker and text for own goal (if applicable)
    if shotData['isOwnGoal'].sum():
        scatter_football(89 - 6, 72, s=750, ax=ax4, c='red', edgecolors='black')
        ax4.text(91 - 6, 65, 'Own Goal', color='white', fontsize=26)
        fig.text(0.87, 0.38, 'Note: xG for own goals is unavailable', color='white', fontsize=26, ha='right')

    # Add scatter plot markers and text labels for other shot outcomes
    ax4.scatter(13, 30, s=500, c='red', lw=2, alpha=0.85)
    ax4.text(15, 23, 'Saved Shot', color='white', fontsize=26)

    ax4.scatter(31, 30, s=500, c='#16aed9', lw=2, alpha=0.85)
    ax4.text(33, 23, 'Missed Shot', color='white', fontsize=26)

    ax4.scatter(50, 30, s=500, c='yellow', lw=2, alpha=0.85)
    ax4.text(52, 23, 'Blocked Shot', color='white', fontsize=26)

    ax4.scatter(70, 30, c='white', s=500, lw=2, alpha=0.85)
    ax4.text(72, 23, 'Off the Post', color='white', fontsize=26)

    scatter_football(89, 30, s=750, ax=ax4, c='white', edgecolors='black')
    ax4.text(91, 23, 'Goal', color='white', fontsize=26)

    # -----------------------------------------------------
    # Annotating the Metrics
    # -----------------------------------------------------

    # Define the bounding box dictionaries for the text
    bboxDict = dict(facecolor='w', alpha=1, boxstyle=('round,rounding_size=0.5'), linewidth=3, edgecolor='#2b2b2b')
    bboxDict_home = dict(facecolor=home_color, alpha=1, boxstyle=('round,rounding_size=0.5'), linewidth=3, edgecolor='#2b2b2b')
    bboxDict_away = dict(facecolor=away_color, alpha=1, boxstyle=('round,rounding_size=0.5'), linewidth=3, edgecolor='#2b2b2b')

    # List of strings containing the metrics to display and their coordinates
    metrics_info = ['Shots', 'xG/Shot', 'Shots on Target', 'xGOT', 'Mean Shot Distance\nfrom Goal (m)']
    metrics_y = np.linspace(0.75, 0.5, 5)

    # Text formatting options
    text_kwargs = {'fontsize': 28, 'ha': 'center', 'ma': 'center', 'va': 'center'}

    # Loop through the metrics and add the text to the plot using fig.text()
    for i, metric in enumerate(metrics_info):
        fig.text(0.512, metrics_y[i] + 0.005, s=metric, color='k', bbox=bboxDict, **text_kwargs)

    # List of strings containing the home team's metrics to display and their coordinates
    home_metrics = [
        "len(home_df)",
        "round(home_df['expectedGoals'].sum()/len(home_df), 2)",
        "len(home_df[home_df['isOnTarget']==True])",
        "round(home_df['expectedGoalsOnTarget'].sum(),2)",
        "round(avgShotDistHome,2)"
    ]

    # Loop through the home team's metrics and add the text to the plot using fig.text()
    for i, home_metric in enumerate(home_metrics):
        fig.text(0.4, metrics_y[i] + 0.005, s=str(eval(home_metric)), color='w', bbox=bboxDict_home, **text_kwargs)

    # List of strings containing the away team's metrics to display and their coordinates
    away_metrics = [
        "len(away_df)",
        "round(away_df['expectedGoals'].sum()/len(away_df), 2)",
        "len(away_df[away_df['isOnTarget']==True])",
        "round(away_df['expectedGoalsOnTarget'].sum(),2)",
        "round(avgShotDistAway,2)"
    ]

    # Loop through the away team's metrics and add the text to the plot using fig.text()
    for i, away_metric in enumerate(away_metrics):
        fig.text(0.624, metrics_y[i] + 0.005, s=str(eval(away_metric)), color='w', bbox=bboxDict_away, **text_kwargs)

    # -----------------------------------------------------
    # Plotting the Titles
    # -----------------------------------------------------
    
    # Get the competition name from the FOTMOB JSON data
    competitionName = FOTMOB_JSON['general']['leagueName']

    # Add a title with match and competition information using fig_text function
    fig_text(s= '<'+str(home_df['teamName'][0])+' : '+str(len(home_goals))+'>\n'+
                '<'+str(away_df['teamName'][0])+' : '+str(len(away_goals))+'>\n'+
                '<'+competitionName +' | '+pd.to_datetime(FOTMOB_JSON['general']['matchTimeUTCDate']).strftime('%d-%m-%Y')+'>',
            x=.155, y=0.89,
            ha='left',va='center',
            fontsize = 30,
            color = 'white',            
            highlight_textprops = [{'fontsize':54,'color':home_color,'fontweight':'bold'},
                                   {'fontsize':54,'color':away_color,'fontweight':'bold'},
                                   {'fontsize':35,'color':'#9399a3'}])

    # Add the Total xG value for the home team on the home side using fig_text function
    fig_text(s=  '<'+str(home_df['teamName'][0])+' : '+str(round((home_df['expectedGoals'].sum()),2))+' xG>',
            x=.35, y=0.8,
            ha='center',va='center',textalign='center',
            fontsize = 25, fontweight='bold',
            color = 'white',            
            highlight_textprops = [{'fontsize':48,'color':home_color}])

    # Add the Total xG value for the away team on the away side using fig_text function
    fig_text(s=  '<'+str(away_df['teamName'][0])+' : '+str(round((away_df['expectedGoals'].sum()),2))+' xG>',
            x=.675, y=0.8,
            ha='center',va='center',textalign='center',
            fontsize = 25, fontweight='bold',
            color = 'white',            
            highlight_textprops = [{'fontsize':48,'color':away_color}])

    # Add the Total xGOT value for the home team using ax_text function
    ax_text(s=  '<'+str(home_df['teamName'][0])+' : '+str(round(home_df['expectedGoalsOnTarget'].sum(),2))+' xGOT>',
            x=12, y=10.5,
            ha='center',va='center',textalign='center',
            fontsize = 25, fontweight='bold',
            color = 'white',            
            highlight_textprops = [{'fontsize':48,'color':home_color}],ax=ax2)

    # Add the Total xGOT value for the away team using ax_text function
    ax_text(s=  '<'+str(away_df['teamName'][0])+' : '+str(round(away_df['expectedGoalsOnTarget'].sum(),2))+' xGOT>',
            x=12, y=10.5,
            ha='center',va='center',textalign='center',
            fontsize = 25, fontweight='bold',
            color = 'white',            
            highlight_textprops = [{'fontsize':48,'color':away_color}],ax=ax3)

    # Add title and credits to the figure
    fig.text(x=.5,y=.925,s='Shot Map',color='#ffffff',fontsize=60,ha='center')
    fig.text(x=.5,y=.135,s='Created By: @Barcalytix',color='#a5a6a8',fontsize=35,ha='center')

    # -----------------------------------------------------
    # Saving the figure
    # -----------------------------------------------------

    # Save the figure if a path is provided
    if savePath is not None:
        fig.savefig(savePath+'\ShotMap.png',bbox_inches='tight')
