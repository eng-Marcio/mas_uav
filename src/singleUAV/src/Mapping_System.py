#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import random

class Mapping_System:

    def __init__(self,controler):
        ##maintain pointer to controler
        self.controler = controler
        

    def start(self):##starts the operating variables
        self.map = self.buildMap(30, 30, 0.3)

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
    
    #build a map 40mx40m: 50cm resolution >>array 80x80
    def buildMap(self, sizeX, sizeY, qtd_obs):
        arr = []
        for i in range(sizeX):
            line = []
            for j in range(sizeY):
                if((j == 0) or (j == (sizeY-1)) or (i==0) or (i == (sizeX-1))): #limits of the map are the walls
                    line.append(1)
                else:
                    if(random.random() < qtd_obs):
                        line.append(1)
                    else:
                        line.append(0)
            arr.append(line)

        return arr