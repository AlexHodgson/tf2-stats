# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 11:23:11 2020

Interacts with ETF2L and logs.tf APIs to get player data and store it in object

@author: Alex
"""

import json
import requests
import matplotlib.pyplot as plt
#import pandas as pd
import numpy as np
import matplotlib.dates
from datetime import datetime
import warnings
#import threading
import time

#logs.tf docs at http://logs.tf/about
logs_url_base = "http://logs.tf/api/v1/log"
full_log_url_base = "http://logs.tf/json/"

#etf2l docs can be found by following api url
etf2l_url_base = "https://api.etf2l.org/"
dataFormat = ".json"




class Player:
    '''
    Class to store information on a player's match history and logs
    for those matches, contains methods to collect said info
    
    '''
    
    def __init__(self,playerID):
        
        #Player ID is their ETF2L id
        self.playerID = playerID
        self.playerInfo = self.__get_player_info()
        self.playerMatches = self.__get_match_history()
        self.transferHistory = self.__get_match_history()
        self.tierHistory = np.transpose(np.array([[match['division']['tier'] for match in self.playerMatches if match['competition']['category'] == "6v6 Season"], [match['time']for match in self.playerMatches if match['competition']['category'] == "6v6 Season"]]))
        
        #ETF2L Name
        self.playerName = self.playerInfo['name']
        self.steamID64 = self.playerInfo['steam']['id64']
        #Stores logs.tf info for every match on a certain map
        self.mapLogInfo = {}
        
    
    
    def __get_player_info(self):
        '''Returns general info about a player'''
        
        idAsString = str(self.playerID)
        url = etf2l_url_base + "player/" + idAsString + dataFormat
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))['player']
        else:
            warnings.warn("Unable to retrieve player data, possibly invalid ID or issues with ETF2L API")
            return None
        
    def __get_match_history(self):
        '''Returns all matches a player has been in'''
        
        matches = []
        nextPage = True
        
        #Where to find the data
        idAsString = str(self.playerID)
        url = etf2l_url_base + "player/" + idAsString + "/results"+ dataFormat + "?since=0&per_page=100"
        
        #Keep going until there aren't any more pages
        while nextPage:
        
            response = requests.get(url)
            
            #Something bad happened
            if response.status_code != 200:
                return None
            
            #Only add if match has a time
            jsonResponse = json.loads(response.content.decode('utf-8'))
            matches.extend([match for match in jsonResponse['results'] if match['time'] is not None])
            
            
            if 'next_page_url' in jsonResponse['page'].keys():
                url = jsonResponse['page']['next_page_url']
            else:
                nextPage = False
        
        return matches
    
    
    def __get_transfer_history(self):
        '''Returns the last 100 transfers of a player (effectively all their transfers)'''
        
        idAsString = str(self.playerID)
        url = etf2l_url_base + "player/" + idAsString + "/transfers"+ dataFormat + "?since=0&per_page=100"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
        
    def find_official_logs(self,matches):
        '''
        Returns logs.tf IDs for a player's officials
        May get warm up games as well, but that's more good
        data so I'm cool with that
        '''
        
        officialLogIDs = []
        officialFullLogs = []
        
        #Get info on logs played on the same map as the official
        for match in matches:
            #Skip if no map or time data
            if 'maps' not in match.keys() or 'time' not in match.keys():
                continue
            officialMaps = match['maps']
            for officialMap in officialMaps:
                #Pull from logs.tf if we don't already have data
                if officialMap not in self.mapLogInfo.keys():
                    self.mapLogInfo[officialMap] = self.get_logs_info(officialMap)
                    
                #Then check for logs uploaded within 24 hours of game
                #Could use numpy arrays to find min value?
                #This is inefficient
                for logInfo in [log for log in self.mapLogInfo[officialMap] if log['date'] - match['time'] > 0]: 
                    if 0 < logInfo['date'] - match['time'] < 86400:
                        officialLogIDs.append(logInfo['id'])       
                        
        #Download logs for officials
        for log in officialLogIDs:
            fullLog = get_full_log(log)
            if fullLog:
                officialFullLogs.append(fullLog)
                        
        return officialFullLogs   
        
        
    def get_logs_info(self, gameMap="All_Maps"):
        '''Gets info on all logs for a player, can filter by map'''
        
        logsDownloaded = 0
        logsPerDownload = 10000 #How many logs per request
        moreLogs = True
        allLogInfo = []
        

        #Keep pulling logs until we have them all
        while moreLogs:
            
            #Whether to filter by map or not
            if gameMap == "All_Maps":
            
                url = logs_url_base + "?limit=" + str(logsPerDownload) + "&player=" + self.steamID64 + "&offset=" + str(logsDownloaded)
            else:
                url = logs_url_base + "?limit=" + str(logsPerDownload) + "&player=" + self.steamID64 + "&map=" + gameMap + "&offset=" + str(logsDownloaded)
   
            
            response = requests.get(url)
            #error somewhere
            if response.status_code != 200:
                return None
            
            logsJson = json.loads(response.content.decode('utf-8'))
            
            allLogInfo.extend(logsJson['logs'])
            
            logsDownloaded +=logsPerDownload
            
            if logsDownloaded >= logsJson['total']:
                moreLogs = False
        
        #print(allLogInfo)
        return allLogInfo

    
    def get_6s_matches(self):
        '''
        Selects matches played as part of a 6v6 season

        '''
        
        return [match for match in self.playerMatches if match['competition']['category'] == "6v6 Season"]

   
    def plot_div_progress(self):
        '''
        Plot player progress, from div 6 to prem
        Might move this outside of class
        '''
 
        #Convert from unix time to matplotlib date
        dates = matplotlib.dates.date2num([datetime.utcfromtimestamp(time) for time in self.tierHistory[:,1]])
        
        plt.title(self.playerName + " ETF2L Division Progress")
        plt.xlabel = "Date"
        plt.plot_date(dates,self.tierHistory[:,0], ms=3)
        ax = plt.gca()
        ax.set_xlabel("Match Date")
        ax.set_ylabel("Tier")
        ax.set_ylim([6.2,-0.2])
        
        plt.show()
        
    
        
    
def get_full_log(logID):
    '''Gets a full game log from logs.tf'''
    
    #try 3 times to get log from server
    url = full_log_url_base + str(logID)
    
    tries = 1
    response = requests.get(url)
    while response.status_code != 200 and tries < 3:
        print("Retrying log download, logID: " + str(logID))
        response = requests.get(url)
        if response.status_code != 200:
            time.sleep(0.1)
            
        tries += 1

    #Return log if found, error message if not
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Log not found, logID: " + str(logID))
        return None
     
  

##Some test cases
#testPlayer = Player(70219)
#print(testPlayer.playerName)
#playerMatches = testPlayer.playerMatches
#playerLogs = testPlayer.find_official_logs(testPlayer.get_6s_matches())


    
    