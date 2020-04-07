import numpy
import json
import time

class CarParkSlot:
    def __init__(self, carParkSlotName, creationDateTime, modifiedDateTime):
        self._carParkSlotName = carParkSlotName
        self._isOccupied = False
        self._creationDateTime = time.mktime(creationDateTime.timetuple()) + creationDateTime.microsecond / 1E6
        self._modifiedDateTime = modifiedDateTime
        
    # getter method 
    def get_name(self): 
        return self._carParkSlotName 
      
    def set_occupancy(self, isOccupied): 
        self._isOccupied = isOccupied
    
    def get_occupancy(self):
        return self._isOccupied
    
    def get_creationTime(self):
        return self._creationDateTime
    
    def set_modifiedTime(self, modifiedDateTime):
        self._modifiedDateTime = modifiedDateTime
    
    def get_modifiedTime(self):
        return self._modifiedDateTime
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        #return json.dumps(self)
        
class CarParkData:
    TOTAL_NUMBER_OF_SLOTS = 'TOTAL NUMBER OF PARKING SLOT(S) : '
    CARPARK_FULL_MESSAGE = 'CAR PARK IS FULLY OCCUPIED'
    CARPARK_AVAILABLE_MESSAGE = 'CAR PARK IS AVAILABLE'
    NUMBER_OF_CARPARK_SLOTS_AVAILABLE = 'NUMBER OF PARKING SLOT(S) AVAILABLE : '

    def __init__(self, carParkName, numberOfSlots, creationTime):
        self._carParkName = carParkName
        self._numberOfSlots = numberOfSlots
        self._creationTime = creationTime
        
        self._carParkSlots = numpy.empty(numberOfSlots, dtype=object)
        self._availableSlots = 0
        self._occupiedSlots = 0
        
        for count in range(0, numberOfSlots):
            carParkSlot = CarParkSlot('car_park_slot_' + str(count), creationTime, creationTime)
            self._carParkSlots[count] = carParkSlot
    
    def get_available_carpark_slots(self):
        availableSlotsCount = 0
        for count in range(0, self._numberOfSlots):
            if not self._carParkSlots[count].get_occupancy():
                availableSlotsCount = availableSlotsCount + 1
        self._availableSlots = availableSlotsCount
        return availableSlotsCount
    
    def get_occupied_carpark_slots(self):
        occupiedSlotsCount = 0
        for count in range(0, self._numberOfSlots):
            if self._carParkSlots[count].get_occupancy():
                occupiedSlotsCount = occupiedSlotsCount + 1
        self._occupiedSlots = occupiedSlotsCount
        return occupiedSlotsCount
    
    def is_carpark_full(self):
        return self._numberOfSlots == self.get_occupied_carpark_slots()
    
    def is_carpark_available(self):
        return self._availableSlots < self.get_available_carpark_slots()
    
    def is_carpark_empty(self):
        return self._availableSlots < self.get_available_carpark_slots()
    
    def get_carpark_name(self):
        return self._carParkName
    
    def get_carpark_slots(self):
        return self._carParkSlots
    
    def get_total_car_park_slots(self):
        return self._numberOfSlots
    
    def get_carpark_creation_time(self):
        return self._creationTime