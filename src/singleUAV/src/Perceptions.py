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
        self.posLock.acquire()
        self.position = msg.pose.pose.position
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