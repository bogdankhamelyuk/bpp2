from tkinter import Event
import cv2, time
import numpy as np
import threading
import tkinter 
from datetime import datetime
import math
import socket
import json 
import time 
from queue import Queue
<<<<<<< HEAD
import continuous_threading

=======
>>>>>>> 6b70c6a1486e6536d055ce6c7903be508430d82a

class Gauge(object): 

    # variables for storing center coordinates of a circle
    x0 = 0 # x-coordinate of the circle's center
    y0 = 0 # y-coordinate of the circle's center
    r  = 0 # radius of the circle 
    x_arrow = 0
    y_arrow = 0
    
    x_1_quadrant_limit = 0
    y_1_quadrant_limit = 0
    
    x_2_quadrant_limit = 0
    y_2_quadrant_limit = 0 
    
    x_3_quadrant_limit = 0
    y_3_quadrant_limit = 0
    
    x_4_quadrant_limit = 0
    x_4_quadrant_limit = 0
    preprocessed_digits = []
    circles = []
    # variables for angle measurement in degrees
    alpha_deg = 0. # angle of the arrow at the current time of measure
    alpha_zero_pressure =  90-45.44414443 # angle of the arrow at zero pressure
    alpha_difference = 0. # difference between angles
    # constant value of correlation between pressure and degree 
    bars_pro_degree = 21.22222e-3
    name = 'detected circle'
####################################################################################
    def __init__(self, event:Event):#, q: Queue, e: Event):
        #!!!these values are going to be controlled from slice bar !!!
        self.canny_threshold1 = 350 
        self.canny_threshold2 = 175
        
        #!!!these values must be controlled from slice bar
        self.minLineLength = 30
        self.maxLineGap = 18
        self.houghlines_threshold = 25
        
        self.pressure = 0.
        self.frame = self.img = self.masked_image = self.gray_img = None
        self.camera = 0 
        self.capture = cv2.VideoCapture(self.camera)
        self.event = event
        
        self.video_thread = threading.Thread(target=self.update, args=())#q,e,))
        self.video_thread.name='video thread'
        self.video_thread.daemon = True
        self.video_thread.start()
        
        self.time_now = self.time_past = time.time()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try: 
            self.s.connect((socket.gethostname(),10240))
            print("connected!")
        except ConnectionRefusedError:
            print("cannot connect to server")
        
####################################################################################    
    #The following method allows to capture frames from available camera device.
    def update(self):
        while True:
            if self.capture.isOpened():
                ret, self.frame = self.capture.read()
                if ret:
                    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    self.frame_copy = self.frame
                    self.img = self.frame 
                    return True
                else:
                    return False
            else:
                return False
              
####################################################################################
    def start(self):
        self.makeBlur()   
####################################################################################
    def makeBlur(self):
        try:
            self.blur = cv2.blur(self.img,(3,3))
            self.makeGray() # in case of succeeded blurring call makeGray method
        except Exception:
            print("caught an exceptpon in make blur")
            self.start()
####################################################################################
    def makeGray(self):
        try:
            self.gray_img = cv2.cvtColor(self.blur,cv2.COLOR_RGB2GRAY)
            self.findCircle() 
        except Exception:
            print("caught an exception in make gray")
            pass
#####################################################################################            
    def findCircle(self):
        circles = cv2.HoughCircles(self.gray_img,cv2.HOUGH_GRADIENT_ALT,dp=1.5,minDist=5,param1=300,param2=0.9,minRadius=0, maxRadius=1200)
        if circles is not False:
            self.circles = np.uint16(np.around(self.circles))
            self.x0 = self.circles[0,0,0] 
            self.y0 = self.circles[0,0,1]  
            self.r  = self.circles[0,0,2]
            
            self.drawCircle() 
        else:
            print("couldn't find the circles")
            self.start()
####################################################################################
    def drawCircle(self):
        self.img = cv2.circle(self.img,(self.x0,self.y0),self.r,(0,255,0),3)
        self.cutBackground()
#####################################################################################    
    def cutBackground(self):
        self.masked_image = np.zeros(self.gray_img.shape[:2], dtype="uint8")#mem alloc for mask
        x = self.circles[0,0,0]
        y = self.circles[0,0,1]
        r = self.circles[0,0,2]
        cv2.circle(self.masked_image , (x,y),r,255,-1) # Thickness of -1 px will fill the circle shape by the specified color.
        self.masked_image = cv2.bitwise_and(self.gray_img, self.gray_img, mask=self.masked_image) # using logical AND compare mask with image and delete everything outside the mask
        self.CannyEdges()
#####################################################################################        
    def CannyEdges(self):
        self.edges = cv2.Canny(self.masked_image,self.canny_threshold1,self.canny_threshold2)
        self.drawLine()
#####################################################################################        
    def drawLine(self):
        lines = cv2.HoughLinesP(self.edges,1, np.pi/180.0, self.houghlines_threshold, self.minLineLength, self.maxLineGap)
        if lines is not None:
            #print("found the lines")
            self.x_arrow = lines[0,0,0] # 
            self.y_arrow = lines[0,0,1]
            cv2.line(self.img,(self.x0,self.y0), (self.x_arrow,self.y_arrow), (0,0,255),2)
            self.findQuadrants()
        else:
            self.start()
####################################################################################                        
    def findQuadrants(self):
        self.x_1_quadrant_limit = self.x0  
        self.y_1_quadrant_limit = self.y0 + self.r 
        
        self.x_2_quadrant_limit = self.x0 - self.r 
        self.y_2_quadrant_limit = self.y0 - 6 

        self.x_3_quadrant_limit = self.x0 + 6 
        self.y_3_quadrant_limit = self.y0 - self.r 

        self.x_4_quadrant_limit = self.x0 + self.r 
        self.y_4_quadrant_limit = self.y0 + 6 
        self.findAngle()
####################################################################################             
    def findAngle(self): 
        if self.x_arrow >= self.x_2_quadrant_limit and self.y_arrow >= self.y_2_quadrant_limit and self.x_arrow <= self.x_1_quadrant_limit and self.y_arrow <= self.y_1_quadrant_limit:
            if self.y0 > self.y_arrow : 
                self.alpha_deg = (math.atan((self.x0-self.x_arrow)/(self.y0-self.y_arrow))*180.0/math.pi)
            else:
                self.alpha_deg = (math.atan((self.x0-self.x_arrow)/(self.y_arrow-self.y0))*180.0/math.pi)
        if self.x_arrow < self.x_3_quadrant_limit and self.y_arrow > self.y_3_quadrant_limit and self.x_arrow > self.x_2_quadrant_limit and self.y_arrow < self.y_2_quadrant_limit:
            if self.x0 > self.x_arrow:
                self.alpha_deg = ((math.pi - math.atan((self.x0-self.x_arrow)/(self.y0-self.y_arrow)))*180.0/math.pi)
            else:
                self.alpha_deg = ((math.pi - math.atan((self.x_arrow-self.x0)/(self.y0-self.y_arrow)))*180.0/math.pi)
        if self.x_arrow >= self.x_3_quadrant_limit and self.y_arrow >= self.y_3_quadrant_limit and self.x_arrow <= self.x_4_quadrant_limit and self.y_arrow <= self.y_4_quadrant_limit:
            if (self.x_3_quadrant_limit-self.x_arrow) != 0 :
                if(self.y_4_quadrant_limit-self.y_arrow)!=0:  
                    self.alpha_deg = ((math.pi + math.atan((self.x_arrow-self.x0)/(self.y0-self.y_arrow)))*180.0/math.pi)
                else:
                    self.alpha_deg = 235.0
            else:
                self.alpha_deg = 135.
        if self.x_arrow < self.x_4_quadrant_limit and self.y_arrow > self.y_4_quadrant_limit and self.x_arrow > self.x_1_quadrant_limit and self.y_arrow < self.y_1_quadrant_limit:
            self.alpha_deg = ((2*math.pi - math.atan((self.x_arrow-self.x0)/(self.y_arrow-self.y0)))*180.0/math.pi)
        #after all calculations find the pressure
        self.findPressure()
#####################################################################################
    def findPressure(self):
        self.alpha_difference = self.alpha_deg - self.alpha_zero_pressure # find angular difference relative to angle at zero pressure 
        if self.alpha_difference <= 0 : # if difference going to be negative it means automatically that arrrow is at zero pressure
            self.pressure = 0.
            self.now = datetime.now()
            self.current_time = self.now.strftime("%H:%M:%S")
        else:
            self.pressure = self.bars_pro_degree * self.alpha_difference
            self.now = datetime.now()
            self.current_time = self.now.strftime("%H:%M:%S")
            self.sendData()
            print("pressure:",round(self.pressure,1),"+- 0.1 bar")
        # set event to trigger callback for text output in gui_active.py    
        
        return round(self.pressure,1)
####################################################################################
    def sendData(self):
        #while 1:
            #if self.network_event.isSet():
        a = {'Pressure':self.pressure, 'Time':self.current_time}
        b = json.dumps(a).encode('utf-8')
        try:
            self.s.send(b)
        except BrokenPipeError:
            pass
####################################################################################
    #Release the video source when the object is destroyed
    def __del__(self):
        if self.capture.isOpened():
            continuous_threading.shutdown(0)
            self.capture.release() 
#####################################################################################        
