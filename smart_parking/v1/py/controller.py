from motion_detector import MotionDetector
import os
import os.path
import time

class Controller:
    
    def __init__(self, points, previousTime, currentTime, carPark):
        
        self.points = points
        self.previousTime = previousTime
        self.currentTime = currentTime
        self.carPark = carPark
        self.detector = MotionDetector(self.points, 1, self.carPark)
        
    def runController(self):
            
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
        
        return self.detector.detect_motion(videoFilePath, hasIncomingVideoCaptureChanged), self.carPark