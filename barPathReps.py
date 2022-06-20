#AIMS
# - Input video of lift DONE
# - Be able to select bar DONE
# - Track movement of the bar DONE
# - Differentiate between eccentric and concentric DONE
# - Plot bar path and send too graph to show path DONE
# - Plot bar path on video DONE
# - Connect dots between points
# - Plot best bar path for SBD respectively DONE 
# - Plot error of bar path (harder than once thought)

# - Account for mutiple reps 
# Get start of the rep DONE
# Get end of rep height buffer zone DONE
# If buffer gets entered and exited count rep DONE
# Dont count movement within buffer
# show difference between reps
# Visualise 

# - Show bar path for all reps 
# - Show error for all reps and decide on best rep

# - Track depth on squat

# - Allow users to trim down videos 
# - Save video visulasiation and graph visulaistaion 
# - Save raw trimmed videos
from turtle import color
import numpy as np
import cv2 
import matplotlib.pyplot as plt
from math import sqrt

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))


class lifts: 
    def __init__(self,path):
        self.path = path
        self.cap = cv2.VideoCapture(path)
        self.X = []
        self.Y = []
        self.XPart = []
        self.Ypart = []
        self.ix = 0
        self.iy = 0
        self.oldPoints = []
        self.oldFrame = 0
        self.midIndex = 0
        self.top = 0
        self.reps = 0 
        self.current = 0 
        self.inBuffer = False
        self.iterations = 0
        self.enter = []
        self.exit =  []
        self.liveReps = 0
        self.visFrame = 0

    def setCap(self):
        self.cap = cv2.VideoCapture(self.path)
    def selectBar(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK: 
            self.ix,self.iy = x,y
            self.oldPoints = np.array([[self.ix,self.iy]],dtype=np.float32)
    def locateBar(self):
        cv2.namedWindow('Select bar')
        while True:
            ret, frame = self.cap.read()
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            self.oldFrame = cv2.resize(frame, (500,500))
            cv2.setMouseCallback('Select bar', self.selectBar)
            cv2.imshow('Select bar',self.oldFrame)
            k = cv2.waitKey(0) & 0xFF
            if k == ord('a'):
                break
    def opticalFlow(self):
        while (self.cap.isOpened()):
            ret, frame = self.cap.read()
            if ret == True:
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                frame = cv2.resize(frame, (500,500))
                p1,st,err = cv2.calcOpticalFlowPyrLK(self.oldFrame, frame, self.oldPoints, None, **lk_params)
                self.oldFrame = frame.copy()
                self.oldPoints = p1
                x, y = p1.ravel()
                self.X.append(x)
                self.Y.append(y)
                cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
                self.current = y
                self.countRep()
                self.iterations += 1
                cv2.imshow("Video",frame)
            else:
                break
            if cv2.waitKey(1) == ord('q'):
                break
        if len(self.enter) == len(self.exit):
            self.enter.append(self.iy)
    
    
    def videoVisualisation(self):
        print(len(self.enter))
        print(len(self.exit))
        print("Rep(s): ", self.reps)
        self.oldPoints = np.array([[self.ix,self.iy]],dtype=np.float32)
        self.setCap()
        while True:
            ret, frame = self.cap.read()
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            self.oldFrame = cv2.resize(frame, (500,500))
            break
        while True:        
            ret, frame = self.cap.read()
            if ret == True:
                self.visframe = cv2.resize(frame, (500,500))
                gray_frame = cv2.cvtColor(self.visframe,cv2.COLOR_BGR2GRAY)
                p1,st,err = cv2.calcOpticalFlowPyrLK(self.oldFrame, gray_frame, self.oldPoints, None, **lk_params)
                self.oldFrame = gray_frame.copy()
                self.oldPoints = p1
                x, y = p1.ravel()
                self.current = y
                self.checkRep()
                s = str(self.liveReps)
                s1 = str(self.reps)
                s2 = "Reps: " + s + "/" +s1
                cv2.putText(self.visframe,(s2),(10,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA )
                cv2.circle(self.visframe, (int(x), int(y)), 5, (0, 0, 255), -1)

                self.getPoints()
                
                cv2.imshow("Visualisation", self.visframe)
                if cv2.waitKey(1) == ord('q'):
                    break
            else:
                self.setCap()
                while True:
                    self.liveReps = 0
                    ret, frame = self.cap.read()
                    self.visframe = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                    self.oldFrame = cv2.resize(self.visframe, (500,500))
                    self.oldPoints = np.array([[self.ix,self.iy]],dtype=np.float32)
                    break


class squat(lifts):
    def getLowest(self):
        low = 0
        i = 0
        for y in self.YPart:
            if y > low:
                low = y
                self.midIndex = i
            i+=1   
    def countRep(self):
        bufferBottom = self.iy*1.075

        if self.current < bufferBottom and self.inBuffer == False:
                self.inBuffer = True
                self.enter.append(self.iterations)

        elif self.current > bufferBottom and self.inBuffer == True:
            self.reps += 1
            self.exit.append(self.iterations)
            self.inBuffer = False
    def checkRep(self):
        bufferBottom = self.iy*1.075
        if self.liveReps <= self.reps:
            if self.current < bufferBottom and self.inBuffer == False:
                self.inBuffer = True

            elif self.current > bufferBottom and self.inBuffer == True:
                self.liveReps += 1
                self.inBuffer = False

    def getPoints(self):

        self.XPart = self.X[self.exit[self.liveReps-1]:self.enter[self.liveReps]]
        self.YPart = self.Y[self.exit[self.liveReps-1]:self.enter[self.liveReps]]
        self.getLowest()
        for i in range(len(self.YPart)):
            if i < self.midIndex:
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[i]),int(self.YPart[i])),radius=1, color=(0,0,255),thickness=-1)
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[1]),int(self.YPart[i])),radius=1, color=(0,255,0),thickness=-1)

            else:
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[i]),int(self.YPart[i])),radius=1, color=(255,0,0),thickness=-1)
        p1 = 0, int(self.iy*1.075)
        p2 = 499, int(self.iy*1.075)
        self.visframe = cv2.line(self.visframe, (p1),(p2),color=(255,255,255),thickness=1)

class deadLifts(lifts):
    def getHighest(self):
        high = 1000
        i = 0
        for y in self.YPart:
            if y < high:
                high = y
                self.midIndex = i
            i+=1
    def countRep(self):
        bufferBottom = self.iy*0.975

        if self.current > bufferBottom and self.inBuffer == False:
                self.inBuffer = True
                self.enter.append(self.iterations)

        elif self.current < bufferBottom and self.inBuffer == True:
            self.reps += 1
            self.exit.append(self.iterations)
            #self.getDataPoints()
            self.inBuffer = False
    def checkRep(self):
        bufferBottom = self.iy*0.975
        if self.liveReps <= self.reps:
            if self.current > bufferBottom and self.inBuffer == False:
                self.inBuffer = True

            elif self.current < bufferBottom and self.inBuffer == True:
                self.liveReps += 1
                self.inBuffer = False

    def getPoints(self):
        self.XPart = self.X[self.exit[self.liveReps-1]:self.enter[self.liveReps]]
        self.YPart = self.Y[self.exit[self.liveReps-1]:self.enter[self.liveReps]]
        self.getHighest()
        for i in range(len(self.YPart)):
            if i < self.midIndex:
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[i]),int(self.YPart[i])),radius=1, color=(255,0,0),thickness=-1)
            else:
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[i]),int(self.YPart[i])),radius=1, color=(0,0,255),thickness=-1)
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[1]),int(self.YPart[i])),radius=1, color=(0,255,0),thickness=-1)

        p1 = 0, int(self.iy*0.975)
        p2 = 499, int(self.iy*0.975)
        self.visframe = cv2.line(self.visframe, (p1),(p2),color=(255,255,255),thickness=1)

class benchPress(lifts):
    def distance(self,x1,y1,x2,y2):
            return sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def getLowest(self):
        low = 0
        i = 0
        for y in self.YPart:
            if y > low:
                low = y
                self.midIndex = i
            i+=1   
    def countRep(self):
        bufferBottom = self.iy*1.1

        if self.current < bufferBottom and self.inBuffer == False:
                self.inBuffer = True
                self.enter.append(self.iterations)

        elif self.current > bufferBottom and self.inBuffer == True:
            self.reps += 1
            self.exit.append(self.iterations)
            self.inBuffer = False
    def checkRep(self):
        bufferBottom = self.iy*1.1
        if self.liveReps <= self.reps:
            if self.current < bufferBottom and self.inBuffer == False:
                self.inBuffer = True

            elif self.current > bufferBottom and self.inBuffer == True:
                self.liveReps += 1
                self.inBuffer = False

    def getPoints(self):

        self.XPart = self.X[self.exit[self.liveReps-1]:self.enter[self.liveReps]]
        self.YPart = self.Y[self.exit[self.liveReps-1]:self.enter[self.liveReps]]
        self.getLowest()
        #print(self.midIndex)
        for i in range(len(self.YPart)):
            if i < self.midIndex:
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[i]),int(self.YPart[i])),radius=1, color=(0,0,255),thickness=-1)
                
            else:
                self.visframe = cv2.circle(self.visframe,(int(self.XPart[i]),int(self.YPart[i])),radius=1, color=(255,0,0),thickness=-1)
            
            p3  = int(self.XPart[1]),int(self.YPart[1])
            p4 = int(self.XPart[self.midIndex]),int(self.YPart[self.midIndex])
            print(p3)
            print(p4)
            self.visframe = cv2.line(self.visframe, (p3),(p4),color=(0,255,0),thickness=1)        #self.visframe = cv2.circle(self.visframe,(int(i),int()),radius=1, color=(0,255,0),thickness=-1)

        p1 = 0, int(self.iy*1.1)
        p2 = 499, int(self.iy*1.1)
        self.visframe = cv2.line(self.visframe, (p1),(p2),color=(255,255,255),thickness=1)

    def getDataPoints(self):
        self.getLowest()
        for i in range(len(self.Y)):
            if i < self.midIndex:
                self.eX.append(self.X[i])
                self.eY.append(self.Y[i])
            else:
                self.cX.append(self.X[i])
                self.cY.append(self.Y[i])

        for i in (self.eX):
            c = 10000
            for i2 in range(499):
                d1 = self.distance(self.ix,self.iy,i,i2)
                d2 = self.distance(i,i2,self.X[self.midIndex],self.Y[self.midIndex])
                d3 = self.distance(self.ix,self.iy,self.X[self.midIndex],self.Y[self.midIndex])
                d4 = (d1 + d2)-d3
                
                if d4 < c:
                    c = d4
                    y = i2
            self.oX.append(i)
            self.oY.append(y)

                    
path = ('C:/Users/olive/Documents/Portfolio/Bar path tracker/Videos/deadliftReps.MP4')

s = deadLifts(path)
s.locateBar()
s.opticalFlow()
s.videoVisualisation()

