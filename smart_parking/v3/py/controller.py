import os
import os.path
import time

class Controller:
    
    def __init__(self, points, previousTime, currentTime):
        
        self.points = points
        self.previousTime = previousTime
        self.currentTime = currentTime
    
    def getVideoFilePath(self):
            
        workingDirectory = os.getcwd() + '\\captured_videos'
        hasIncomingVideoCaptureChanged = False
        try:
            
            videoCaptureDirectory = max([os.path.join(workingDirectory,d) 
                        for d in os.listdir(workingDirectory)], key=os.path.getmtime)
    
            self.currentTime = time.ctime(os.path.getmtime(videoCaptureDirectory))
            
        except FileNotFoundError:
            pass
        
        if self.currentTime == self.previousTime:
            hasIncomingVideoCaptureChanged = False
            return None, None
        
        hasIncomingVideoCaptureChanged = True
        self.previousTime = self.currentTime
                
                
        videoFilePath = videoCaptureDirectory + '//output.mp4'
        return videoFilePath, hasIncomingVideoCaptureChanged