import cv2 as open_cv
import numpy as np
import logging
from drawing_utils import draw_contours
from colors import COLOR_GREEN, COLOR_WHITE, COLOR_BLUE
import cx_Oracle
import time
from statistics import mode 

class MotionDetector:
    LAPLACIAN = 1.4
    DETECT_DELAY = 1

    def __init__(self, coordinates, start_frame, area):
        #self.video = video
        self.coordinates_data = coordinates
        self.start_frame = start_frame
        self.contours = []
        self.bounds = []
        self.mask = []
        self.area = area
        self.previousStatusesCount = 0
        self.currentStatusesCount = 0
        self.count = 0
        self.list = []
        
    def detect_motion_activity(self, video, hasVideoChanged):
        if hasVideoChanged == True:
            capture = open_cv.VideoCapture(video)
            coordinates_data = self.coordinates_data
            logging.debug("coordinates data: %s", coordinates_data)
    
            for p in coordinates_data:
                coordinates = self._coordinates(p)
                logging.debug("coordinates: %s", coordinates)
    
                rect = open_cv.boundingRect(coordinates)
                logging.debug("rect: %s", rect)
    
                new_coordinates = coordinates.copy()
                new_coordinates[:, 0] = coordinates[:, 0] - rect[0]
                new_coordinates[:, 1] = coordinates[:, 1] - rect[1]
                logging.debug("new_coordinates: %s", new_coordinates)
    
                self.contours.append(coordinates)
                self.bounds.append(rect)
    
                mask = open_cv.drawContours(
                    np.zeros((rect[3], rect[2]), dtype=np.uint16),
                    [new_coordinates],
                    contourIdx=-1,
                    color=255,
                    thickness=-1,
                    lineType=open_cv.LINE_8)
    
                mask = mask == 255
                self.mask.append(mask)
                logging.debug("mask: %s", self.mask)
    
            statuses = [False] * len(coordinates_data)
            times = [None] * len(coordinates_data)

            return capture, coordinates_data, times, statuses
    
    def process_algo_per_frame(self, frame, capture, coordinates_data, times, statuses):
        
        zones = []
        
        blurred = open_cv.GaussianBlur(frame.copy(), (5, 5), 3)
        grayed = open_cv.cvtColor(blurred, open_cv.COLOR_BGR2GRAY)
        new_frame = frame.copy()
        logging.debug("new_frame: %s", new_frame)

        position_in_seconds = capture.get(open_cv.CAP_PROP_POS_MSEC) / 1000.0
        
        for index, c in enumerate(coordinates_data):
            status = self.__apply(grayed, index, c)

            if times[index] is not None and self.same_status(statuses, index, status):
                times[index] = None
                continue

            if times[index] is not None and self.status_changed(statuses, index, status):
                if position_in_seconds - times[index] >= MotionDetector.DETECT_DELAY:
                    statuses[index] = status
                    if status:
                        if self.previousStatusesCount == 0:
                            self.previousStatusesCount = self.previousStatusesCount + 1
                        self.currentStatusesCount = self.currentStatusesCount + 1
                    times[index] = None
                continue

            if times[index] is None and self.status_changed(statuses, index, status):
                times[index] = position_in_seconds

        for index, p in enumerate(coordinates_data):
            coordinates = self._coordinates(p)

            color = COLOR_GREEN if statuses[index] else COLOR_BLUE
            draw_contours(new_frame, coordinates, str(p["id"] + 1), COLOR_WHITE, color)
                    
                    
        for index, p in enumerate(coordinates_data):
            if statuses[index]:
                #print(str(index + 1))
                zones.append(index + 1)
                #self.waterLevelSlots.get_water_level_slots()[index].set_water_level(False)
            #else:
                #print('OFF') 
                #self.waterLevelSlots.get_water_level_slots()[index].set_water_level(True)
                
        
        if self.previousStatusesCount != self.currentStatusesCount:
            self.previousStatusesCount = self.currentStatusesCount
            #print(str(self.area.get_area_to_light(zones)))
            self.count = self.count + 1;
            self.list.append(str(self.area.get_area_to_light(zones)))
            if self.count == 13:
                #print(mode(self.list))
                self.persistStreetLightData(mode(self.list))
                self.count = 0
                self.list = []
                '''
                for item in set(self.list):
                    print(item +" - item "+str(self.list.count(item))+" times")
                print("end---end----end")
                '''
                
                
        else:
            self.previousStatusesCount = 0
        #print("green - " + str(self.countFalse))
        #print("red - " + str(self.countTrue))
                    
        return new_frame, self.area
    
    def persistStreetLightData(self, condition):        
        sql = ('insert into smart_street_lighting(area_1, area_2, precise_counter) ' +
               'values(:area_1, :area_2, :precise_counter)')
        
        try:
            # establish a new connection
            with cx_Oracle.connect('gsmuser/oracle@//localhost:1521/orcl') as connection:
                # create a cursor
                with connection.cursor() as cursor:
                    
                    # execute the insert statement
                    if condition == 'A1:OFF,A2:OFF':
                        cursor.execute(sql, ['OFF', 'OFF', time.time_ns()])
                    elif condition == 'A1:ON,A2:ON':
                        cursor.execute(sql, ['ON', 'ON', time.time_ns()])
                    elif condition == 'A1:ON,A2:OFF':
                        cursor.execute(sql, ['ON', 'OFF', time.time_ns()])
                    elif condition == 'A1:OFF,A2:ON':
                        cursor.execute(sql, ['OFF', 'ON', time.time_ns()])
                    # commit work
                    connection.commit()
        except cx_Oracle.Error as error:
            print('SQL Error occurred:')
            print(error)  
        
    def __apply(self, grayed, index, p):
        coordinates = self._coordinates(p)
        logging.debug("points: %s", coordinates)

        rect = self.bounds[index]
        logging.debug("rect: %s", rect)

        roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        laplacian = open_cv.Laplacian(roi_gray, open_cv.CV_64F)
        logging.debug("laplacian: %s", laplacian)

        coordinates[:, 0] = coordinates[:, 0] - rect[0]
        coordinates[:, 1] = coordinates[:, 1] - rect[1]

        status = np.mean(np.abs(laplacian * self.mask[index])) < MotionDetector.LAPLACIAN
        logging.debug("status: %s", status)

        return status

    @staticmethod
    def _coordinates(p):
        return np.array(p["coordinates"])

    @staticmethod
    def same_status(coordinates_status, index, status):
        return status == coordinates_status[index]

    @staticmethod
    def status_changed(coordinates_status, index, status):
        return status != coordinates_status[index]


class CaptureReadError(Exception):
    pass
