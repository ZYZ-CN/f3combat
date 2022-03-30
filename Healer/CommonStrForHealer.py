from functools import cache
from math import radians
from turtle import end_fill
from XivCombat.utils import a, s, cnt_enemy, res_lv, find_area_belongs_to_me
from XivCombat.strategies import *
from XivCombat import define, api
from XivCombat.multi_enemy_selector import Rectangle, NearCircle, circle, FarCircle



#Some abbreviation
'''
White Mage = WM
Astrologian = AST
Sage = SAG
Scholar = SCH
'''
#HP percent
def hp_percent(actor: 'api.Actor'):
    return actor.current_hp / actor.max_hp

#Healing Strategy
def HealingStgy():
    '''
    AOE Healing = Num of charactor needed >=3
    ONE Healing = Num of charactor needed <=2

    Big Healing = HP<=50%
    Small Healing = HP>=50

    '''




#Healing Resourses 
def HResourses():




#0GCD



