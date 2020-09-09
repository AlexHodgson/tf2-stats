# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 22:00:38 2020

For calculating performance ratings from logs

@author: Alex
"""

#from api_interface import Player
#from tf2_classes import GameClass, GameTeam
from statistics import mean, mode
import pandas as pd
#import math


def mainClass(steamID, log):
    '''
    

    Parameters
    ----------
    steamID : string
        Player's steam id
    log : dict
        Full log file for one map

    Returns
    -------
    The class the player played the most during the map

    '''
    
    classStats = log['players'][steamID]['class_stats']
    
    mainClass = None
    maxTime = 0
    for playedClass in classStats:
        if playedClass['total_time'] > maxTime:
            mainClass = playedClass['type']

    return mainClass

    # if mainClass == "medic":
    #     return GameClass.MEDIC
    # elif mainClass == "demoman":
    #     return GameClass.DEMOMAN
    # elif mainClass == "soldier":
    #     return GameClass.SOLDIER
    # elif mainClass == "scout":
    #     return GameClass.SCOUT
    # elif mainClass == "sniper":
    #     return GameClass.SNIPER
    # elif mainClass == "heavyweapons":
    #     return GameClass.HEAVY
    # elif mainClass == "pyro":
    #     return GameClass.PYRO
    # elif mainClass == "engineer":
    #     return GameClass.ENGINEER
    # elif mainClass == "spy":
    #     return GameClass.SPY


def gameImpact(player, fullLog, calculateScore = True):
    '''
    

    Parameters
    ----------
    player : Player object
        player object for the gamer in question
    fullLog : dict
        All full log files for an official match
    calculateScore : bool
        If the function returns the performance score(True)
        or a DataFrame of important stats (False)
    Returns
    -------
    dpm : int
    Damage per minute for player, placeholder for full performance evaluation

    '''

    
    steamID = player.steamID
    matchStats = {'mainClass' : [], 'dpm' : [], 'kad' : [], 'kills' : [], 'assists' : [], 'deaths' : [], 'bigPicks' : [], 'airshots' : [], 'caps' : [], 'pct_hr' : []}
    #Class with most time per map
    #Damage per minute
    #Kills + assists per death
    #Number of med and demo kills
    #The most important stat
    #Point caps
    #Percentage of heals recieved
    for log in fullLog:
        
        #Older logs use steamID3
        if steamID not in log['players'].keys():
            steamID = player.steamID3

        # #Check which team the player was on
        playerTeam = log['players'][steamID]['team']

        # if log['players'][steamID]['team'] == 'Red':
        #     playerTeam = GameTeam.RED
        # elif log['players'][steamID]['team'] == 'Blue':
        #     playerTeam = GameTeam.BLU
        
        # Get some provided stats, for some reason ka/d is a string
        # TODO Make this a function for the repeatable retrievals
        matchStats['mainClass'].append(mainClass(steamID, log))
        matchStats['dpm'].append(log['players'][steamID]['dapm'])
        matchStats['kad'].append(float(log['players'][steamID]['kapd']))
        matchStats['caps'].append(log['players'][steamID]['cpc'])
        matchStats['kills'].append(log['players'][steamID]['kills'])
        matchStats['assists'].append(log['players'][steamID]['assists'])
        matchStats['deaths'].append(log['players'][steamID]['deaths'])
#        matchStats['ubers'].append(log['players'][steamID]['ubers'])
#       matchStats['drops'].append(log['players'][steamID]['drops'])
        
        #Airshots
        if 'as' in log['players'][steamID].keys():
            matchStats['airshots'].append(log['players'][steamID]['as'])
        
        #Important kills, check if player has any kills at all first
        bigPicks = 0
        if steamID in log['classkills'].keys():
            if 'medic' in log['classkills'][steamID].keys():
                bigPicks += log['classkills'][steamID]['medic']
            if 'demoman' in log['classkills'][steamID].keys():
                bigPicks += log['classkills'][steamID]['demoman']
            
        matchStats['bigPicks'].append(bigPicks)
        
        
        #Get percentage of heals recieved
        for medicID in log['healspread'].keys():
            if steamID in log['healspread'][medicID].keys():
                totalHeals = 0
                for healsRec in log['healspread'][medicID].values():
                    totalHeals += healsRec 
                matchStats['pct_hr'].append((log['healspread'][medicID][steamID] / totalHeals) * 100)
    
    #Add up or average for the whole game
    #Will extend the class choice if different classes were played on each map
    matchStats['mainClass'] = mode(['mainClass'])

    #Average performance across all maps
    for key in matchStats.keys():
        if key == 'mainClass':
            continue
        elif key == 'pct_hr':
            if len(matchStats[key]) == 0:
                matchStats[key] = 1 #Can't be dividing by 0 so set this to 1
            else:
                matchStats[key] = mean(matchStats[key])
        else:
            if len(matchStats[key]) == 0:
                matchStats[key] = 0
            else:
                matchStats[key] = mean(matchStats[key])

    
    #For now return simplified score
    #print(matchStats['dpm'])

    if calculateScore:
        return (matchStats['dpm']/matchStats['pct_hr'])**2
    else:
        return pd.DataFrame(matchStats)



def logToDataFrame(player, matchID, fullLog):
    """"
    Converts a full log file to a data frame row detailing performance in a match for upload to SQL server

    """

    player_id: int = player.playerID
    match_id: int = matchID

    # Use the game impact calculator to collect important stats
    match_stats = gameImpact(player, fullLog, calculateScore=False)

    match_stats['player_id'] = player_id
    match_stats['match_id'] = match_id

    # Generate a hash so local data can be compared with server data
    match_stats['hash'] = match_stats.apply(lambda x: hash(tuple(x)), axis = 1)

    return match_stats




#testPlayer = Player(70219)
    
#def medicScore(steamID,log):
    
    
