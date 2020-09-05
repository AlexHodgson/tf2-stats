# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 15:55:59 2020

tkinter GUI to interact with the Player class and show progress graph

@author: Alex
"""

import tkinter
from api_interface import Player
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

loadedPlayers = {}

#Show graph of player progress when button is clicked
def call_progress_plot():
    idAsString = e.get()
    idAsInt = int(idAsString)
    
    if idAsInt not in loadedPlayers.keys():
        
        print ("Downloading Player Data for ID: " + idAsString)
        player = Player(idAsInt)
        loadedPlayers[idAsInt] = player
        
    else:
        print("Player Info For " + loadedPlayers[idAsInt].playerName + " (" + idAsString + ") Already Downloaded")
        player = loadedPlayers[idAsInt]
        
    #call the function from Player object
    player.plot_div_progress()
    

#Window for inputting player ID
master = tkinter.Tk()
master.title("ETF2L Progress Tracker")

canvas = tkinter.Canvas(master, width=250, height=100)  # define the size


topFrame = tkinter.Frame(master)
topFrame.pack(side= tkinter.TOP)

bottomFrame = tkinter.Frame(master)
bottomFrame.pack(side= tkinter.BOTTOM)

idLabel = tkinter.Label(topFrame, text="ETF2L ID")
idLabel.pack( side = tkinter.LEFT)

e = tkinter.Entry(topFrame, width=25)
e.pack(side = tkinter.RIGHT)

canvas.pack()

e.focus_set()

buttonPlot = tkinter.Button(bottomFrame, text="Plot Player Progress", width=15, command=call_progress_plot)
buttonPlot.pack()

master.mainloop()


        