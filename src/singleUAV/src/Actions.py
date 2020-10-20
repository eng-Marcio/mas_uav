#!/usr/bin/env python2

import rospy
import mavros_msgs.srv
import geometry_msgs.msg
import std_msgs.msg

class Actions:

    ##attributes


    ##constructor
    def __init__(self, controler):
        
        ##maintain pointer to controler
        self.controler = controler



    ##methods: services
    def start(self):
        ##setting up action topics to publish
        self.setPoint_pub = rospy.Publisher('mavros/setpoint_position/local', geometry_msgs.msg.PoseStamped, queue_size=1, latch=True)

    def setMode(self, mode):
        rospy.wait_for_service('mavros/set_mode')
        set_mode = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
        try:
            set_mode(custom_mode=mode)
        except:
            pass

    def ArmMotors(self, arm):
        rospy.wait_for_service('mavros/cmd/arming')
        arm_motors = rospy.ServiceProxy('mavros/cmd/arming', mavros_msgs.srv.CommandBool)
        try:
            arm_motors(arm)
        except:
            pass

    def TakeOff(self, alt):    
        rospy.wait_for_service('mavros/cmd/takeoff')
        take_off = rospy.ServiceProxy('mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL)
        take_off(altitude=alt)

    def Land(self):
        rospy.wait_for_service('mavros/cmd/land')
        land = rospy.ServiceProxy('mavros/cmd/land', mavros_msgs.srv.CommandTOL)
        rospy.wait_for_service('mavros/cmd/land')
        land()

    
    #methods topics
    def SetPoint(self, des):
        pos = geometry_msgs.msg.Point(des[0], des[1], des[2]) ##set a linear destination as a 3d point in space
        pose = geometry_msgs.msg.Pose(position=pos)
        header = std_msgs.msg.Header()
        header.stamp = rospy.Time.now()
        self.setPoint_pub.publish(pose=pose, header=header)

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
