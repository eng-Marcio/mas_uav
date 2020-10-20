#!/usr/bin/env python2
import rospy
import time
#from pythonAgArch.pythonAgArch import *
import signal
from math import sqrt
from math import ceil

from Actions import Actions
from Perceptions import Perceptions
from Com_FMC import Com_FMC
from SlamHandler import SlamHandler

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
        self.slamHandler = SlamHandler(self) ##Map handler, slam-sensor topic listener, colision detection
        
        ##setup of the system communication
        

        ##start state machine
        self.stateLock = RLock()
        self.currentState = self.S_Awaiting
        self.stateChanged = True

        self.trajectoryState = self.T_None
        self.trajectory = [[0, 0, 0]]   ##trajectory will always be a finite 3d array of points
        self.trajPointer = -1   ##pointer which shows the current destination in the array above that drone is following
        ##some important attributes
        self.dest_lat = 10
        self.dest_lng = 10
        self.dest_alt = 10

        
        ###connecting to ROS master
        self.state = mavros_msgs.msg.State()
        self.position = geometry_msgs.msg.Point()
        # print("Starting python Agent node on ROS.")
        # try:
        #     rospy.init_node('python_agent', log_level=rospy.INFO)
        #     signal.signal(signal.SIGINT, signal.SIG_DFL)
        # except:
        #     traceback.print_exc()

        # ##start actions and perceptions
        # self.actions.set_mode()



    #methods
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
                    self.actions.takeOff()
                    self.stateChanged = False
                pos = self.perceptions.getPos()
                if(matchPositions(pos, (pos[0], pos[1], 5), 0.1)):   ##only check altitude, it should be bigger than 5
                    self.setState(self.S_HoldPos)

            elif(self.currentState == self.S_HoldPos):  ##execute only once, then change the state
                if(self.stateChanged):
                    pos = self.perceptions.getPos()
                    self.actions.setPoint(pos[0], pos[1], pos[2]) 
                    self.stateChanged = False
                if(matchPositions(pos, (self.dest_lat, self.dest_lng, self.dest_alt), 0.01)):
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
                if((self.trajectoryState == self.T_None) or matchPositions(cur_pos, (self.dest_lat, self.dest_lng, self.dest_alt), 0.001)): ##slam found an obstacle or destination reached
                    self.setState(self.S_HoldPos)
                else:
                    if(self.trajPointer == -1):
                        self.trajPointer = self.trajPointer + 1
                        self.actions.setPoint(self.trajectory[0][0], self.trajectory[0][1], self.trajectory[0][2])
                    des = self.trajectory[self.trajPointer]         ##get current destination on trajectory plan
                    if(matchPositions(cur_pos, (des[0], des[1], des[2]), 0.15)):
                        if(self.trajPointer != (len(self.trajectory) - 1)):                      ## set setpoint to next coordinate on trajectory plan
                            self.trajPointer = self.trajPointer + 1
                            self.actions.setPoint(self.trajectory[self.trajPointer][0], self.trajectory[self.trajPointer][1], self.trajectory[self.trajPointer][2])

            elif(self.currentState == self.S_TrackSmoke):                  ##this is a ghost state for now
                if(self.stateChanged):                    ##no setup needed
                    self.stateChanged = False
                self.setState(self.S_InformAndWaitFMC)
                
            elif(self.currentState == self.S_InformFMC):
                if(self.stateChanged):         ##no setup needed
                    self.stateChanged = False
                
            elif(self.currentState == self.S_Landing):
                if(self.stateChanged):           
                    self.actions.RTL()
                    self.stateChanged = False
                cur_pos = self.perceptions.getPos()
                if(matchPositions(cur_pos, (cur_pos[0], cur_pos[1], 0), 0.1)): ##only care if drone is on the ground (altitude zero)
                    self.trajectoryState = self.T_None
                    self.setState(self.S_Awaiting)

            elif(self.currentState == self.S_InformAndWaitFMC):
                if(self.stateChanged):                    ##no setup needed
                    self.stateChanged = False
                
            elapsed_time = int(round(time.time() * 1000)) - start   ##elapsed time in milliseconds
            if((50 - elapsed_time) > 0):                                                        # sampling at 50ms
                time.sleep((50 - elapsed_time) / 1000) ##convert to seconds for sleep function  #
                            
    def pos_call_back(self, msg):
        self.position = msg.pose.pose.position
        
    def state_callback(self, msg):
        self.state = msg

    def getTrajectory(self):
        ##for testing reasons we will calculate an interpolated number of points on an straight line to the destination
        pos = self.perceptions.getPos()
        dest = (self.dest_lat, self.dest_lng, self.dest_alt)
        
        #calculate vector pointing to destination with size 1
        vector = (dest[0] - pos[0], dest[1] - pos[1], dest[2] - pos[2])
        size_raw = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        if(size_raw > 10000): ##distance to destination is absurd, some error has happened
            print("invalid destination provided")
            self.trajectoryState = self.T_None
            return
        vector = (vector[0] / size_raw, vector[1] / size_raw, vector[2] / size_raw)  ##normalize vector
        self.trajectory = []
        ##set coordinate values for the trajectory
        for i in range(int(size_raw)):
            x = []
            x.append(pos[0] + (i + 1) * vector[0])
            x.append(pos[1] + (i + 1) * vector[1])
            x.append(pos[2] + (i + 1) * vector[2])
            self.trajectory.append(x)
        self.trajectory.append(dest) ##last coordinate is the destination itself
        
        ##everything done
        self.trajPointer = -1
        self.trajectoryState = self.T_Active


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
    #teste1

    ###comandos concentrados para iniciar o ros e os topicos necessarios
    print("Starting python Agent node on ROS.")
    try:
        rospy.init_node('python_agent', log_level=rospy.INFO)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
            
        state_sub = rospy.Subscriber('/mavros/state', mavros_msgs.msg.State, controler.state_callback)
        pos_sub = rospy.Subscriber('mavros/global_position/local', nav_msgs.msg.Odometry, controler.pos_call_back)

        rate = rospy.Rate(5)
        
        rospy.wait_for_service('mavros/set_mode')
        set_mode = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
        set_mode(custom_mode='GUIDED')
        while(not controler.state.guided):
            rate.sleep()

        rospy.wait_for_service('mavros/cmd/arming')
        arm_motors = rospy.ServiceProxy('mavros/cmd/arming', mavros_msgs.srv.CommandBool)
        
        while(not controler.state.armed):
            arm_motors(True)
            rate.sleep()

        rospy.wait_for_service('mavros/cmd/takeoff')
        take_off = rospy.ServiceProxy('mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL)
        take_off(altitude=7.0)  
        
        while(not matchPositions((0, 0, 7),(0, 0, controler.position.z), 0.5)):
            rate.sleep()
         
        setPoint_pub = rospy.Publisher('mavros/setpoint_position/local', geometry_msgs.msg.PoseStamped, queue_size=1, latch=True)
        header = std_msgs.msg.Header()
        header.stamp = rospy.Time.now()
        pos = geometry_msgs.msg.Point(0, 50, 10)
        pose = geometry_msgs.msg.Pose(position=pos)
        setPoint_pub.publish(pose=pose, header=header)

        while(not matchPositions((0,50,10),(controler.position.x, controler.position.y, controler.position.z), 1.0)):
            rate.sleep()

        ##send new position
        header = std_msgs.msg.Header()
        header.stamp = rospy.Time.now()
        pos = geometry_msgs.msg.Point(0, 0, 3)
        pose = geometry_msgs.msg.Pose(position=pos)
        setPoint_pub.publish(pose=pose, header=header)

        while(not matchPositions((0,0,3),(controler.position.x, controler.position.y, controler.position.z), 0.5)):
            rate.sleep()

        land = rospy.ServiceProxy('mavros/cmd/land', mavros_msgs.srv.CommandTOL)
        rospy.wait_for_service('mavros/cmd/land')
        land()

        print("project changed")

    except:
        print("Service failed")
        traceback.print_exc()

        
# [global_pos]
# name = mavros/global_position/global
# msg_type = NavSatFix
# dependencies = sensor_msgs.msg
# args = latitude, longitude
# buf = update[global_pos]



    ##start process
    ###controler.controlState()

    ##when exiting
    #print("exiting server")
    #controler.comFMC.terminate = True

    ##old code for initialization
    # print("Starting python Agent node.")
    # rospy.init_node('python_agent', log_level=rospy.INFO)
    # signal.signal(signal.SIGINT, signal.SIG_DFL)

    # my_name = 'uav'
    # agArch = AgArch(my_name)

    # waitOnline(agArch)
    # setModeGuided(agArch)
    # armMotor(agArch)

    # takeOff(agArch, 5)
    # goToPos(agArch, -27.603683, -48.518052, 40)
    # rtl(agArch)

if __name__ == '__main__':
    main()
