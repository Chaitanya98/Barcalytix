# Importing packages
import pandas as pd
import requests
import json

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

    # Extracting team names and adding them as columns to the DataFrame
    homeTeam = data['general']['homeTeam']
    awayTeam = data['general']['awayTeam']
    teamNames = pd.DataFrame([homeTeam]+[awayTeam])
    shotsData.join(teamNames.set_index("id"), on="teamId")
    shotsData["homeTeam"] = homeTeam["name"]
    shotsData["awayTeam"] = awayTeam["name"]
    
    return shotsData