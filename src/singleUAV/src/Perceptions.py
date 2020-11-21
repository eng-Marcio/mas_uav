#!/usr/bin/env python2

from threading import RLock
import math

import rospy

import std_msgs.msg
import mavros_msgs.msg
import nav_msgs.msg
import geometry_msgs.msg

class Perceptions:
    #constructor
    def __init__(self, controler):
        
        ##maintain pointer to controler
        self.controler = controler

        ## important attributes
        self.state = mavros_msgs.msg.State()
        self.position = geometry_msgs.msg.Point()
        self.orientation = [0, 0, 0] ##roll pitch yaw
        self.destination = geometry_msgs.msg.Point()
        self.fcuSpeed = 0   ##remember to use a topic which returns approximatelly the speed        
        
        #create lock to protect integrity of info
        self.posLock = RLock()
        self.stateLock = RLock()
        self.velLock = RLock()
        

    #methods for main to get information
    def getState(self):
        self.stateLock.acquire()
        state = self.state
        self.stateLock.release()
        return state

    def getPos(self):
        self.posLock.acquire()
        pos = self.position
        self.posLock.release()
        return (pos.x, pos.y, pos.z)
    
    def getOrientation(self):
        self.posLock.acquire()
        pos = self.orientation
        self.posLock.release()
        return pos

    def getSpeed(self):
        self.velLock.acquire()
        speed = self.fcuSpeed
        self.velLock.release()
        return speed

    #ros callbacks
    def start(self):
        ##starting ros topics
        rospy.Subscriber('mavros/state', mavros_msgs.msg.State, self.state_callback)
        rospy.Subscriber('mavros/global_position/local', nav_msgs.msg.Odometry, self.pos_callback)
        rospy.Subscriber('mavros/global_position/gp_vel', geometry_msgs.msg.TwistStamped, self.speed_callback)

    def pos_callback(self, msg):
        param = msg.pose.pose
        quat = param.orientation
        new_angles = self.quaternion_to_euler(quat.x, quat.y, quat.z, quat.w)
        self.posLock.acquire()
        self.position = param.position
        self.orientation = new_angles
        self.posLock.release()
        
    def state_callback(self, msg):
        self.stateLock.acquire()
        self.state = msg
        self.stateLock.release()
    
    def speed_callback(self, msg):
        vec_vel = msg.twist.linear
        #vectorial sum of speeds to determine absolut linear speed
        lin_vel = math.sqrt(vec_vel.x**2 + vec_vel.y**2 + vec_vel.z**2)
        self.velLock.acquire()
        self.fcuSpeed = lin_vel
        self.velLock.release()


    def quaternion_to_euler(self, x, y, z, w):

        import math
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll = math.degrees(math.atan2(t0, t1))

        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch = math.degrees(math.asin(t2))

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw = math.degrees(math.atan2(t3, t4))

        return [roll, pitch, yaw]
