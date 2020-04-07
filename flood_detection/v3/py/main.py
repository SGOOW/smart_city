from __future__ import print_function
import cv2 as cv
import yaml
from datetime import datetime
import time
import os.path
from os import path
import shutil
from controller import Controller
from coordinates_generator import CoordinatesGenerator
from colors import *
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
from collections import deque
from water_level_data import WaterLevelSlots
from common import draw_str, draw_str_green, draw_str_red
import video
import cx_Oracle
#import base64
from motion_detector import MotionDetector

def init_child(lock_):
    global lock
    lock = lock_
    
capture_duration = 1


def setPoints(frame):
    if path.exists('images/p1.png'):
        os.remove('images/p1.png')
    cv.imwrite('images/p1.png', frame)
    with open('data/coordinates_1.yml', "w+") as points:
        generator = CoordinatesGenerator('images/p1.png', points, COLOR_RED)
        generator.generate()
        
def getPoints(frame, points):
    if path.exists('data/coordinates_1.yml'):
        return points
    else:
        setPoints(frame)
        try:
            with open('data/coordinates_1.yml', "r") as data:
                try:
                    points = yaml.safe_load(data)
                except yaml.YAMLError as exc:
                    print(exc)
        except IOError:
            print ("Could not open file! Please close data/coordinates_1.yml !")
        return points

def captureShortIntervalVideos(cap, lock):
    with lock:
        startDateTime = datetime.now()
        destinationDirectoryStr = startDateTime.strftime('FROM_%d_%m_%Y_%H_%M_%S_TO')
        current_directory = os.getcwd() + '\\captured_videos'
        
        out = cv.VideoWriter(current_directory + '\\output.mp4', 0x00000021, 5, (640,480))
            
        start_time = time.time()
        while( int(time.time() - start_time) < capture_duration ):
            ret, frame = cap.read()
            if ret==True:
                out.write(frame)
            else:
                break
        
        out.release()
        
        endDateTime = datetime.now()
        destinationDirectoryStr = destinationDirectoryStr + endDateTime.strftime('_%d_%m_%Y_%H_%M_%S')
        print('Current Timestamp : ', destinationDirectoryStr)
            
        
        final_directory = os.path.join(current_directory, destinationDirectoryStr)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
                
        shutil.move(current_directory + '\\output.mp4', final_directory + '\\output.mp4')
        return None, None

def persistWaterLevelData(waterLevel):
    sql = ('insert into flood_detection(current_level, precise_counter) ' +
           'values(:current_level, :precise_counter)')
    
    try:
        # establish a new connection
        with cx_Oracle.connect('gsmuser/oracle@//localhost:1521/orcl') as connection:
            # create a cursor
            with connection.cursor() as cursor:
                # execute the insert statement
                cursor.execute(sql, [waterLevel, time.time_ns()])
                # commit work
                connection.commit()
    except cx_Oracle.Error as error:
        print('SQL Error occurred:')
        print(error)    

def main():
    import sys
    
    if path.exists('data/coordinates_1.yml'):
        os.remove('data/coordinates_1.yml')
        
    points = None
    waterLevelSlots = None
    
    try:
        fn = sys.argv[1]
    except:
        fn = 0
    cap = video.create_capture(fn)

    def fetchShortIntervalVideos(ctrl, motion_detector, coordinates_data, times, statuses, lock):
        with lock:
             videoFilePath, hasIncomingVideoCaptureChanged = ctrl.getVideoFilePath()
             return videoFilePath, hasIncomingVideoCaptureChanged, motion_detector, coordinates_data, times, statuses
    
    threadn = cv.getNumberOfCPUs()
    pending = deque()
    lock = Lock()
    pool = ThreadPool(processes = threadn, initializer = init_child, initargs=(lock,))
    
    threaded_mode = True
    ctrl = None
    motionDetector = None
    
    lastsave = 0
    coordinates_data = None
    times = None 
    statuses = None
    
    pointsCaptured = False
    while True:
        with lock:
            while len(pending) > 1 and pending[0].ready() and pending[1].ready():
                payload = pending.popleft().get()
                if len(payload) == 6:
                    videoFilePath, hasIncomingVideoCaptureChanged, motion_detector, coordinates_data, times, statuses = payload
                    if videoFilePath == None and hasIncomingVideoCaptureChanged == None:
                        break
                    else:
                    
                        if hasIncomingVideoCaptureChanged == True:
                            capture = cv.VideoCapture(videoFilePath)
                            while capture.isOpened():
                                result, frame = capture.read()
                                if not result:
                                    capture.release()
                                    continue
                                else:
                                    res, evaluated_waterLevelSlots  = motion_detector.process_algo_per_frame(frame, capture, coordinates_data, times, statuses)
                                    
                                    draw_str(res, (5, 20), WaterLevelSlots.LEVEL_REACHED_MSG
                                             + str(evaluated_waterLevelSlots.get_current_water_level()))
                        
                                    if time.time() - lastsave > 1:
                                        lastsave = time.time()
                                        persistWaterLevelData(evaluated_waterLevelSlots.get_current_water_level())
                        
                        cv.namedWindow('flood-detection', cv.WINDOW_NORMAL)
                        cv.setWindowProperty('flood-detection', 0, 1)
                        
                        cv.imshow('flood-detection', res)
                         
        if len(pending) < threadn:
            
            if not pointsCaptured:
                _ret, frame = cap.read()
                points = getPoints(frame, points)
                waterLevelSlots = WaterLevelSlots(len(points))
                ctrl = Controller(points, None, None)
                motionDetector = MotionDetector(points, 1, waterLevelSlots)
                coordinates_data, times, statuses = motionDetector.detect_motion_activity()
                pointsCaptured = True
           
            if threaded_mode:
                task_put_videos = pool.apply_async(captureShortIntervalVideos, (cap, lock))
                task_get_videos = pool.apply_async(fetchShortIntervalVideos,
                                                   (ctrl, motionDetector, coordinates_data, times, statuses, lock))
                
            
            pending.append(task_put_videos)
            pending.append(task_get_videos)
        
        ch = cv.waitKey(1)
        if ch == ord(' '):
            threaded_mode = not threaded_mode
        if ch == 27:
            break

    print('Done')
    cap.release()


if __name__ == '__main__':
    print(__doc__)
    main()
    if path.exists('data/coordinates_1.yml'):
        os.remove('data/coordinates_1.yml')
    cv.destroyAllWindows()