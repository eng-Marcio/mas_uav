#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from search import SearchProblem
from search import aStarSearch
import random
import math

class Mapping_System(SearchProblem):
    def __init__(self,controler):
        ##maintain pointer to controler
        self.controler = controler
        self.pathFinder = SearchProblem(self)
        self.map = self.buildMap(120, 120, 0.05)

        self.offsetX = -10     #
        self.offsetY = -10     # constants to convert matrix to gps
        self.resolution = 0.25  #

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
        self.goal = [100, 100]
        self.map[10][10] = 0
        self.map[100][100] = 0  #guarantee that origin and destination are reachable
        self.path = aStarSearch(self.pathFinder)
        print(self.path)


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
    
    #build a map 30mx30m: 25cm resolution >>array 120x120
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
    
    def printMap(self):
        mapp = self.map
        ##add the path
        x, y = self.cur_pos
        for i in self.path:
            if i=='L':
                x = x-1
            elif i=='R':
                x = x+1
            elif i=='N':
                y = y+1
            elif i=='S':
                y = y-1
            if(mapp[x][y] == 0):
                mapp[x][y] = 2
            else:
                mapp[x][y] = 3
            
        limit = len(mapp[0])
        for y in range(len(mapp[0])):
            string = ""
            for x in range(len(mapp)):
                if(mapp[x][limit - y - 1] == 0): #no obstacle
                    string = string + "-"
                elif(mapp[x][limit - y - 1] == 1): #obstacle
                    string = string + "#"
                elif(mapp[x][limit - y - 1] == 2): #path
                    string = string + "o"
                elif(mapp[x][limit - y - 1] == 3): #colision
                    string = string + "x"
            print(string)

    def updateCurrentMap(self,posXUAVGPS,posYUAVGPS,AngleUAVGPS,inputLidarArray):
        angleInArray = 0 ## 0 - 270
        print("inici update Map")

        while(angleInArray<len(inputLidarArray)):
            if (inputLidarArray[angleInArray]>0.5):
                totalAngle = (((angleInArray-45)+AngleUAVGPS)*math.pi)/(180)## angleInArray em graus, AngleUAV graus tbms. angleInArray-45 parar desconsiderar o inicio da varredura anti-horaria
                PosXObstToUAVGPS = math.cos(totalAngle)*inputLidarArray[angleInArray]
                PosYObstToUAVGPS = math.sin(totalAngle)*inputLidarArray[angleInArray]
                PosXObstGPS = posXUAVGPS+PosXObstToUAVGPS
                PosYObstGPS = posYUAVGPS+PosYObstToUAVGPS

                PosObstMatrix = self.GPSToMatrix(PosXObstGPS,PosYObstGPS)
                print("PosObstMatrix x e y",int(PosObstMatrix[0]),int(PosObstMatrix[1]))
                self.map[int(PosObstMatrix[0])][int(PosObstMatrix[1])]=1## update the map
           
            angleInArray +=1