import cv2 as open_cv
import numpy as np
import logging
from drawing_utils import draw_contours
from colors import COLOR_GREEN, COLOR_WHITE, COLOR_BLUE
import time
import cx_Oracle



class MotionDetector:
    LAPLACIAN = 1.4
    DETECT_DELAY = 1

    def __init__(self, coordinates, start_frame, carPark):
        #self.video = video
        self.coordinates_data = coordinates
        self.start_frame = start_frame
        self.contours = []
        self.bounds = []
        self.mask = []
        self.carPark = carPark
        self.previousStatusesCount = 0
        self.currentStatusesCount = 0

    def detect_motion(self, video, hasVideoChanged):
         frames = {}
         
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
    
            count = 0;
            while capture.isOpened():
                result, frame = capture.read()
                if not result:
                    #raise CaptureReadError("Error reading video capture on frame %s" % str(frame))
                    capture.release()
                    continue
                else:
                    new_frame = self.__process_algo_per_frame(frame, result, capture, coordinates_data, times, statuses)
                    frames[count] = new_frame
                    count = count + 1
                
            capture.release()
            return frames, self.carPark
    
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
            
            if self.carPark.get_carpark_slots()[index] is not None:
                if color == COLOR_GREEN:
                    self.carPark.get_carpark_slots()[index].set_occupancy(False)
                    
                else:
                    self.carPark.get_carpark_slots()[index].set_occupancy(True)
                    
        if self.previousStatusesCount != self.currentStatusesCount:
            self.previousStatusesCount = self.currentStatusesCount
            self.persistToDB()
            
        return new_frame, self.carPark
    
    def persistToDB(self):
        json = '['
        for carpark_slot in self.carPark.get_carpark_slots():
            json = json + carpark_slot.toJSON() + ','
                                    
        json = json[:-1]
        json = json + ']'
        json = json.replace('\n','');
        json = json.replace('\t','');
        json = json.replace('\r','');
        json = json.replace("\'",'');
        json = json.replace('    ', '');         
        self.persistSmartParkRealTime(None, None, self.carPark.get_total_car_park_slots(), 
                                                                     self.carPark.get_available_carpark_slots(), json, None, None)
    def persistSmartParkRealTime(self, carParkId, createDateTime, total_slots, available_slots, 
                             carpark_status, modifiedDateTime, carpark_image):
    
        sql = ('insert into smart_parking(carpark_id, created_date_time, total_slots, ' + 
               'available_slots, carpark_status, modified_date_time, carpark_image, precise_counter) ' +
               'values(:carpark_id, :created_date_time, :total_slots, :available_slots, ' +
               ':carpark_status, :modified_date_time, :carpark_image, :precise_counter)')
        try:
            # establish a new connection
            with cx_Oracle.connect('gsmuser/oracle@//localhost:1521/orcl') as connection:
                # create a cursor
                with connection.cursor() as cursor:
                    # execute the insert statement
                    cursor.execute(sql, [carParkId, createDateTime, total_slots, available_slots, carpark_status, 
                                         modifiedDateTime, carpark_image, time.time_ns()])
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
