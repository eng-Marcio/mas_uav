#!/usr/bin/env python2

import rospy
import mavros_msgs.srv
import geometry_msgs.msg
import std_msgs.msg
import math


class Actions:

    ##constructor
    def __init__(self, controler):
        
        ##maintain pointer to controler
        self.controler = controler
        self.des = geometry_msgs.msg.Point() ##setpoint final destination
        self.cur_dest = geometry_msgs.msg.Point() ##current position on setpoint



    ##methods: services
    ##small change
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
        self.cur_dest = pos
        quat = geometry_msgs.msg.Quaternion()
        if(len(des) > 3): ##angle given
            quat_from_eu = self.euler_to_quaternion(0, 0, des[3]*math.pi/180)
            quat.x = quat_from_eu[0]
            quat.y = quat_from_eu[1]
            quat.z = quat_from_eu[2]
            quat.w = quat_from_eu[3]
        pose = geometry_msgs.msg.Pose(position=pos, orientation=quat)
        header = std_msgs.msg.Header()
        header.stamp = rospy.Time.now()
        self.setPoint_pub.publish(pose=pose, header=header)

    def euler_to_quaternion(self, roll, pitch, yaw):

        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)

        return [qx, qy, qz, qw]

