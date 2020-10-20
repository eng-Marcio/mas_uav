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
            if("status" in message):
                pos = self.controler.global_pos
                res = "currentState: {}; position -> lat: {}, long: {}, alt: {}".format(self.controler.currentState, pos.altitude, pos.longitude, pos.altitude)
                self.socket.send(str.encode(res))
            elif("exit" in message):
                self.socket.send(b"comand sent successfully.")
                break                     ##stops the server
            else:
                if(suc):
                    self.socket.send(b"comand sent successfully.")
                else:
                    self.socket.send(b"comand failed.")
            
        print("server closed.")

    def changeDestination(self, msg):
        if((self.controler.currentState == self.controler.S_Awaiting) or (self.controler.currentState == self.controler.S_InformFMC) or (self.controler.currentState == self.controler.S_InformAndWaitFMC) or (self.controler.currentState == self.controler.S_Moving)):
            _list = msg.split(" ")
            try:
                dest_lat = float(_list[2]) ## try parsing the 3 coordinates provided
                dest_lng = float(_list[3])
                dest_alt = float(_list[4])
                self.controler.dest_lat = dest_lat  ## if parse was successful, write them as destination on system
                self.controler.dest_lng = dest_lng
                self.controler.dest_alt = dest_alt

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
            cmd = input(">>>fmc-command>>> ")

            self.socket.send(str.encode(cmd))

            if("exit" in cmd):
                break
            
            res = self.socket.recv()

            print(res)
            
        print("client closed")

if __name__ == '__main__':
    FMClient()


    
    
