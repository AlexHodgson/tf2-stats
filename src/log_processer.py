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
        
        #Older logs use steamID3
        if steamID not in log['players'].keys():
            steamID = player.steamID3

        #Check which team the player was on
        if log['players'][steamID]['team'] == 'Red':
            playerTeam = GameTeam.RED
        elif log['players'][steamID]['team'] == 'Blue':
            playerTeam = GameTeam.BLU
        
        #Get some provided stats, for some reason ka/d is a string
        matchStats['mainClass'].append(mainClass(steamID, log))
        matchStats['dpm'].append(log['players'][steamID]['dapm'])
        matchStats['kad'].append(float(log['players'][steamID]['kapd']))
        matchStats['caps'].append(log['players'][steamID]['cpc'])
        
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
    
    #Check if any damage was found, then average over maps
    if len(matchStats['dpm']) == 0:
        matchStats['dpm'] = 0
    else:
        matchStats['dpm'] = mean(matchStats['dpm'])
        
    #Check if any kills or assists were found, then average over maps
    if len(matchStats['kad']) == 0:
        matchStats['kad'] = 0
    else:
        matchStats['kad'] = mean(matchStats['kad'])
        
        #Check if any caps were found, then average over maps
    if len(matchStats['caps']) == 0:
        matchStats['caps'] = 0
    else:
        matchStats['caps'] = mean(matchStats['caps'])
        
    #Check if any big picks were found, then average over maps
    if len(matchStats['bigPicks']) == 0:
        matchStats['bigPicks'] = 0
    else:
        matchStats['bigPicks'] = mean(matchStats['bigPicks'])
    
    #Check if airshot stats were recorded
    if len(matchStats['airshots']) > 0:
        matchStats['airshots'] = mean(matchStats['airshots'])
    else:
        matchStats['airshots'] = None
    
    #For now only return dpm^4 for testing
    #print(matchStats['dpm'])
    return matchStats['dpm']**4
    
#testPlayer = Player(70219)
    
#def medicScore(steamID,log):
    
    
