# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 22:00:38 2020

For calculating performance ratings from logs

@author: Alex
"""

#from api_interface import Player
from tf2_classes import GameClass, GameTeam
from statistics import mean, mode

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
            
    if mainClass == "medic":
        return GameClass.MEDIC
    elif mainClass == "demoman":
        return GameClass.DEMOMAN
    elif mainClass == "soldier":
        return GameClass.SOLDIER
    elif mainClass == "scout":
        return GameClass.SCOUT
    elif mainClass == "sniper":
        return GameClass.SNIPER
    elif mainClass == "heavyweapons":
        return GameClass.HEAVY    
    elif mainClass == "pyro":
        return GameClass.PYRO
    elif mainClass == "engineer":
        return GameClass.ENGINEER  
    elif mainClass == "spy":
        return GameClass.SPY  


def gameImpact(player, fullLog):
    '''
    

    Parameters
    ----------
    player : Player object
        player object for the gamer in question
    fullLog : dict
        All full log files for an official match
    Returns
    -------
    dpm : int
    Damage per minute for player, placeholder for full performance evaluation

    '''
    
    steamID = player.steamID
    matchStats = {'mainClass' : [], 'dpm' : [], 'kad' : [], 'bigPicks' : [], 'airshots' : [], 'caps' : [], 'pct_hr' : []}
    #Class with most time per map
    #Damage per minute
    #Kills + assists per death
    #Number of med and demo kills
    #The most important stat
    #Point caps
    #Percentage of heals recieved
    for log in fullLog:
        
        #Check which team the player was on
        if log['players'][steamID]['team'] == 'Red':
            playerTeam = GameTeam.RED
        elif log['players'][steamID]['team'] == 'Blue':
            playerTeam = GameTeam.BLU
        
        #Get some provided stats
        matchStats['mainClass'].append(mainClass(steamID, log))
        matchStats['dpm'].append(log['players'][steamID]['dapm'])
        matchStats['kad'].append(log['players'][steamID]['kapd'])
        matchStats['caps'].append(log['players'][steamID]['cpc'])
        
        #Airshots
        if 'as' in log['players'][steamID].keys():
            matchStats['airshots'].append(log['players'][steamID]['as'])
        
        #Important kills
        bigPicks = 0
        if 'medic' in log['classKills'][steamID].keys():
            bigPicks += log['classKills'][steamID]['medic']
        if 'demoman' in log['classKills'][steamID].keys():
            bigPicks += log['classKills'][steamID]['medic']
            
        matchStats['bigPicks'].append(bigPicks)
        
        
        #Get percentage of heals recieved
        for medic in log['healspread']:
            if steamID in medic.keys():
                totalHeals = 0
                for healsRec in medic.values():
                    totalHeals += healsRec 
                matchStats['pct_hr'].append((medic[steamID] / totalHeals) * 100)
    
    #Add up or average for the whole game
    #Will extend the class choice if different classes were played on each map
    matchStats['mainClass'] = mode(['mainClass'])
    matchStats['dpm'] = mean(matchStats['dpm'])
    matchStats['kad'] = mean(matchStats['kad'])
    matchStats['caps'] = mean(matchStats['caps'])
    matchStats['bigPicks'] = mean(matchStats['bigPicks'])
    
    #Check if airshot stats were recorded
    if len(matchStats['airshots']) > 0:
        matchStats['airshots'] = mean(matchStats['airshots'])
    else:
        matchStats['airshots'] = None
    
    #For now only return dpm for testing
    print(matchStats['dpm'])
    return matchStats['dpm']
    
#testPlayer = Player(70219)
    
#def medicScore(steamID,log):
    
    