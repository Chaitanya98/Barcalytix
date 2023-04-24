# Importing packages
import json
import requests
import numpy as np
import pandas as pd


# Creeating a function extracts shots data from a fotmob url for a specific match and returns a pandas dataframe of the shots information
def getFOTMOBShots(url):
    """
    A function that takes in a FOTMOB match URL, extracts the match ID and uses the FOTMOB API
    to fetch shot data for that match. The function then converts the shot data into a pandas DataFrame
    and adds the names of the two teams playing the match.
    
    Args:
    url (str): A FOTMOB match URL
    
    Returns:
    pandas.DataFrame: A DataFrame containing shot data for the match
    
    """
    
    url = "https://www.fotmob.com/match/3918232/matchfacts/barcelona-vs-atletico-madrid"
    
    # Extracting match ID from match URL
    matchLink = url
    matchId = matchLink.split("/")[4]

    # Creating API link to fetch shot data for the match
    apiLink = "https://www.fotmob.com/api/matchDetails?matchId=" + matchId

    # Making request to API and loading JSON response
    response = requests.get(apiLink)
    data = json.loads(response.content)

    # Creating a pandas DataFrame from shot data    
    shotsData = pd.DataFrame(data["content"]["shotmap"]["shots"])

    # Extract the home team and away team data from the main data dictionary
    homeTeam = data['general']['homeTeam']
    awayTeam = data['general']['awayTeam']

    # Create a DataFrame to store the team names and join it with the shots data
    teamNames = pd.DataFrame([homeTeam] + [awayTeam])
    shotsData.join(teamNames.set_index("id"), on="teamId")

    # Create new columns for the home team and away team names
    shotsData["homeTeam"] = homeTeam["name"]
    shotsData["awayTeam"] = awayTeam["name"]

    # Create a new column to indicate whether the shot was taken by the home or away team
    shotsData['h_a'] = np.where(shotsData["teamId"] == homeTeam["id"], 'h', 'a')

    # Update the 'eventType' column to 'Blocked' for blocked shots
    shotsData.loc[shotsData['isBlocked'], 'eventType'] = 'Blocked'

    # Calculate the distance from goal
    shotsData['distanceFromGoal'] = np.sqrt((105 - shotsData['x']) ** 2 + (34 - shotsData['y']) ** 2)
    
    # Extract the 'x' and 'y' values from the 'onGoalShot' column
    shotsData['onGoalX'] = shotsData['onGoalShot'].str['x']
    shotsData['onGoalY'] = shotsData['onGoalShot'].str['y']
    
    return shotsData