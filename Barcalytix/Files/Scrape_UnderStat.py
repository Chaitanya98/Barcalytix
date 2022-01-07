import pandas as pd
import json
from bs4 import BeautifulSoup
import requests

def scrapeShotData(matchID):
    base_url = 'https://understat.com/match/'
    matchId = str(matchID)
    url = base_url + matchId
    
    req = requests.get(url)
    soup = BeautifulSoup(req.content,'lxml')
    scripts = soup.find_all('script')
    
    json_raw_string = scripts[1].string
    
    start_ind = json_raw_string.index("\\")
    stop_ind = json_raw_string.index("')")
    
    json_data = json_raw_string[start_ind:stop_ind]
    
    json_data = json_data.encode('utf8').decode('unicode_escape')
    
    match_data = json.loads(json_data)
    
    home_data = pd.json_normalize(match_data['h'])
    away_data = pd.json_normalize(match_data['a'])
    
    shotData = pd.concat([home_data,away_data])
    shotData.reset_index(inplace=True,drop=True)
    
    return shotData
    