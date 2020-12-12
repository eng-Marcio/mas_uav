#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from search import SearchProblem
from search import aStarSearch
import random
import math
import csv
import rospy
import copy

class Mapping_System(SearchProblem):
    def __init__(self,controler):
        ##maintain pointer to controler
        self.controler = controler
        self.path = []
        self.pathCells = []
        self.offsetX = -10     #
        self.offsetY = -10     # constants to convert matrix to gps
        self.resolution = 0.25  #
        #self.resolution = 0.5  #
        

    def matrixToGPS(self, xMat, yMat):
        xgps = (xMat + self.offsetX)*self.resolution
        ygps = (yMat + self.offsetY)*self.resolution 
        return [xgps, ygps]
    
    def GPSToMatrix(self, xGPS, yGPS):
        xMat = int(round(xGPS/self.resolution) - self.offsetX)
        yMat = int(round(yGPS/self.resolution) - self.offsetY)
        return [xMat, yMat]

    def start(self):##starts the operating variables
        self.pathFinder = SearchProblem(self)
        #build a map 30mx30m: 25cm resolution >>array 120x120 with obstacles
        #self.map = self.buildRealisticMap(40, 40) #(120,120,0.02)
        #self.map = self.buildMap(120, 120,0) #(120,120,0.02)
        self.buildCSVMaps()


    def trajectoryService(self):
        curr = self.controler.perceptions.getPos()
        des = self.controler.actions.des
        self.cur_pos = self.GPSToMatrix(curr[0], curr[1])
        self.goal = self.GPSToMatrix(des.x, des.y)
        self.path = self.getFlightPlan()

        return self.convertToCoord(self.path)

    ## Mapping_System mathods
    def getFlightPlan(self): 
        self.path = aStarSearch(self.pathFinder)
        return self.path

    def convertToCoord(self,pathCommands):## this function removes coordinates from the middle of a line and build diagonal paths(useless coordinates)
        ##get start destination from current positions, z does not change
        z = self.controler.actions.des.z
        x, y = self.matrixToGPS(self.cur_pos[0], self.cur_pos[1])
        angle = -1
        res = []
        self.pathCells = []
        self.pathCells.append([x,y])
        #loops through A* commands
        i = 0
        while(i < len(pathCommands)):
            delta = self.deltaDist(pathCommands[i])
            x = x + delta[0]
            y = y + delta[1]
            self.pathCells.append([x,y])
            newAngle = delta[2]
            if((i != 0)and(i  != len(pathCommands)- 1)): #you must have 3 elements to check diagonals
                ##criteria for diagonals, they are always 101: RNR, LSL, SRS
                if((pathCommands[i-1] == pathCommands[i+1])and(pathCommands[i]!= pathCommands[i+1])): 
                    delta2= self.deltaDist(pathCommands[i+1])
                    x = x + delta2[0]
                    y = y + delta2[1]
                    if(abs(delta2[2]-newAngle) > 90): ##270 exception
                        newAngle = 315
                    else:
                        newAngle = (delta2[2]+newAngle)/2  ##mix of 2 angles is a mean on this case
                    i = i+1 ##jump one command more
            if(newAngle == angle): ##if it is on the same orientation, replace element
                del res[-1]
            res.append([x,y,z,newAngle])
            angle = newAngle
            i = i+1
        return res
    
    def deltaDist(self, com):
        if(com == 'N'):
            return [0, self.resolution, 90]
        if(com == 'S'):
            return [0, -self.resolution, 270]
        if(com == 'L'):
            return [-self.resolution, 0, 180]
        if(com == 'R'):
            return [self.resolution, 0, 0]
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
    
    def buildRealisticMap(self, sizeX, sizeY):
        mapp = self.buildMap(sizeX,sizeY,0)
        i = 8
        j = 16
        while (i<22):
            while(j<26):
                mapp[i][j] = 1
                j+=1
            j = 16
            i+=1
        return mapp
    
    def readMapFromCSVFile(self, address):
        
        cr = csv.reader(open(address,"rb"))
        strMap = list(cr)
        map = []
        for i in range(len(strMap)):
            line = []
            for j in range(len(strMap[0])):
                if('1' in strMap[i][j]):
                    line.append(1)
                else:
                    line.append(0)                
            map.append(line)
        return map
        

    def buildCSVMaps(self):
        self.map = self.readMapFromCSVFile("/home/marcio/jason_ros_ws/src/mas_uav/KnownMap.csv")
        self.RealMap = self.readMapFromCSVFile("/home/marcio/jason_ros_ws/src/mas_uav/RealMap.csv")

    def checkCollision(self, obsPos):
        for pos in self.pathCells:
            if(abs(pos[0]-obsPos[0])<=1 and abs(pos[1]-obsPos[1])<=1):
                return True #possible collision detected
        return False

    def lidarTask(self, cur_pos): #lidar has 1.5 meter range >> 6 cells for each direction
        collision = False
        for i in range(13):
            for j in range(13):
                x = cur_pos[0] + i - 6
                y = cur_pos[1] + j - 6
                if((self.dist(x,y,cur_pos[0], cur_pos[1]) > 6) or (x >= len(self.map) or y >= len(self.map[0]))):
                    continue
                if(self.RealMap[x][y] == 1 and self.map[x][y] == 0): #new obstacle found
                    self.map[x][y] = 1
                    if(self.checkCollision([x,y])):
                        collision = True

        if collision:
            self.controler.trajectoryState = self.controler.T_None

    def dist(self, a1, a2, b1, b2):
        return math.sqrt((a1 - b1)**2+(a2 - b2)**2)
    
    def printMap(self):
        mapp = self.map
        ##add the path
        #x, y = self.cur_pos
        curr = self.controler.perceptions.getPos()
        x, y = self.GPSToMatrix(curr[0], curr[1])
        mapp[x][y] = 4
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
                    string = string + " "
                elif(mapp[x][limit - y - 1] == 1): #obstacle
                    string = string + "#"
                elif(mapp[x][limit - y - 1] == 2): #path
                    string = string + "o"
                elif(mapp[x][limit - y - 1] == 3): #colision
                    string = string + "c" 
                elif(mapp[x][limit - y - 1] == 4): #drone
                    string = string + "X"
            print(string)
            
    
    


    def updateCurrentMap(self,posXUAVGPS,posYUAVGPS,AngleUAVGPS,inputLidarArray=0):
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
        PosUAVMatrix = self.GPSToMatrix(posXUAVGPS,posYUAVGPS)
        #self.map[int(PosUAVMatrix[0])][int(PosUAVMatrix[1])]= 8 ## update the map with drone position

    
    def updateCurrentMapInterface(self,miniMap=0):## this function updates the txt file used as an interface to monitor the development of the map
        localMap = self.map
        posUAVGPS = self.controler.perceptions.getPos()
        PosUAVMatrix = self.GPSToMatrix(posUAVGPS[0],posUAVGPS[1])
        localMap[int(PosUAVMatrix[0])][int(PosUAVMatrix[1])]= 8
        fileText = open("CurrentMap.txt","w")## clean what has in this file
        fileText.close()

        lines = list()
        
        if(miniMap == 0):
            fileText = open("CurrentMap.txt","a")
            j=0
            while (j<120):
                var = localMap[j]
                lines.append('{} --> {}\n'.format(var,j))## add map line in the list
                j+=1
            fileText.writelines(lines)
            fileText.close()
            print("updated CurrentMinimizedFile")
        else:
            lines = miniMap
            fileText = open("CurrentMap.txt","a")
            fileText.writelines(lines)
            fileText.close()
            print("updated CurrentMinimizedFile")
            
        return 

    def getCurrentMapString(self):
        i=0
        listMapLines = []
        while (i<len(self.map)):
            listMapLines.append(str(self.map[i]).strip('[]'))
            i+=1
        return '\n'.join(map(str,listMapLines))

    def getCurrentMinimizedMapString(self):
        localMap = copy.deepcopy(self.map)
        posUAVGPS = self.controler.perceptions.getPos()
        PosUAVMatrix = self.GPSToMatrix(posUAVGPS[0],posUAVGPS[1])
        localMap[int(PosUAVMatrix[0])][int(PosUAVMatrix[1])]= 8
        i=0
        j=0 
        minimizedMap = self.buildMap(len(localMap)/2, len(localMap)/2, 0)
        
        if(len(self.controler.trajectory)>1):
            for y in range(len(self.controler.trajectory)):
                checkpointTraj = self.GPSToMatrix(self.controler.trajectory[y][0],self.controler.trajectory[y][1])
                localMap[int(checkpointTraj[0])][int(checkpointTraj[1])]= -4

        while (i<(len(localMap)/2)):
            while (j<(len(localMap)/2)-1):
                minimizedMap[i][j] = localMap[i*2][j*2]+localMap[(i*2)+1][j*2]+localMap[i*2][(j*2)+1]+localMap[(i*2)+1][(j*2)+1]
                if(minimizedMap[i][j]>=8):
                    minimizedMap[i][j] = 8#drone is here
                if(minimizedMap[i][j]<0):
                    minimizedMap[i][j] = 9#checkpoint is here
                j+=1
            j=0
            i+=1
        i=0
        listMapLines = []
        while (i<len(minimizedMap)):
            listMapLines.append(str(minimizedMap[(len(minimizedMap)-1)-i]).strip('[]'))
            i+=1
        text = '\n'.join(map(str,listMapLines))
        text = text.replace(","," ")
        text = text.replace("8","X")#drone
        text = text.replace("0"," ")
        return text.replace("9","O")#checkPoint of trajectory

    def createForsedLidarArray(self,range = 270, max = 5):##create a signal similar to the one that would come from dealing, function for testing
        i=0
        arrayLidar = []
        while(i<range):
            
            if (i>135 and i<180):
                arrayLidar.append(1)
            else:
                arrayLidar.append(1)
            i+=1
        return arrayLidar

if __name__ == '__main__':
    mapp = Mapping_System(None)
    mapp.start()
    mapp.pathCells = []
    mapp.pathCells.append([13,15])
    mapp.lidarTask([13,13])
    print(mapp.map)
