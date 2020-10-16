#!/usr/bin/env python2
from threading import RLock

class Perceptions:
    #constructor
    def __init__(self, controler):
        
        ##maintain pointer to controler
        self.controler = controler

        #def global position to keep in memory
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0

        self.apparentSpeed = 0   ##remember to use a topic which returns approximatelly the speed

        #setup topics to listen the sensors of the simulation
        self.defaultRate = 30  ##rate is used by ROS for sampling
        
        
        #create lock to protect integrity of position info
        self.positionLock = RLock()
        

    #methods
    def getPos(self):
        self.positionLock.acquire()
        lat = self.latitude
        lon = self.longitude
        alt = self.altitude
        self.positionLock.release()
        return (lat, lon, alt)

    def getApparentSpeed(self):
        self.positionLock.acquire()
        speed = self.apparentSpeed
        self.positionLock.release()
        return speed

# [state]
# name = mavros/state
# msg_type = State
# dependencies = mavros_msgs.msg
# args = mode, connected, armed
# buf = update

# [altitude]
# name = mavros/global_position/rel_alt
# msg_type = Float64
# dependencies = std_msgs.msg
# args = data
# buf = update

# [global_pos]
# name = mavros/global_position/global
# msg_type = NavSatFix
# dependencies = sensor_msgs.msg
# args = latitude, longitude
# buf = update

# [home_pos]
# name = mavros/home_position/home
# msg_type = HomePosition
# dependencies = mavros_msgs.msg
# args = geo.latitude, geo.longitude
# buf = update