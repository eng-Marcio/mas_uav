#!/usr/bin/env python2
class SlamHandler:
    ##constructor
    def __init__(self, controler):                               ######this class has the map model and the routines which deal with the SLAM sensor
        
        ##maintain pointer to controler
        self.controler = controler

        self.map = list()

    ##methods
    def getMap(self):
        return self.map