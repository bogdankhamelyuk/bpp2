import cv2
import time
import numpy as np
from datetime import datetime
import math
import json
import websocket
import time
from parameters import Parameters
import threading
from threading import Event
import requests


class Gauge(object):
    ####################################################################################
    def __init__(self, e: Event):  # , q: Queue, e: Event):
        cv2.useOptimized()
        self.param = Parameters()
        # variables for storing center coordinates of a circle
        self.x0 = 0  # x-coordinate of the circle's center
        self.y0 = 0  # y-coordinate of the circle's center
        self.r = 0  # radius of the circle
        self.x_arrow = 0
        self.y_arrow = 0
        self.pressure = 0.
        self.mirrorEvent = e
        self.frame = self.img = self.masked_image = self.gray_img = self.frame_copy = None
        self.capture = cv2.VideoCapture(self.param.__class__._camera)

        self.x_1_quadrant_limit = 0
        self.y_1_quadrant_limit = 0
        self.x_2_quadrant_limit = 0
        self.y_2_quadrant_limit = 0
        self.x_3_quadrant_limit = 0
        self.y_3_quadrant_limit = 0
        self.x_4_quadrant_limit = 0
        self.x_4_quadrant_limit = 0
        self.preprocessed_digits = []
        self.circles = []
        # variables for angle measurement in degrees
        self.alpha_deg = 0.  # angle of the arrow at the current time of measure
        self.alpha_zero_pressure = 90-45.44414443  # angle of the arrow at zero pressure
        self.alpha_difference = 0.  # difference between angles
        # constant value of correlation between pressure and degree
        self.bars_pro_degree = 21.22222e-3
        self.name = 'detected circle'

        self.time_now = self.time_past = time.time()
        #self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_status = False
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect("ws://127.0.0.1:8000/graph/upload/")
            self.connection_status = True
        except ConnectionRefusedError:
            print("cannot connect to server")
        video_thread = threading.Thread(target=self.update, args=[])
        video_thread.start()

####################################################################################
    #The following method allows to capture frames from available camera device.
    def update(self):

        while True:
            if self.capture.isOpened():
                ret, self.frame = self.capture.read()
                if ret is not None:
                    #try:
                    #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

                    if self.mirrorEvent.isSet() is True:
                        #print("mirrorEvent is set")
                        self.frame = cv2.flip(self.frame, 1)  # todo with event
                    self.img = self.frame_copy = self.frame
                    #self.img = cv2.flip(self.frame_copy,1)
                    #cv2.flip(self.img,0)
                    final_image = self.start()
                    if final_image is not None:
                        return final_image
                    else:
                        self.start()
                    #except:
                    #    print("caught exception in def update()")
                    #    return self.frame
                else:
                    print("no status ")
                    return None
            else:
                print("couldnt open camera")
                return None
####################################################################################

    def start(self):
        if self.makeBlur() is not False:
            #print("maked blur")
            if self.makeGray() is not False:
                #print("maked gray")
                if self.findCircle() is not False:
                    self.drawCircle()
                    self.cutBackground()
                    if self.CannyEdges() is not False:
                        #print("found canny")
                        if self.drawLine() is not False:
                            self.findQuadrants()
                            self.findAngle()
                            if self.connection_status is True:
                                self.sendData()
                            return self.img
                        else:
                            #print("failed on lines")
                            return self.img
                    else:
                        print("failed on edges")
                        return self.frame
                else:
                    print("no circles")
                    return self.frame
            else:
                print("making gray failed")
                return self.img
        else:
            print("failed on blur")
            return self.img
####################################################################################

    def makeBlur(self):
        try:
            self.img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.blur = cv2.blur(self.img, (5, 5))
            return True
        except Exception:
            #print("caught an exceptpon in make blur")
            return False
####################################################################################

    def makeGray(self):
        try:
            self.gray_img = cv2.cvtColor(self.blur, cv2.COLOR_RGB2GRAY)

            return True

        except Exception:
            #print("caught an exception in make gray")
            return False
#####################################################################################

    def findCircle(self):
        self.circles = cv2.HoughCircles(self.gray_img, cv2.HOUGH_GRADIENT_ALT, dp=1.5, minDist=self.param.__class__._minDist,
                                        param1=self.param.__class__._param1, param2=self.param.__class__._param2,
                                        minRadius=self.param.__class__._minRadius, maxRadius=self.param.__class__._maxRadius)
        try:
            self.circles = np.uint16(np.around(self.circles))
            #print(self.circles)
            self.x0 = self.circles[0, 0, 0]
            self.y0 = self.circles[0, 0, 1]
            self.r = self.circles[0, 0, 2]
            #print("self.x0:",self.x0)
            #print("self.y0",self.y0)
            #print("self.r:",self.r)
            return True
        except:
            #print("couldn't find the circles")
            return False
####################################################################################

    def drawCircle(self):
        self.img = cv2.circle(self.img, (self.x0, self.y0),
                              self.r, (0, 255, 0), 3)
#####################################################################################

    def cutBackground(self):
        self.masked_image = np.zeros(
            self.gray_img.shape[:2], dtype="uint8")  # mem alloc for mask
        x = self.circles[0, 0, 0]
        y = self.circles[0, 0, 1]
        r = self.circles[0, 0, 2]
        # Thickness of -1 px will fill the circle shape by the specified color.
        cv2.circle(self.masked_image, (x, y), r, 255, -1)
        # using logical AND compare mask with image and delete everything outside the mask
        self.masked_image = cv2.bitwise_and(
            self.gray_img, self.gray_img, mask=self.masked_image)
#####################################################################################

    def CannyEdges(self):
        try:
            self.edges = cv2.Canny(
                self.masked_image, self.param.__class__._canny_threshold1, self.param.__class__._canny_threshold2)
            return True
        except:
            print("no edges")
            return False
#####################################################################################

    def drawLine(self):
        lines = cv2.HoughLinesP(self.edges, 1, np.pi/180.0, self.param.__class__._houghlines_threshold,
                                self.param.__class__._minLineLength, self.param.__class__._maxLineGap)
        self.edges = cv2.cvtColor(self.edges, cv2.COLOR_GRAY2RGB)
        if lines is not None:
            #print("found the lines")
            self.x_arrow = lines[0, 0, 0]
            self.y_arrow = lines[0, 0, 1]
            #print("self.x_arrow: ",self.x_arrow)
            #print("self.y_arrow: ",self.y_arrow)

            cv2.line(self.img, (self.x0, self.y0),
                     (self.x_arrow, self.y_arrow), (0, 0, 255), 6)
            self.edges = cv2.circle(
                self.edges, (self.x0, self.y0), self.r, (0, 255, 0), 3)
            cv2.line(self.edges, (self.x0, self.y0),
                     (self.x_arrow, self.y_arrow), (255, 0, 0), 6)

            return True
        else:
            return False
####################################################################################

    def findQuadrants(self):
        self.x_1_quadrant_limit = self.x0
        self.y_1_quadrant_limit = self.y0 - self.r
        #print("###########################################")
        #print("self.x_1_quadrant_limit: ",self.x_1_quadrant_limit)
        #print("self.y_1_quadrant_limit: ",self.y_1_quadrant_limit)
        self.x_2_quadrant_limit = self.x0 - self.r
        self.y_2_quadrant_limit = self.y0 - 4
        #print("###########################################")
        #print("self.x_2_quadrant_limit: ",self.x_2_quadrant_limit)
        #print("self.y_2_quadrant_limit: ",self.y_2_quadrant_limit)
        self.x_3_quadrant_limit = self.x0 + 4
        self.y_3_quadrant_limit = self.y0 + self.r
        #print("###########################################")
        #print("self.x_3_quadrant_limit: ",self.x_3_quadrant_limit)
        #print("self.y_3_quadrant_limit: ",self.x_3_quadrant_limit)
        self.x_4_quadrant_limit = self.x0 + self.r
        self.y_4_quadrant_limit = self.y0 + 4
        #print("###########################################")
        #print("self.x_4_quadrant_limit: ",self.x_4_quadrant_limit)
        #print("self.y_4_quadrant_limit: ",self.y_4_quadrant_limit)
        #print("###########################################")
####################################################################################

    def findAngle(self):
        if self.x_arrow >= self.x_2_quadrant_limit and self.y_arrow <= self.y_2_quadrant_limit and self.x_arrow <= self.x_1_quadrant_limit and self.y_arrow >= self.y_1_quadrant_limit:
            if self.y0 > self.y_arrow:
                self.loesung = 0
                self.alpha_deg = (
                    math.atan((self.x0-self.x_arrow)/(self.y0-self.y_arrow))*180.0/math.pi)
                self.findPressure()
            else:
                self.loesung = 1
                self.alpha_deg = 90
                self.findPressure()
        if self.x_arrow < self.x_3_quadrant_limit and self.y_arrow < self.y_3_quadrant_limit and self.x_arrow > self.x_2_quadrant_limit and self.y_arrow >= self.y_2_quadrant_limit:
            if self.y0 < self.y_arrow:
                self.loesung = 2
                self.alpha_deg = (
                    (math.pi - math.atan((self.x0-self.x_arrow)/(self.y_arrow-self.y0)))*180.0/math.pi)
                self.findPressure()
            else:
                self.alpha_deg = (
                    (math.pi - math.atan((self.x_arrow-self.x0)/(self.y0-self.y_arrow)))*180.0/math.pi)
                self.findPressure()
        if self.x_arrow >= self.x_3_quadrant_limit and self.y_arrow <= self.y_3_quadrant_limit and self.x_arrow <= self.x_4_quadrant_limit and self.y_arrow >= self.y_4_quadrant_limit:
            if (self.x_3_quadrant_limit-self.x_arrow) != 0:
                self.loesung = 3
                if(self.y_4_quadrant_limit-self.y_arrow) != 0:
                    self.loesung = 4
                    self.alpha_deg = (
                        (math.pi + math.atan((self.x_arrow-self.x0)/(self.y0-self.y_arrow)))*180.0/math.pi)
                    self.findPressure()
                else:
                    self.loesung = 5
                    self.alpha_deg = 235.0
                    self.findPressure()
            else:
                self.loesung = 6
                self.alpha_deg = 135.
                self.findPressure()
        if self.x_arrow < self.x_4_quadrant_limit and self.y_arrow < self.y_4_quadrant_limit and self.x_arrow > self.x_1_quadrant_limit and self.y_arrow > self.y_1_quadrant_limit:
            self.loesung = 7
            self.alpha_deg = (
                (2*math.pi - math.atan((self.x_arrow-self.x0)/(self.y_arrow-self.y0)))*180.0/math.pi)
            self.findPressure()
        #after all calculations find the pressure
        #print("self.alpha_deg:",self.alpha_deg)
        self.findPressure()
#####################################################################################

    def findPressure(self):

        # find angular difference relative to angle at zero pressure
        self.alpha_difference = self.alpha_deg - self.alpha_zero_pressure
        #print("self.alpha_difference: ",self.alpha_difference)
        self.param.__class__._angle = self.alpha_difference
        if self.alpha_difference <= 0:  # if difference going to be negative it means automatically that arrrow is at zero pressure
            self.pressure = 0.
            self.now = datetime.now()
            self.current_time = self.now.strftime("%H:%M:%S")
            print("pressure is: ", self.pressure)

        else:
            self.pressure = self.bars_pro_degree * self.alpha_difference
            self.now = datetime.now()
            self.current_time = self.now.strftime("%H:%M:%S")
            self.sendData()
            print("self.alpha_deg:", self.alpha_difference)
            print("self.x0", self.x0)
            print("self.y0", self.y0)
            print("self.x_1_quadrant_limit:", self.x_1_quadrant_limit)
            print("self.y_1_quadrant_limit:", self.y_1_quadrant_limit)
            print("self.x_arrow:", self.x_arrow)
            print("self.y_arrow:", self.y_arrow)
            print("self.x_2_quadrant_limit:", self.x_2_quadrant_limit)
            print("self.y_2_quadrant_limit:", self.y_2_quadrant_limit)
            print("self.x_3_quadrant_limit", self.x_3_quadrant_limit)
            print("self.y_3_quadrant_limit:", self.y_3_quadrant_limit)
            print("self.loesung:", self.loesung)
            print("PRESSURE :::", round(self.pressure, 1), "+- 0.1 bar")
            print("#################################################")
        if self.pressure >= 4.0:
            print("############EXCEPTION!!!!#######################")
            print("self.alpha_deg:", self.alpha_difference)
            print("self.x0", self.x0)
            print("self.y0", self.y0)
            print("self.x_1_quadrant_limit:", self.x_1_quadrant_limit)
            print("self.y_1_quadrant_limit:", self.y_1_quadrant_limit)
            print("self.x_arrow:", self.x_arrow)
            print("self.y_arrow:", self.y_arrow)
            print("self.x_2_quadrant_limit:", self.x_2_quadrant_limit)
            print("self.y_2_quadrant_limit:", self.y_2_quadrant_limit)
            print("self.x_3_quadrant_limit", self.x_3_quadrant_limit)
            print("self.y_3_quadrant_limit:", self.y_3_quadrant_limit)
            print("self.loesung:", self.loesung)
            print("PRESSURE :::", round(self.pressure, 1), "+- 0.1 bar")
            print("#################################################")
            #raise ValueError("error pressure!!")

        # set event to trigger callback for text output in gui_active.py

        return round(self.pressure, 1)
####################################################################################

    def sendData(self):
        #while 1:
        #if self.network_event.isSet():
        a = {'pressure': np.round(self.pressure)}
        b = json.dumps(a).encode('utf-8')
        try:
            self.ws.send(b)
        except:
            print("cannot connect")
            self.connection_status = False
####################################################################################
    #Release the video source when the object is destroyed

    def __del__(self):
        if self.capture.isOpened():
            self.capture.release()
        self.ws.close()
#####################################################################################


if __name__ == '__main__':
   # js = """
   # const WebSocket = require('ws');
   # var socket = new WebSocket('ws://127.0.0.1:8000/graph/upload/');
#
   # """
   # 
   # res = js2py.eval_js(js)
   pass
