from tkinter import Event
import cv2, time
import numpy as np
import threading
import tkinter 
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import math
import socket
import json 
import time 
from queue import Queue
import continuous_threading

matplotlib.use("TkAgg")

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
    # variable for pressure
    
    #masked_image = gray_img = img = cv2.imread('/home/bogdan/Vs-code-workspace/python/opencv/image read/screen.png')

    def __init__(self, e:Event):#, q: Queue, e: Event):
        #######################################################################
        #!!!these values are going to be controlled from slice bar in tkinter!!!
        self.canny_threshold1 = 350 
        self.canny_threshold2 = 175
        #######################################################################
        #!!!these values must be controlled from slice bar
        self.minLineLength = 30
        self.maxLineGap = 18
        self.houghlines_threshold = 25
        #######################################################################
        self.cannyWidgetTop = False
        self.lol = 300
        self.pressure = 0.
        self.i=0
        self.img = self.masked_image = self.gray_img = None
        self.camera = 0 
        self.capture = cv2.VideoCapture(self.camera)
        self.event = e 
        #print("event status:",self.event.isSet())
        self.video_thread = threading.Thread(target=self.update, args=())#q,e,))
        self.video_thread.name='video thread'
        self.video_thread.daemon = True
        self.video_thread.start()

        self.time_now = self.time_past = time.time()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #!!!!SOCKETS ARE SLOWING DOWN THE WHOLE APP!!!!!
        try: 
            self.s.connect((socket.gethostname(),10240))
            print("connected!")
        except ConnectionRefusedError:
            print("cannot connect to server")
        
    # Stores captures in a queue for someone to consume

    def sendData(self):
        #while 1:
            #if self.network_event.isSet():
        a = {'Pressure':self.pressure, 'Time':self.current_time}
        b = json.dumps(a).encode('utf-8')
        try:
            self.s.send(b)
        except BrokenPipeError:
            pass


    def snapshot(self):
        self.img = self.capture.read()[1]
        #cv2.imshow("snapshot orig",self.img)
        self.runAll()
    # Stores captures in a queue for someone to consume
    def update(self):#, q,e): 
        while True:
            if self.capture.isOpened():
                ret, frame = self.capture.read()
              #frame = cv2.resize(frame,(200,200))
                if ret:
                    # Return a boolean success flag and the current frame converted to BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_copy = frame
                    self.img = frame 
                    final_img=self.runAll() 
                    return (ret, frame_copy,final_img)
                else:
                    return (ret, None,None)
            else:
                return (None, None,None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.capture.isOpened():
            continuous_threading.shutdown(0)
            self.capture.release()
        #        q.put(self.capture.read())                     
    

    def show_frame(self):
        cv2.imshow('frame', self.frame)
        key = cv2.waitKey(1)
        self.time_now = time.time()
        if self.time_now - self.time_past >=1 :
           # print("{} sec are past".format(self.time_now - self.time_past))
            
            self.time_past = self.time_now
            #self.threads[self.i]=Thread(target=self.snapshot,args=())
            #self.threads[self.i].start()
            self.snapshot()
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)    
    def drawPlot(self):
        print("====================================")
        # x axis will have pressure values
        x_axis = [0.4, 0.8, 1, 1.4, 2, 3, 3.6, 4, 4.6, 5, 5.4, 6]
        x_axisNew = []
        x_axisNew2 = []
        x_axisNewFloat = np.array(x_axisNew,dtype=np.float32)
        x_axisNewFloat2 = np.array(x_axisNew2,dtype=np.float32)
        y_axis = []
        angles = []
        sigma  = []
        sigma2 = []
        angle = 0.
        anglesFloat = np.array(angles,dtype=np.float32)
        y_axisFloat = np.array(y_axis,dtype=np.float32)
        sigmaFloat  = np.array(sigma, dtype=np.float32)
        sigmaFloat2  = np.array(sigma2, dtype=np.float32)
        coefficient = 0.

        bar04 = [248,463]
        bar08 = [240,436]
        bar1  = [208,420]
        bar14 = [244,395]
        bar2  = [269,364]
        bar3  = [333,307]
        bar36 = [369,351]
        bar4  = [388,370]
        bar46 = [408,403]
        bar5  = [446,432]
        bar54 = [405,455]
        bar6  = [383,493]

        pointsList = [bar04,bar08,bar1,bar14,bar2,bar3,bar36, bar4, bar46, bar5, bar54, bar6]

        for x,y in pointsList[0:]: #ToDo: Copy this logic to the findAngle method!!!!
            if x >= self.x_2_quadrant_limit and y >= self.y_2_quadrant_limit and x <= self.x_1_quadrant_limit and y <= self.y_1_quadrant_limit:
                if self.y0 > y : 
                    angle = (math.atan((self.x0-x)/(self.y0-y))*180.0/math.pi) - self.alpha_zero_pressure
                    anglesFloat = np.append(anglesFloat,angle)
                else:
                    angle = (math.atan((self.x0-x)/(y-self.y0))*180.0/math.pi) - self.alpha_zero_pressure
                    anglesFloat = np.append(anglesFloat,angle)
                #print("{d}. angle is: {a}".format(d=(len(anglesFloat)-1),a=angle))
        
            if x < self.x_3_quadrant_limit and y > self.y_3_quadrant_limit and x > self.x_2_quadrant_limit and y < self.y_2_quadrant_limit:
                if self.x0 > x:
                    angle = ((math.pi - math.atan((self.x0-x)/(self.y0-y)))*180.0/math.pi) - self.alpha_zero_pressure
                    anglesFloat = np.append(anglesFloat,angle)
                else:
                    angle = ((math.pi - math.atan((x-self.x0)/(self.y0-y)))*180.0/math.pi) - self.alpha_zero_pressure
                    anglesFloat = np.append(anglesFloat,angle)     
                #print("{d}. angle is: {a}".format(d=(len(anglesFloat)-1),a=angle))
            
            if x >= self.x_3_quadrant_limit and y >= self.y_3_quadrant_limit and x <= self.x_4_quadrant_limit and y <= self.y_4_quadrant_limit:
                if(self.x_3_quadrant_limit-x) != 0 :
                    if(self.y_4_quadrant_limit-y)!=0:  
                        angle = ((math.pi + math.atan((x-self.x0)/(self.y0-y)))*180.0/math.pi) - self.alpha_zero_pressure
                    else:
                        angle = 235. 
                else:
                    angle = 135.
                    
                anglesFloat = np.append(anglesFloat,angle)
                #print("{d}. angle is: {a}".format(d=(len(anglesFloat)-1),a=angle))
            
            if x < self.x_4_quadrant_limit and y > self.y_4_quadrant_limit and x > self.x_1_quadrant_limit and y < self.y_1_quadrant_limit:
                angle = ((2*math.pi - math.atan((x-self.x0)/(y-self.y0)))*180.0/math.pi)
                anglesFloat = np.append(anglesFloat,angle)
                #print("{d}. angle is: {a}".format(d=(len(anglesFloat)-1),a=angle))

        j=0
        while j < 12:
            y_axisFloat = np.append(y_axisFloat,x_axis[j]/anglesFloat[j])
            j+=1

        print("====================================")
        for coefficient in range(len(y_axisFloat)):
            #print("{a}) {b} bars/degree".format(a=coefficient,b=y_axisFloat[coefficient]))
            sigmaFloat = np.append(sigmaFloat,((y_axisFloat[coefficient] * anglesFloat[4]  - 2),
                                               (y_axisFloat[coefficient] * anglesFloat[7]  - 4),
                                               (y_axisFloat[coefficient] * anglesFloat[11] - 6)))
            x_axisNewFloat = np.append(x_axisNewFloat,y_axisFloat[coefficient])
            x_axisNewFloat = np.append(x_axisNewFloat,y_axisFloat[coefficient])
            x_axisNewFloat = np.append(x_axisNewFloat,y_axisFloat[coefficient])
            
        
        plt.figure()
        plt.plot(x_axis,y_axisFloat,color='#3ae9ac',linestyle='dashed', linewidth = 3,
                                    marker='o', markerfacecolor='#e9e33a', markersize=12)
        plt.xlabel('bar')  
        plt.ylabel('bar/degree')
        plt.title('correlation of bar and bar-degree coefficient')
        for _,y in zip(x_axis,y_axisFloat):
            plt.text(_,y,str(round(y,5)),fontsize='x-small',fontweight='bold')
        #plt.ioff()
        
        plt.figure()
        plt.bar(x_axisNewFloat,sigmaFloat,width=0.0001,color='#3aa9e9')
        for x,_ in zip(x_axisNewFloat,sigmaFloat):
            plt.text(x,_,str(round(x,5)),fontsize='x-small',fontweight='bold' )
        plt.xlabel('bar/degree coeffcient')
        plt.ylabel('range of difference')
        plt.title('comparison of calculated pressure to orig pressure value using coefficients')

        currentValue = 0.01875
        stopValue  =   0.025
        stepValue  =   0.0005
        i = 0
        while currentValue < stopValue : 
            sigmaFloat2 = np.append(sigmaFloat2,((currentValue * anglesFloat[8]  - 4.6)))#,
             #                                    (currentValue * anglesFloat[11] - 6)))
            print("{0} has delta of : {1}".format(currentValue,sigmaFloat2[i])) 
            x_axisNewFloat2 = np.append(x_axisNewFloat2,currentValue)
            #x_axisNewFloat2 = np.append(x_axisNewFloat2,currentValue)
            #x_axisNewFloat2 = np.append(x_axisNewFloat2,currentValue)
            currentValue += stepValue
            i += 1

        plt.figure()
        plt.bar(x_axisNewFloat2,sigmaFloat2,width = 0.001, color='#e93a3a')
        for x,_ in zip(x_axisNewFloat2,sigmaFloat2):
            plt.text(x,_,str(round(x,5)),fontsize='xx-small',fontweight='bold' )
        plt.xlabel('range of coeffs from 0.01874 up to 0.0186')
        plt.ylabel('difference')
        plt.title('4 bar ')
        plt.show(block=True)
    def makeBlur(self):
        try:
            self.blur = cv2.blur(self.img,(5,5))
        except Exception:
            print("caught an exceptpon in make blur")
            return 0
        #cv2.imshow("blurred",self.img)
    def makeGray(self):
        try:
            self.gray_img = cv2.cvtColor(self.blur,cv2.COLOR_BGR2GRAY)
        except Exception:
            print("caught an exception in make gray")
            return 0
        #cv2.imshow("gray image", self.gray_img)
    def cutBackground(self):
        mask = np.zeros(self.gray_img.shape[:2], dtype="uint8")#mem alloc for mask
        x = self.circles[0,0,0]
        y = self.circles[0,0,1]
        r = self.circles[0,0,2]
        cv2.circle(mask , (x,y),r,255,-1) # Thickness of -1 px will fill the circle shape by the specified color.
        #cv2.imshow("circular mask", mask)
        masked = cv2.bitwise_and(self.gray_img, self.gray_img, mask=mask)
        #cv2.imshow("only circle",masked)
        return masked
    def findPressure(self):
        self.alpha_difference = self.alpha_deg - self.alpha_zero_pressure
        if self.alpha_difference <= 0 : 
            self.pressure = 0.
            self.now = datetime.now()
            self.current_time = self.now.strftime("%H:%M:%S")
            #print("pressure: 0.0 Bar")
            #print("======================")
            return self.pressure
        else:
            print("alpha difference",self.alpha_difference)
            self.pressure = self.bars_pro_degree * self.alpha_difference
            self.now = datetime.now()
            self.current_time = self.now.strftime("%H:%M:%S")
            self.sendData()
            self.event.set()

            
            #print("======================")
            print("pressure:",round(self.pressure,1),"+- 0.1 bar")
            return round(self.pressure,1)
    def findAngle(self): 
        if self.x_arrow >= self.x_2_quadrant_limit and self.y_arrow >= self.y_2_quadrant_limit and self.x_arrow <= self.x_1_quadrant_limit and self.y_arrow <= self.y_1_quadrant_limit:
            #print("it's 1st quadrant")
            # sometimes arrow can be in 1. quadrant, but higher than circle's center for 2-3 pixels
            # in such exceptions can be useful to use this if-condition, which doesn't affect the correctness of measure
            if self.y0 > self.y_arrow : 
                self.alpha_deg = (math.atan((self.x0-self.x_arrow)/(self.y0-self.y_arrow))*180.0/math.pi)
            else:
                self.alpha_deg = (math.atan((self.x0-self.x_arrow)/(self.y_arrow-self.y0))*180.0/math.pi)
            #print("angle:",self.alpha_deg)
        if self.x_arrow < self.x_3_quadrant_limit and self.y_arrow > self.y_3_quadrant_limit and self.x_arrow > self.x_2_quadrant_limit and self.y_arrow < self.y_2_quadrant_limit:
            if self.x0 > self.x_arrow:
                self.alpha_deg = ((math.pi - math.atan((self.x0-self.x_arrow)/(self.y0-self.y_arrow)))*180.0/math.pi)
            else:
                self.alpha_deg = ((math.pi - math.atan((self.x_arrow-self.x0)/(self.y0-self.y_arrow)))*180.0/math.pi)     
            #print("it's 2nd quadrant")
            #print("angle:", self.alpha_deg)   
        if self.x_arrow >= self.x_3_quadrant_limit and self.y_arrow >= self.y_3_quadrant_limit and self.x_arrow <= self.x_4_quadrant_limit and self.y_arrow <= self.y_4_quadrant_limit:
            #print("it's 3rd quadrant")
            if (self.x_3_quadrant_limit-self.x_arrow) != 0 :
                if(self.y_4_quadrant_limit-self.y_arrow)!=0:  
                    self.alpha_deg = ((math.pi + math.atan((self.x_arrow-self.x0)/(self.y0-self.y_arrow)))*180.0/math.pi)
                else:
                    self.alpha_deg = 235.0
            else:
                self.alpha_deg = 135.
        if self.x_arrow < self.x_4_quadrant_limit and self.y_arrow > self.y_4_quadrant_limit and self.x_arrow > self.x_1_quadrant_limit and self.y_arrow < self.y_1_quadrant_limit:
            #print("it's 4th quadrant")
            self.alpha_deg = ((2*math.pi - math.atan((self.x_arrow-self.x0)/(self.y_arrow-self.y0)))*180.0/math.pi)
            #print("angle:", self.alpha_deg)
    def drawCircle(self):
        self.circles = cv2.HoughCircles(self.gray_img,cv2.HOUGH_GRADIENT_ALT,dp=1.5,minDist=5,param1=300,param2=0.9,minRadius=0, maxRadius=1200)
        if self.circles is None:
            return 0
        self.circles = np.uint16(np.around(self.circles))
        self.x0 = self.circles[0,0,0] 
        self.y0 = self.circles[0,0,1]  
        self.r  = self.circles[0,0,2] 
        self.img = cv2.circle(self.img,(self.x0,self.y0),self.r,(0,255,0),3)
        self.masked_image = self.cutBackground()
        self.threshold_threshold = 30 
        ret, thresh = cv2.threshold(self.masked_image.copy(), self.threshold_threshold, 255, cv2.THRESH_BINARY_INV)
        self.edges = self.CannyEdges()
        #cv2.imshow("edges", edges)
        #finding general contours
        contours, hier = cv2.findContours(thresh.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        '''
        findContours function has three parameters: 
            - the input image, 
            - the hierarchy type, 
            - and the contour approximation method.
        
        The second parameter specifies the type of hierarchy tree returned by the function. 
        
        One of the supported values is cv2.RETR_TREE, which tells the function 
        to retrieve the entire hierarchy of external and internal contours. These relationships may matter
        if we are searching for smaller objects (or smaller regions) inside larger objects (or larger regions). 
        
        If you only want to retrieprint('angle')ve the most external contours, use cv2.RETR_EXTERNAL. 
        This may be a good choice in cases where the objects appear on a plain background and we do not care about
        finding objects within objects.
        '''
        for c in contours:
            x,y,w,h = cv2.boundingRect(c)
            #cv2.rectangle(self.img, (x,y), (x+w, y+h), color=(0, 255, 0), thickness=2)
            digit = thresh[y:y+h, x:x+w]
            resized_digit = cv2.resize(digit, (18,18))
            # Padding the digit with 5 pixels of black color (zeros) in each side to finally produce the image of (28, 28)
            padded_digit = np.pad(resized_digit, ((5,5),(5,5)), "constant", constant_values=0)
            self.preprocessed_digits.append(padded_digit)
            #cv2.imshow("lol",self.img)
        
        
        ##################################################
        #lines = self.Hough_Lines()
        
        '''
        The parameters of HoughLinesP are as follows:
            - The image.cv2.imshow("lines", img)
            
            - The resolution or step size to use when searching for lines. 
            rho is the positional step size in pixels, while theta is the rotational step size in radians.
            For example, if we specify rho=1 and theta=np.pi/180.0, 
            we search for lines that are separated by as little as 1 pixel and 1 degree.
            
            - The threshold, which represents the threshold below which a line is discarded. 
            The Hough transform works with a system of bins and votes, with each bin representing a line, 
            so if a candidate line has at least the threshold number of votes, it is retained;  
            otherwise, it is discarded.

            - minLineLength and maxLineGap, which we mentioned previously.
        '''

        # draw complete arrow of the monometer: 
        # startpoint - middle of the circle 
        # endpoint -end of the arrow on monometer 
        self.Hough_Lines()
        
        
        #print("coordinates of the arrow: ",self.x_arrow,", ",self.y_arrow)
        # find the limit point of every quadrant in order to properly 
        # calculate the angle of the arrow, according to its position 
        self.x_1_quadrant_limit = self.x0  
        self.y_1_quadrant_limit = self.y0 + self.r 
        
        self.x_2_quadrant_limit = self.x0 - self.r 
        self.y_2_quadrant_limit = self.y0 - 6 

        self.x_3_quadrant_limit = self.x0 + 6 
        self.y_3_quadrant_limit = self.y0 - self.r 

        self.x_4_quadrant_limit = self.x0 + self.r 
        self.y_4_quadrant_limit = self.y0 + 6 

        #print("x_1_quadrant_limt",self.x_1_quadrant_limit)
        #print("y_1_quadrant_limt",self.y_1_quadrant_limit)

        #print("x_2_quadrant_limt",self.x_2_quadrant_limit)
        #print("y_2_quadrant_limt",self.y_2_quadrant_limit)

        #print("x_3_quadrant_limt",self.x_3_quadrant_limit)
        #print("y_3_quadrant_limt",self.y_3_quadrant_limit)

        #print("x_4_quadrant_limt",self.x_4_quadrant_limit)
        #print("y_4_quadrant_limt",self.y_4_quadrant_limit)
    #def finalResult(self):
    #    pass
    #    cv2.namedWindow("result",cv2.WINDOW_NORMAL)
    #    cv2.imshow("result",self.img)
    #    cv2.waitKey(1)


    def CannyEdges(self):
        edges = cv2.Canny(self.masked_image,self.canny_threshold1,self.canny_threshold2)
        #print("threshold1: ",self.canny_threshold1)
        #print("threshold2:",self.canny_threshold2)
        return edges
    def Hough_Lines(self):
        lines = cv2.HoughLinesP(self.edges,1, np.pi/180.0, self.houghlines_threshold, self.minLineLength, self.maxLineGap)
        if lines is not None:
            #print("found the lines")
            self.x_arrow = lines[0,0,0] # 
            self.y_arrow = lines[0,0,1]
        
        cv2.line(self.img,(self.x0,self.y0), (self.x_arrow,self.y_arrow), (0,0,255),2)
        edges_copy = self.img
        cv2.line(edges_copy,(self.x0,self.y0), (self.x_arrow,self.y_arrow), (0,0,255),2)
        return edges_copy
    def runAll(self):
        if self.makeBlur() !=0:
            if self.makeGray() != 0:
                if self.drawCircle() !=0:
                    self.findAngle()
                    self.findPressure()
                    
                    #self.s.sendData(self.pressure,self.current_time)
                    return self.img 
                    #print("{}. Attempt".format(self.i))
                    #self.i+=1
                else:
                    #print("there are no circles")
                    return None
            else:
                    print("making gray failed")
                    return None
        else:
            return None
        #    print("blurring failed")
       
