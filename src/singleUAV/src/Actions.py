#!/usr/bin/env python2

import rospy
import mavros_msgs.srv

class Actions:

    ##attributes


    ##constructor
    def __init__(self, controler):
        
        ##maintain pointer to controler
        self.controler = controler

        ### set callable methods for action
        self.configureIOs()



    ##methods
    def configureIOs(self):  ##set up topics and services
        print("configuring")
        self.ROS_set_mode = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)

        


    def set_mode(self):
        rospy.wait_for_service('mavros/set_mode')
        self.ROS_set_mode(mavros_msgs.srv.SetMode, "GUIDED")

    def setPoint(self, lat, lng, alt):
        print("going to %d , %d, %d", lat, lng, alt)
    
    def takeOff(self):
        print("taking off")

    def RTL(self):
        print("landing")

# [set_mode]
# method = service
# name = mavros/set_mode
# msg_type = SetMode
# dependencies = mavros_msgs.srv
# params_name = custom_mode

# [arm_motors]
# method = service
# name = mavros/cmd/arming
# msg_type = CommandBool
# dependencies = mavros_msgs.srv
# params_name = value
# params_type = bool

# [takeoff]
# method = service
# name = mavros/cmd/takeoff
# msg_type = CommandTOL
# dependencies = mavros_msgs.srv
# params_name = altitude
# params_type = float

# [setpoint]
# method = topic
# name = mavros/setpoint_position/global
# msg_type = GeoPoseStamped
# dependencies = geographic_msgs.msg
# params_name = pose.position.latitude, pose.position.longitude, pose.position.altitude
# params_type = float, float, float

# [land]
# method = service
# name = mavros/cmd/land
# msg_type = CommandTOL
# dependencies = mavros_msgs.srv
