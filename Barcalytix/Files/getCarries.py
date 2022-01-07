import pandas as pd
import numpy as np



def checkCarryLength(endX,endY,nextX,nextY):
    distance = np.sqrt(np.square(nextX - endX) + np.square(nextY - endY))
    if(distance < 1.5):
        return True
    else:
        return False



def getCarries(df,teamId):
    df['recipient'] = df['playerId'].shift(-1)
    df['nextTeamId'] = df['teamId'].shift(-1)


    carries_btw_passes = np.array(df[(df['type']=="Pass") & (df['outcomeType'] == "Successful") & (df['teamId']==int(teamId))].index.tolist())
    carries_after_recov = np.array(df[((df['type']=="BallRecovery") | (df['type']=="Interception") | (df['type']=="Tackle") | (df['type']=="BlockedPass")) & (df['outcomeType'] == "Successful") & (df['teamId']==int(teamId))].index.tolist())

    carries_df = pd.DataFrame()

    for index in carries_btw_passes:
        carry = pd.Series()
        carry['matchId'] = df.iloc[index].matchId
        carry['minute'] = df.iloc[index].minute
        carry['playerId'] = df.iloc[index].recipient
        carry['x'] = df.iloc[index].endX
        carry['y'] = df.iloc[index].endY 
        if(df.iloc[index+1].type == "OffsideGiven" or df.iloc[index+1].type == "End" or df.iloc[index+1].type == "SubstitutionOff" or df.iloc[index+1].type == "SubstitutionOn"):
            continue
        elif(df.iloc[index+1].type == "Challenge" and df.iloc[index+1].outcomeType == "Unsuccessful" and df.iloc[index+1].teamId != teamId):
            carry['playerId'] = df.iloc[index+2].playerId
            index += 1
            while((df.iloc[index+1].type == "TakeOn" and df.iloc[index+1].outcomeType == "Successful") or 
                  (df.iloc[index+1].type == "Challenge" and df.iloc[index+1].outcomeType == "Unsuccessful")):
                index += 1
            if(df.iloc[index+1].type == "OffsideGiven" or df.iloc[index+1].type == "End" or df.iloc[index+1].type == "SubstitutionOff" or df.iloc[index+1].type == "SubstitutionOn"):
                continue 
        if(df.iloc[index+1].teamId != int(teamId)):
            continue
        else:
            carry['endX'] = df.iloc[index+1].x
            carry['endY'] = df.iloc[index+1].y
            carry['nextAction'] = df.iloc[index+1].type
            carry['keyPassEndingCarry'] = df.iloc[index+1].passKey
        carries_df = carries_df.append(carry,ignore_index=True)
        
        
    for index in carries_after_recov:
        carry = pd.Series()
        carry['matchId'] = df.iloc[index].matchId
        carry['minute'] = df.iloc[index].minute
        carry['playerId'] = df.iloc[index].playerId
        carry['x'] = df.iloc[index].x
        carry['y'] = df.iloc[index].y
        if(df.iloc[index+1].type == "OffsideGiven" or df.iloc[index+1].type == "End" or df.iloc[index+1].type == "SubstitutionOff" or df.iloc[index+1].type == "SubstitutionOn"):
            continue
        elif(df.iloc[index+1].type == "Challenge" and df.iloc[index+1].outcomeType == "Unsuccessful" and df.iloc[index+1].teamId != teamId):
            carry['playerId'] = df.iloc[index+2].playerId
            index += 1
            while((df.iloc[index+1].type == "TakeOn" and df.iloc[index+1].outcomeType == "Successful") or 
                  (df.iloc[index+1].type == "Challenge" and df.iloc[index+1].outcomeType == "Unsuccessful")):
                index += 1
            if(df.iloc[index+1].type == "OffsideGiven" or df.iloc[index+1].type == "End" or df.iloc[index+1].type == "SubstitutionOff" or df.iloc[index+1].type == "SubstitutionOn"):
                continue 
        if(df.iloc[index+1].playerId != df.iloc[index].playerId or df.iloc[index+1].teamId != int(teamId)):
            continue
        carry['endX'] = df.iloc[index+1].x
        carry['endY'] = df.iloc[index+1].y
        carry['nextAction'] = df.iloc[index+1].type
        carry['keyPassEndingCarry'] = df.iloc[index+1].passKey
        carries_df = carries_df.append(carry,ignore_index=True)
    
    carries_df['Removable'] = carries_df.apply(lambda row: checkCarryLength(row['x'], row['y'],row['endX'], row['endY']),axis = 1)
    carries_df = carries_df[carries_df['Removable']==False]
    
    carries_df['type']='Carry'
    carries_df['outcomeType']='Successful'
    carries_df.drop(['Removable'],axis=1,inplace=True)
    carries_df.reset_index(inplace=True,drop=True)
    
    return carries_df