#!/usr/bin/env python2
import rospy
import time
import math
#from pythonAgArch.pythonAgArch import *
import signal
from math import sqrt
from math import ceil

from Actions import Actions
from Perceptions import Perceptions
from Com_FMC import Com_FMC
from Mapping_System import Mapping_System

from threading import RLock

import traceback
import mavros_msgs.srv
import geographic_msgs.msg
import geometry_msgs.msg
import std_msgs.msg
import nav_msgs.msg

############################################ Controler ##########################################################

class Controler:
    
    ##state machine constants
    S_Awaiting = 0
    S_takeOff = 1
    S_HoldPos = 2
    S_RunTrajAlgo = 3
    S_Moving = 4
    S_TrackSmoke = 5
    S_InformFMC = 6
    S_Landing = 7
    S_InformAndWaitFMC = 8
    S_Fatal_Error = 9

    ##trajectory algorithm constants
    T_None = 0
    T_Calculating = 1
    T_Active = 2


    #constructor
    def __init__(self):
        print("initializing")

        ##def main IO classes
        self.actions = Actions(self)         ##routines to publish actions to mavros
        self.perceptions = Perceptions(self) ##listeners to the perceptions coming from mav-ros
        self.comFMC = Com_FMC(self)          ##communication with the Fire Monitoring Center, represented by a human user in this system 
        self.mapping_System = Mapping_System(self) ## Binds class responsible for making the flight plan and updating the map

        ##some important constants
        self.TAKEOFF_ALT_DEF = 5.25 ##default altitude to take off
        

        ##start state machine
        self.stateLock = RLock()
        self.currentState = self.S_Awaiting
        self.stateChanged = True

        self.trajectoryState = self.T_None
        self.trajectory = [[0, 0, 0]]   ##trajectory will always be a finite 3d array of points
        self.trajPointer = -1   ##pointer which shows the current destination in the array above that drone is following
        
        
    #methods
    def start(self):
        # init ROS master and python node
        print("Starting python Agent node on ROS.")
        try:
            rospy.init_node('python_agent', log_level=rospy.INFO)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
        except:
            traceback.print_exc()

        # ros sleeps used in the system
        self.setupRate = rospy.Rate(0.2) ##on setup, it rests for 5 secs
        self.operRate = rospy.Rate(5)  ##on operation 200ms
        self.smRate = rospy.Rate(20) ##during statemachine checks, wait 50 ms

        ##start ros instances on peripheral objects
        self.perceptions.start()
        self.actions.start()
        self.mapping_System.start()

    def isAValidStateChange(self, state):
        if(state == self.S_Awaiting):
            if(self.currentState != self.S_Landing):
                return False
        elif(state == self.S_takeOff):
            if(self.currentState != self.S_Awaiting):
                return False
        elif(state == self.S_HoldPos):
            if((self.currentState != self.S_takeOff) and (self.currentState != self.S_Moving) and (self.currentState != self.S_InformFMC)):
                return False
        elif(state == self.S_RunTrajAlgo):
            if((self.currentState != self.S_HoldPos) and (self.currentState != self.S_InformAndWaitFMC)):
                return False
        elif(state == self.S_Moving):
            if(self.currentState != self.S_RunTrajAlgo):
                return False
        elif(state == self.S_TrackSmoke):
            if(self.currentState != self.S_InformFMC):
                return False
        elif(state == self.S_InformFMC):
            if(self.currentState != self.S_HoldPos):
                return False
        elif(state == self.S_Landing):
            if(self.currentState != self.S_InformFMC):
                return False
        elif(state == self.S_InformAndWaitFMC):
            if((self.currentState != self.S_RunTrajAlgo) and (self.currentState != self.S_TrackSmoke)):
                return False
        return True

    def setState(self, state):
        self.stateLock.acquire()

        #if system is broken, set fatal error and return directly
        if((self.currentState == self.S_Fatal_Error) or (state == self.S_Fatal_Error)):
            self.currentState = self.S_Fatal_Error
        
        #check validity of state change
        elif(self.isAValidStateChange(state)):
            print("changing to {}".format(state))
            #change the state
            self.currentState = state
            self.stateChanged = True
        self.stateLock.release()

    def controlState(self): ###control the actions done in each of the states
        
        start = int(round(time.time() * 1000))   ##get current time in milliseconds --- used for sampling this function
        
        while(True):
            if(self.currentState == self.S_Awaiting): ##wait until comand comes from fmc
                if(self.stateChanged):
                    self.trajectoryState = self.T_None
                    self.stateChanged = False
                        
            elif(self.currentState == self.S_takeOff):
                if(self.stateChanged):
                    self.setupOperation()
                    self.stateChanged = False
                pos = self.perceptions.getPos()
                if(matchPositions((0, 0, self.TAKEOFF_ALT_DEF),(0, 0, self.perceptions.getPos()[2]), 0.5)): 
                    self.setState(self.S_HoldPos)

            elif(self.currentState == self.S_HoldPos):  ##execute only once, then change the state
                if(self.stateChanged):
                    pos = self.perceptions.getPos()
                    self.actions.SetPoint(pos) 
                    self.stateChanged = False
                if(matchPositions(pos, (self.actions.des.x, self.actions.des.y, self.actions.des.z), 0.5)):
                    self.setState(self.S_InformFMC)
                else:
                    self.setState(self.S_RunTrajAlgo)
                    
            elif(self.currentState == self.S_RunTrajAlgo): ##I am treating the algorithm as a parallel task here
                if(self.stateChanged):
                    self.trajectoryState = self.T_Calculating
                    self.stateChanged = False
                    self.getTrajectory()          ##comand which calculates the new trajectory to destination
                if(self.trajectoryState == self.T_None): ##algorithm did not find a valid path
                    self.setState(self.S_InformAndWaitFMC)
                elif(self.trajectoryState == self.T_Active):  ##trajectory is set and drone can move
                    self.setState(self.S_Moving)

            elif(self.currentState == self.S_Moving):
                if(self.stateChanged):                    ##no setup needed
                    self.stateChanged = False
                cur_pos = self.perceptions.getPos()
                if((self.trajectoryState == self.T_None) or matchPositions(cur_pos, [self.actions.des.x, self.actions.des.y, self.actions.des.z], 0.5)): ##slam found an obstacle or destination reached
                    self.setState(self.S_HoldPos)
                else:
                    if(self.trajPointer == -1):
                        self.trajPointer = self.trajPointer + 1
                        self.actions.SetPoint(self.trajectory[0])
                    des = self.trajectory[self.trajPointer]         ##get current destination on trajectory plan
                    if(matchPositions(cur_pos, des, 0.5)):
                        if(self.trajPointer != (len(self.trajectory) - 1)):                      ## set setpoint to next coordinate on trajectory plan
                            self.trajPointer = self.trajPointer + 1
                            self.actions.SetPoint(self.trajectory[self.trajPointer])

            elif(self.currentState == self.S_TrackSmoke):     ##this is a ghost state for now
                if(self.stateChanged):                    ##no setup needed
                    self.stateChanged = False
                self.setState(self.S_InformAndWaitFMC)
                
            elif(self.currentState == self.S_InformFMC):
                if(self.stateChanged):         ##no setup needed
                    self.stateChanged = False
                
            elif(self.currentState == self.S_Landing):
                if(self.stateChanged):           
                    self.actions.Land()
                    self.stateChanged = False
                state = self.perceptions.getState()
                if(not state.armed): ##change to awaiting after drone disarmed the motors
                    self.trajectoryState = self.T_None
                    self.setState(self.S_Awaiting)

            elif(self.currentState == self.S_InformAndWaitFMC):
                if(self.stateChanged):                    ##no setup needed
                    self.stateChanged = False
                
            elapsed_time = int(round(time.time() * 1000)) - start   ##elapsed time in milliseconds #
            if((50 - elapsed_time) > 0):                                                           # sampling at 50ms
                time.sleep((50 - elapsed_time) / 1000) ##convert to seconds for sleep function     #
                            
    def setupOperation(self):
        ##set mode to guided
        while(not self.perceptions.getState().guided):
            self.actions.setMode('GUIDED')
            self.setupRate.sleep()
    
        ##arm motors
        while(not self.perceptions.getState().armed):
            self.actions.ArmMotors(True)
            self.setupRate.sleep()

        self.actions.TakeOff(self.TAKEOFF_ALT_DEF)
    
    def getTrajectory(self):
        traj = self.mapping_System.trajectoryService()
        goal = self.mapping_System.goal
        rospy.loginfo("goal !!!!!!!!!!!!!!!!")
        rospy.loginfo(goal)
        rospy.loginfo("Get trajectory !!!!!!!!!!!!!!!!")
        rospy.loginfo(traj)

        if(not traj): #traj is an empty list, no valid path found
            self.trajectoryState = self.T_None
        else:
            ##everything done
            self.trajectory = traj
            self.trajPointer = -1
            self.trajectoryState = self.T_Active
        return
        

def matchPositions(pos1, pos2, tol):
    res = True
    res = res and (abs(pos1[0] - pos2[0]) < tol)
    res = res and (abs(pos1[1] - pos2[1]) < tol)
    res = res and (abs(pos1[2] - pos2[2]) < tol)
    return res


############################################ main #######################################################

import sensor_msgs.msg

def main():

    #new code for initialization
    print("Starting python node.")
    controler = Controler()
    controler.start()
    controler.controlState() ##start controlling system

    return


    controler.mapping_System.updateCurrentMap(0,0,0,controler.mapping_System.createForsedLidarArray())

    controler.mapping_System.updateCurrentMapInterface()
    print("experimento terminou")
    ##controler.mapping_System.update.updateCurrentMap()
    return

if __name__ == '__main__':
    main()
