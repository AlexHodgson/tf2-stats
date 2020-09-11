# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 11:23:11 2020

Interacts with ETF2L and logs.tf APIs to get player data and store it in Player object

@author: Alex Hodgson
"""

from json import loads
from requests import get
import matplotlib.pyplot as plt
from pandas import DataFrame
from numpy import array, mean, transpose
import matplotlib.dates
from datetime import datetime
# import warnings
# import threading
from time import sleep
import time
import dicts_bisect

from log_processer import gameImpact, logToDataFrame
from sql_interface import write_player_info_to_db

# logs.tf docs at http://logs.tf/about
logs_url_base = "http://logs.tf/api/v1/log"
full_log_url_base = "http://logs.tf/json/"

# etf2l docs can be found by following api url
etf2l_url_base = "https://api.etf2l.org/"
dataFormat = ".json"

class Log:
    """
    TODO Fill this out to tidy up log data storage
    """

    def __init__(self, log_id):

        #logs.tf id
        self.logID = log_id
        self.log : dict

class Match:
    """
    TODO Fill this out to tidy up match data storage
    """

    def __init__(self, match_id):

        # ETF2L match ID
        self.matchID = match_id
        # List of playerIDs who were in this match
        self.players = []
        # List of logs.tf ids for this match
        self.logIDs = []



class Player:
    """
    Class to store information on a player's match history and logs
    for those matches, contains methods to collect said info

    """

    def __init__(self, playerID):

        # Player ID is their ETF2L id
        self.playerID = playerID
        self.playerInfo = self.__get_player_info()
        self.playerMatches = self.__get_match_history()
        self.transferHistory = self.__get_transfer_history()
        self.tierHistory = transpose(array([[self.playerMatches[match]['id'] for match in self.playerMatches.keys() if
                                             self.playerMatches[match]['competition']['category'] == "6v6 Season"],
                                            [self.playerMatches[match]['division']['tier'] for match in
                                             self.playerMatches.keys() if
                                             self.playerMatches[match]['competition']['category'] == "6v6 Season"],
                                            [self.playerMatches[match]['time'] for match in self.playerMatches.keys() if
                                             self.playerMatches[match]['competition']['category'] == "6v6 Season"]]))

        # ETF2L Name
        self.playerName = self.playerInfo['name']
        self.steamID = self.playerInfo['steam']['id']
        self.steamID64 = self.playerInfo['steam']['id64']
        self.steamID3 = "[" + self.playerInfo['steam']['id3'] + "]"
        # Stores logs.tf info for every match on a certain map
        self.mapLogInfo = {}
        # Log files already downloaded
        self.downloadedLogs = {}
        # Info on all logs is pretty small so get the whole lot
        # Reverse to be in ascending time order
        self.allLogs = self.get_logs_info()
        self.allLogs.reverse()

        print("Player data downloaded for: " + self.playerName)

        #Add player info to SQL Server
        self.upload_player_info()

    def __get_player_info(self):
        """
        Returns general info about a player

        Raises
        ------
        Exception
            Raised if the data for given id cannot be found on etf2l.

        Returns
        -------
        dict
            General player information, read etf2l docs for more info.

        """

        idAsString = str(self.playerID)
        url = etf2l_url_base + "player/" + idAsString + dataFormat

        response = get(url)

        if response.status_code == 200:
            return loads(response.content.decode('utf-8'))['player']
        else:
            # warnings.warn("Unable to retrieve player data, possibly invalid ID or issues with ETF2L API")
            raise Exception("Unable to retrieve player data, possibly invalid ID or issues with ETF2L API")

    def __get_match_history(self):
        '''
        Returns all etf2l matches a player has been in

        Returns
        -------
        matches : dict
            Etf2l match info with match ids as keys.

        '''

        matches = {}
        nextPage = True

        # Where to find the data
        idAsString = str(self.playerID)
        url = etf2l_url_base + "player/" + idAsString + "/results" + dataFormat + "?since=0&per_page=100"

        # Keep going until there aren't any more pages
        while nextPage:

            response = get(url)

            # Something bad happened
            if response.status_code != 200:
                return None

            # Only add if match has a time
            jsonResponse = loads(response.content.decode('utf-8'))
            for match in jsonResponse['results']:
                if match['time'] is not None:
                    matches[match['id']] = match

            if 'next_page_url' in jsonResponse['page'].keys():
                url = jsonResponse['page']['next_page_url']
            else:
                nextPage = False

        return matches

    def __get_transfer_history(self):
        '''
        Gets a player's transfer history from etf2l

        Returns
        -------
        dict
            Last 100 transfers of a player (effectively all their transfers).

        '''

        idAsString = str(self.playerID)
        url = etf2l_url_base + "player/" + idAsString + "/transfers" + dataFormat + "?since=0&per_page=100"

        response = get(url)

        if response.status_code == 200:
            return loads(response.content.decode('utf-8'))
        else:
            return None

    def find_official_logs(self, matches :dict):
        """
        Finds logs.tf ids for each etf2l match passed to it
        Uses binary sort to speed up process now a player object holds info on all their logs

        :param matches: dict
        dict of ETF2L match info with match ids as keys

        :return: dict
        dict with match ids as keys, containing list of logs.tf ids
        for the logs for that match
        """

        official_match_logs = {}

        for match_id in matches.keys():

            # Skip if no time info
            if 'time' not in matches[match_id].keys():
                continue

            if 'maps' in matches[match_id].keys():
                match_maps = matches[match_id]['maps']
            else:
                match_maps = ['variable']

            match_time = matches[match_id]['time']
            official_match_logs[match_id] = []


            # Find logs uploaded up to 8 hours after a match start
            # Binary search through log dates
            match_logs = self.allLogs[dicts_bisect.bisect_dicts_left(self.allLogs, match_time,'date')
                                      :dicts_bisect.bisect_dicts_left(self.allLogs, match_time + 28800,'date')]

            # Playoffs don't specify maps, so just take all logs in that case
            # Otherwise drop logs from the wrong maps, in case any were picked up
            if 'variable' not in match_maps:
                for match_log in match_logs:
                    if match_log['map'].lower() not in match_maps:
                        del match_log

            for match_log in match_logs:
                official_match_logs[match_id].append(match_log['id'])

        return official_match_logs

    def get_logs_info(self, gameMap ="All_Maps"):
        '''
        Gets info on all logs for a player, can filter by map

        Parameters
        ----------
        gameMap : String, optional
            The map to look for logs on. The default is "All_Maps".

        Returns
        -------
        allLogInfo : list
            logs.tf ids for logs of possible interest

        '''

        logsDownloaded = 0
        logsPerDownload = 10000  # How many logs per request
        moreLogs = True
        allLogInfo = []

        # Keep pulling logs until we have them all
        while moreLogs:

            # Whether to filter by map or not
            if gameMap == "All_Maps":
                url = logs_url_base + "?limit=" + str(logsPerDownload) + "&player=" + str(self.steamID64) + "&offset=" + str(
                    logsDownloaded)
            else:
                url = logs_url_base + "?limit=" + str(
                    logsPerDownload) + "&player=" + str(self.steamID64) + "&map=" + gameMap + "&offset=" + str(
                    logsDownloaded)

            response = get(url)
            # error somewhere
            # TODO Handle this better
            if response.status_code != 200:
                print("Error getting log info from logs.tf")
                continue

            logsJson = loads(response.content.decode('utf-8'))

            allLogInfo.extend(logsJson['logs'])

            logsDownloaded += logsPerDownload

            if logsDownloaded >= logsJson['total']:
                moreLogs = False


        return allLogInfo

    def get_6s_matches(self):
        '''
        Selects matches played as part of a 6v6 season

        Returns
        -------
        matches : dict
            Matches played in a 6v6 season, match ids as keys.

        '''

        matches = {}

        for matchID in self.playerMatches.keys():
            if self.playerMatches[matchID]['competition']['category'] == "6v6 Season":
                matches[matchID] = self.playerMatches[matchID]

        return matches

    def plot_div_progress(self, plot=True):
        '''
        Plot player progress, from div 6 to prem
        Either plots the graph or returns it's data'

        Parameters
        ----------
        plot : Bool, optional
            If the function should plot the graph itself in a new window.
            The default is True.

        Returns
        -------
        ax : plt plot

        '''

        # Get score to use as size of plot point
        playerImpactScore = []
        start_time  = time.time()
        for matchID in self.tierHistory[:, 0]:
            # find_official_logs requires a dictionary, so can pass dict of length 1
            matchLogIDs = self.find_official_logs({matchID: self.playerMatches[matchID]})[matchID]
            matchLogs = []

            for log_id in matchLogIDs:

                matchLogs.append(get_full_log(log_id))

            self.find_official_logs({matchID: self.playerMatches[matchID]})
            playerImpactScore.append(gameImpact(self, matchLogs))


        end_time = time.time()
        print("Time to find log ids: " + str(end_time- start_time))
        # This is just (dpm/ heals%)^2 at the moment
        # Normalise for sensible marker sizes
        playerImpactScore = normalize_rows(array(playerImpactScore)) * 300

        # Give size to markers for matches without logs
        avgImpact = mean(playerImpactScore)

        # Convert from unix time to matplotlib date
        dates = matplotlib.dates.date2num([datetime.utcfromtimestamp(time) for time in self.tierHistory[:, 2]])

        # Either plot the graph or return it to be handled higher up
        if plot:
            # plot circles for matches with stats, a cross if no data found
            fig = plt.figure()
            ax = fig.add_axes([0, 0, 1, 1])
            ax.scatter(dates[playerImpactScore > 0], self.tierHistory[:, 1][playerImpactScore > 0],
                       s=playerImpactScore[playerImpactScore > 0], alpha=0.6, marker='o')
            ax.scatter(dates[playerImpactScore == 0], self.tierHistory[:, 1][playerImpactScore == 0], s=avgImpact / 2,
                       alpha=0.6, marker='x', c="Red")
            # ax = plt.gca()
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
            ax.set_title(self.playerName + " ETF2L Division Progress")
            ax.set_xlabel("Match Date")
            ax.set_ylabel("Tier")
            ax.set_ylim([6.2, -0.2])
            plt.show()
        else:

            matchData = DataFrame({'time': dates, 'div': self.tierHistory[:, 1], 'impact': playerImpactScore})
            return matchData

    def performance_history_to_df(self):

        performance_history: DataFrame
        # Add performance data to dataframe
        for matchID in self.tierHistory[:, 0]:
            # find_official_logs requires a dictionary, so can pass dict of length 1
            matchLogs = self.find_official_logs({matchID: self.playerMatches[matchID]})
            performance_history = performance_history.append(logToDataFrame(self, matchID, matchLogs[matchID]))

        return performance_history

    def upload_player_info(self):
        """
        Send player data to sql_interface to attempt upload to sql server
        TODO Find a new hash library for consistent hashes across each run
        """
        # Add hash to check if data is different to server's version
        player_info_dict = {'ETF2L_ID': self.playerID, 'Name': self.playerName, 'Steam_ID': self.steamID, 'Join_Date': self.playerInfo['registered']}
        player_info_dict['hash'] = hash(player_info_dict.values())

        #player_info = DataFrame(player_info_dict, index = [0])
        #print(player_info)

        write_player_info_to_db(player_info_dict)




def get_full_log(logID):
    '''
    Gets a full game log from logs.tf

    Parameters
    ----------
    logID : int
        id of logs.tf log

    Returns
    -------
    dict
        The full log

    '''

    # try 3 times to get log from server
    url = full_log_url_base + str(logID)

    tries = 1
    response = get(url)
    while response.status_code != 200 and tries <= 4:
        # print("Retrying log download, logID: " + str(logID))
        response = get(url)
        if response.status_code != 200:
            sleep(0.2 * tries)

        tries += 1

    # Return log if found, error message if not
    if response.status_code == 200:
        return loads(response.content.decode('utf-8'))
    else:
        print("Log not found, logID: " + str(logID))
        return None


def normalize_rows(x):
    return x / mean(x)



##Some test cases
#testPlayer = Player(97913)
# print(testPlayer.playerName)
# playerMatches = testPlayer.playerMatches
#playerLogs = testPlayer.find_official_logs(testPlayer.get_6s_matches())
#print(playerLogs)
#testPlayer.upload_player_info()
