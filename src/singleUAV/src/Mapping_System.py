#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from search import SearchProblem
from search import uniformCostSearch
import random

class Mapping_System(SearchProblem):
    def __init__(self,controler):
        ##maintain pointer to controler
        self.controler = controler
        #self.pathFinder = SearchProblem(self)
        self.map = self.buildMap(60, 60, 0.3)

        self.offsetX = -10     #
        self.offsetY = -10     # constants to convert matrix to gps
        self.resolution = 0.5  #

    def matrixToGPS(self, xMat, yMat):
        xgps = (xMat + self.offsetX)*self.resolution
        ygps = (yMat + self.offsetY)*self.resolution 
        return [xgps, ygps]
    
    def GPSToMatrix(self, xGPS, yGPS):
        xMat = round(xGPS/self.resolution) - self.offsetX
        yMat = round(yGPS/self.resolution) - self.offsetY
        return [xMat, yMat]

    def start(self):##starts the operating variables
        self.cur_pos = [10, 10]
        self.goal = [50, 50]
        self.map[1][1] = 0
        self.map[28][28] = 0  #guarantee that origin and destination are reachable
        #path = uniformCostSearch(self.pathFinder)
        #print path


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
    
    #build a map 30mx30m: 50cm resolution >>array 60x60
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