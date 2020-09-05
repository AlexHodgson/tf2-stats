# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 14:15:20 2020

Class to enumerate tf2 classes and teams

@author: Alex
"""

from enum import Enum, auto

class GameClass(Enum):
    MEDIC = auto()
    DEMOMAN = auto()
    SOLDIER = auto()
    SCOUT = auto()
    SNIPER = auto()
    HEAVY = auto()
    PYRO = auto()
    ENGINEER = auto()
    SPY = auto()
    
class GameTeam(Enum):
    BLU = auto()
    RED = auto()