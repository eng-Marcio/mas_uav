#!/usr/bin/env python2
import time
from threading import Thread
from threading import RLock
import zmq

class Com_FMC:
    def __init__(self, controler):
        from singleUAV import Controler

        ##maintain pointer to controler
        self.controler = controler

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:5515") ##comunication server with fmc stays opened in port 5515 of localhost

        ##these is like a dictionary to better comprehend what's going on with the state os state machine
        self.NameStateList = ["S_Awaiting","S_takeOff","S_HoldPos","S_RunTrajAlgo","S_Moving ","S_TrackSmoke ","S_InformFMC ","S_Landing ","S_InformAndWaitFMC","S_Fatal_Error "]

        ##initialize communication server
        self.thread = Thread(target=self.listenSocket)
        self.terminate = False
        self.thread.start()

    def listenSocket(self):
        print("server started")
        while(True):
            if(self.terminate):
                break
            ###  Wait for next request from client
            try:
                message = self.socket.recv(zmq.NOBLOCK)
            except zmq.ZMQError:
                time.sleep(0.1)
                continue
            message = message.decode()
            ##check string to see what fmc is commanding
            suc = False
            if("go to" in message):
                suc = self.changeDestination(message)
            elif("land" in message):
                suc = self.comandLand()
            elif("track" in message):
                suc = self.comandTracking()
            

            
            ###  Send reply back to client
            
            pos = self.controler.perceptions.getPos()
            des = self.controler.actions.cur_dest
            if("map" in message):##if the controller receives the map request
                res = "CurrenMap \n"
                res = res + self.controler.mapping_System.getCurrentMinimizedMapString()##add the map string and the map itself 
                #if(len(self.controler.trajectory)>1):  
                #    res = res + (self.controler.trajectory[0])
                suc = True
            else:
                res = "currentState: {}; position -> lat: {}, long: {}, alt: {}, mapPos{},  dest = {},{},{}".format(self.NameStateList[int(self.controler.currentState)], pos[0], pos[1], pos[2],self.controler.mapping_System.GPSToMatrix(pos[0],pos[1]), des.x, des.y, des.z)
                #res = res + ",".join(self.controler.mapping_System.path)
            if("exit" in message):
                self.socket.send(b"comand sent successfully.")
                break                     ##stops the server
            else:
                if(suc):
                    res = res + "; comand sent successfully."
                else:
                    res = res + "; comand failed."
            self.socket.send(str.encode(res))
            
        print("server closed.")

    def changeDestination(self, msg):
        if((self.controler.currentState == self.controler.S_Awaiting) or (self.controler.currentState == self.controler.S_InformFMC) or (self.controler.currentState == self.controler.S_InformAndWaitFMC) or (self.controler.currentState == self.controler.S_Moving)):
            _list = msg.split(" ")
            try:
                dest_lat = float(_list[2]) ## try parsing the 3 coordinates provided
                dest_lng = float(_list[3])
                dest_alt = float(_list[4])
                self.controler.actions.des.x = dest_lat ## if parse was successful, write them as destination on system
                self.controler.actions.des.y = dest_lng
                self.controler.actions.des.z = dest_alt

                ##change state if successful
                if(self.controler.currentState == self.controler.S_Awaiting):
                    self.controler.setState(self.controler.S_takeOff)
                elif(self.controler.currentState == self.controler.S_InformAndWaitFMC):
                    self.controler.trajectoryState = self.controler.T_None
                    self.controler.setState(self.controler.S_RunTrajAlgo)
                else:
                    self.controler.trajectoryState = self.controler.T_None
                    self.controler.setState(self.controler.S_HoldPos)
                return True
            except ValueError:
                return False
        return False

    def comandLand(self):
        if(self.controler.currentState == self.controler.S_InformFMC):
            self.controler.setState(self.controler.S_Landing)
            return True
        return False
    
    def comandTracking(self):
        if(self.controler.currentState == self.controler.S_InformFMC):
            self.controler.setState(self.controler.S_TrackSmoke)
            return True
        return False
        

class FMClient:
    def __init__(self):
        print("starting client FMC")
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5515")

        
        ##start service
        self.clientTask()

    def clientTask(self):
        while(True):
            cmd = raw_input(">>>fmc-command>>> ")

            self.socket.send(str.encode(cmd))

            if("exit" in cmd):
                break
            
            res = self.socket.recv()
            if("CurrenMap" in res):
                print(res)
                print("printed res")
                self.updateCurrentMapInterface(res)
            if("TrajectoryMap" in res):
                print(res)
                #self.updateCurrentMapInterface(res)
            else:
                print(res)
            
        print("client closed")

   

    def updateCurrentMapInterface(self,map):## this function updates the txt file used as an interface to monitor the development of the map
        fileText = open("CurrentMap.txt","w")## clean what has in this file
        fileText.close()

        lines = map
        fileText = open("CurrentMap.txt","a")
        fileText.writelines(lines)
        fileText.close()
        print("updated CurrentMinimizedFile")
       

if __name__ == '__main__':
    FMClient()


    
    
