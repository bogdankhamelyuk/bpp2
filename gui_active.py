import tkinter as tk
from gauge import Gauge
import PIL.Image, PIL.ImageTk
from queue import Queue 
import cv2 
import os 
import sys
import threading 
from functools import partial



class Geometry:
	def centerPos(parent_height, parent_width, child_height,child_width):
		x_coordinate = int((parent_width/4)-(child_width/2))
		y_coordinate = int((parent_height/2)-(child_height/2))
		return x_coordinate, y_coordinate

class App:
    def __init__(self, master):
        # initializing the event object
        
        self.houghWidgetTop = False
        self.q = Queue(maxsize=1)
        self.cannyWidgetTop=False
        self.q2 = Queue(maxsize=1)
        
        self.e = threading.Event()
        #self.e.set()
        #print("event status:",self.e.issSet)
        self.vid = Gauge(self.e)
        
        
        self.master = master
        self.master.minsize(800,650)
        self.master.title("OpenCV")
        self.master.protocol("WM_DELETE_WINDOW",self.closeApp)
        self.window_height =640
        self.window_width = 800
        self.menubar = tk.Menu(self.master, background='white',foreground='black', 
                                activebackground='orange',activeforeground='white')
        
        self.menubar.add_command(label="Restart",command = self.restartApp)
        self.menubar_settings = tk.Menu(self.menubar,tearoff=0,background='white',foreground='black')
        self.menubar_settings.add_command(label="Canny Parameters",command = self.startCannyThread)
        self.menubar_settings.add_command(label="Hough Lines Parameters",command = self.showHough)
        self.menubar_settings.add_command(label="Change Address")
        self.menubar.add_cascade(label="Settings",menu=self.menubar_settings)
        self.menubar.add_command(label="Change Camera", command=self.changeCamera)
        self.master.config(menu=self.menubar)
        
        self.master.columnconfigure(0,weight=1)
        self.master.rowconfigure(0,weight=1)
        self.master.rowconfigure(2,weight=1)

        #frame for Video  
        self.VideoContent = tk.Frame(self.master)
        self.VideoContent.grid(column=0, row=0,  columnspan=3, rowspan=2,pady=0,padx=0)
        #label for video 
        self.labelVideo = tk.Label(self.VideoContent,borderwidth=3,relief="ridge")
        self.labelVideo.grid(column=0, row=0)
        self.VideoContent.columnconfigure(0,weight=1)
        self.VideoContent.rowconfigure(0,weight=1)
        
        self.textlabelOutput = tk.Label(self.master,text="pressure: "+str(self.vid.pressure),justify=tk.LEFT,height=1)
        self.textlabelOutput.grid(column=0,row=2,sticky=tk.W)
        
        
        self.delay = 5
        self.updateLabel()
        self.master.mainloop() 
##############################################################################################       
    def updateLabel(self):
        self.status, self.frame, self.final_image = self.vid.update()
        if self.status:
            image = self.frame
            #image = cv2.resize(image,(self.master.winfo_width(),self.master.winfo_height()),interpolation=cv2.INTER_LINEAR)
            image = cv2.resize(image,(800,600),interpolation=cv2.INTER_LINEAR)
            image = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(image))
            
            self.labelVideo.configure(image=image)
            self.labelVideo.image=image
            self.updateOutput()
        self.master.after(self.delay,self.updateLabel)
##############################################################################################
    def updateOutput(self):
        if self.e.isSet() is True:
            self.textlabelOutput.config(text="pressure: "+str(self.vid.findPressure()))
            self.e.clear()
##############################################################################################
    def closeApp(self):
        self.master.destroy()
##############################################################################################
    def restartApp(self):
        self.vid.__del__()
        self.python = sys.executable
        os.execl(self.python, self.python, *sys.argv)
##############################################################################################
    def cannyOff(self,event):
        self.win_canny.destroy()
        with self.q.mutex:
            self.q.queue.clear()
##############################################################################################
    def startCannyThread(self):
            
        if self.q.full() is not True:    
            self.canny_widget_thread = threading.Thread(target=self.showCanny,args=())
            self.canny_widget_thread.name ='canny widget'
            self.canny_widget_thread.daemon = True
            self.canny_widget_thread.start()
        else:
            self.win_canny.focus()
##############################################################################################
    def showCanny(self):
        self.win_canny = tk.Toplevel(self.master)
        self.win_canny.bind('<Destroy>',self.cannyOff)
        self.win_canny.title("Canny Parameters")
        self.win_canny.geometry("800x400")
        self.win_canny.resizable(0,0)
        
        self.win_canny.columnconfigure(0,weight=1)
        self.win_canny.columnconfigure(1,weight=1)
        
        self.win_canny_frame = tk.Frame(self.win_canny)
        self.win_canny_frame.grid(column=0,row=0,rowspan=1,sticky=tk.W+tk.E)
        
        self.win_canny_threshold1 = tk.Scale(self.win_canny_frame,orient=tk.HORIZONTAL,from_=50,to=500,command = lambda e: self.updateCannyThreshold1(),sliderlength=15,length=350,width=20)
        self.win_canny_threshold1.set(self.vid.canny_threshold1)
        self.win_canny_threshold1.grid(column=0,row=0,padx=30,pady=50)

        self.win_canny_threshold2 = tk.Scale(self.win_canny_frame,orient=tk.HORIZONTAL,from_=50,to=500,command = lambda e: self.updateCannyThreshold2(),sliderlength=15,length=350,width=20)
        self.win_canny_threshold2.set(self.vid.canny_threshold2)
        self.win_canny_threshold2.grid(column=0,row=1,padx=30,pady=50)

        self.win_canny_label = tk.Label(self.win_canny,borderwidth=3,relief="ridge")
        self.win_canny_label.grid(column = 1, row=0)
        status = True
        self.q.put(status)
        self.updateCanny()            
        #self.win_canny.mainloop()
#############################################################################################    
    def updateCanny(self):
        canny_edges = self.vid.CannyEdges()
        canny_edges = cv2.resize(canny_edges,(400,400),interpolation=cv2.INTER_AREA)
        canny_edges = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(canny_edges))
        self.win_canny_label.configure(image=canny_edges)
        self.win_canny_label.image=canny_edges
        try:
            self.win_canny_label.after(5,self.updateCanny())
        except:
            pass
        #self.win_canny.after(1,self.updateCanny)
##############################################################################################
    def houghOff(self,event):
        self.win_hough.destroy()
        with self.q2.mutex:
            self.q2.queue.clear()
##############################################################################################
    def showHough(self):
        self.win_hough = tk.Toplevel(self.master)
        self.win_hough.bind('<Destroy>',self.houghOff)
        self.win_hough.title("Hough Parameters")
        self.win_hough.geometry("400x400")
        self.win_hough.resizable(0,0)
        
        self.win_hough.columnconfigure(0,weight=1)
        self.win_hough.columnconfigure(1,weight=1)
        self.win_hough.rowconfigure(0,weight=1)
        self.win_hough_frame = tk.Frame(self.win_hough)
        self.win_hough_frame.grid(column=0,row=0,rowspan=8, columnspan=3,sticky=tk.W+tk.E)

        self.win_hough_thresholdLabel = tk.Label(self.win_hough_frame, text="Threshold")
        self.win_hough_thresholdLabel.grid(row=0,column=2,pady=10,sticky=tk.N)
        
        self.win_hough_threshold1 = tk.Scale(self.win_hough_frame,orient=tk.HORIZONTAL,from_=5,to=50,command = lambda e: self.updateHoughThreshold(),sliderlength=15,length=350,width=20)
        self.win_hough_threshold1.set(self.vid.houghlines_threshold)
        self.win_hough_threshold1.grid(column=2,row=1,padx=30)
        self.win_empty1=tk.Label(self.win_hough_frame)
        self.win_empty1.grid(row=2,column=2,sticky=tk.N+tk.S)

        self.win_hough_minLineLabel = tk.Label(self.win_hough_frame, text="Min Line Length")
        self.win_hough_minLineLabel.grid(row=3,column=2,pady=10)
        self.win_hough_minLineLength = tk.Scale(self.win_hough_frame,orient=tk.HORIZONTAL,from_=10,to=100,command = lambda e: self.mnLineLength(),sliderlength=15,length=350,width=20)#ToDO
        self.win_hough_minLineLength.set(self.vid.minLineLength)
        self.win_hough_minLineLength.grid(column=2,row=4,padx=20)
        self.win_empty2=tk.Label(self.win_hough_frame)
        self.win_empty2.grid(row=5,column=5,sticky=tk.N)

        #self.win_empty3=tk.Label(self.win_hough_frame)
        #self.win_empty3.grid(row=2,column=5,sticky=tk.N)
        self.win_hough_minLineLabel = tk.Label(self.win_hough_frame, text="Max Line Gap")
        self.win_hough_minLineLabel.grid(row=6,column=2,pady=10)
        self.win_hough_maxLineGap = tk.Scale(self.win_hough_frame,orient=tk.HORIZONTAL,from_=10,to=100,command = lambda e: self.mxLineGap(),sliderlength=15,length=350,width=20)#ToDO
        self.win_hough_maxLineGap.set(self.vid.maxLineGap)
        self.win_hough_maxLineGap.grid(column=2,row=7,padx=30,pady=0)

        self.win_hough.columnconfigure(0,weight=1)
        self.win_hough.columnconfigure(1,weight=1)
        self.win_hough.columnconfigure(2,weight=1)

        self.win_hough.rowconfigure(1,weight=1)
        self.win_hough.rowconfigure(3,weight=1)
        self.win_hough.rowconfigure(5,weight=1)
        self.win_hough.rowconfigure(0,weight=1)
        self.win_hough.rowconfigure(2,weight=1)
        self.win_hough.rowconfigure(4,weight=1)
       
        status = True
        self.q2.put(status)
        #self.updateHough()
##############################################################################################
    def updateHough(self):
        hough_lines = self.vid.Hough_Lines()
        hough_lines = cv2.resize(hough_lines,(400,400),interpolation=cv2.INTER_AREA)
        hough_lines = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(hough_lines))
        self.win_hough_label.configure(image=hough_lines)
        self.win_hough_label.image=hough_lines
        try:
            self.win_hough_label.after(5,self.updateHough())
        except:
            pass
##############################################################################################
    def startHoughThread(self):
        if self.q2.full() is not True:    
            self.hough_widget_thread = threading.Thread(target=self.showHough,args=())
            self.hough_widget_thread.name ='hough widget'
            self.hough_widget_thread.daemon = True
            self.hough_widget_thread.start()
        else:
            self.win_hough.focus()
##############################################################################################
    def updateHoughThreshold(self):
        self.vid.houghlines_threshold = self.win_hough_threshold1.get()
##############################################################################################
    def mnLineLength(self):
        self.vid.minLineLength = self.win_hough_minLineLength.get()
##############################################################################################    
    def mxLineGap(self):
        self.vid.maxLineGap = self.win_hough_maxLineGap.get()
##############################################################################################
    def updateCannyThreshold1(self):
        #################################################################
        #!!!COMMENT THIS OUT FOR ONLY REAL PURPOSES!!!
        self.vid.canny_threshold1 = self.win_canny_threshold1.get()
        #################################################################
##############################################################################################
    def updateCannyThreshold2(self):
        self.vid.canny_threshold2 = self.win_canny_threshold2.get()
##############################################################################################
    def changeCamera(self):
        if self.vid.camera == 0:
            self.vid.capture.release()
            self.vid.capture = cv2.VideoCapture(2)

        elif self.vid.camera == 2:
            self.vid.capture.release()
            self.vid.capture = cv2.VideoCapture(0)#doesnt work!!!
            

def main(): 
    App(tk.Tk())

if __name__ == '__main__':
    main()