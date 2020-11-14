#!/usr/bin/env python2
import rospy
import std_msgs.msg 


class Mapping_System:

    def _init_(self,controler):
        ##maintain pointer to controler
        self.controler = controler
        

    def start(self):##starts the operating variables
        self.currentMap = []

    ## Mapping_System mathods
    def makeFlightPlan(self,corruntCoords,destCoords): ## tem que refazer,chamar a função recalcula rota
        #ArrayPlan = findPathByAStar(corruntCoords,destCoords)
        ArrayPlan = [(1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,1.0)]## só um exemplo
        return ArrayPlan

    def findPathByAStar(self,corruntCoords,destCoords):## tem que refazer,função A*
        return 0
    
    def optimizesFlightPlanArray(self,ArrayPlan):## this function removes coordinates from the middle of a line (useless coordinates)
        ##não ta pronta
        return 0
    