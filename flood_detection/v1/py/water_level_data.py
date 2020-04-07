import numpy

class WaterLevelSlot:
    def __init__(self, waterLevelSlotName):
        self._waterLevelSlotName = waterLevelSlotName
        self._hasLevelReached = False
        
    # getter method 
    def get_water_level_slot_name(self): 
        return self._waterLevelSlotName 
      
    def set_water_level(self, isWaterLevelReached): 
        self._hasLevelReached = isWaterLevelReached
    
    def get_water_level(self):
        return self._hasLevelReached
        
class WaterLevelSlots:
    LEVEL_REACHED_MSG = 'THE WATER IS AT : '

    def __init__(self, numberOfWaterLevelSlots):
        self._numberOfWaterLevelSlots = numberOfWaterLevelSlots
        
        self._waterLevelSlots = numpy.empty(numberOfWaterLevelSlots, dtype=object)
   
        for count in range(0, numberOfWaterLevelSlots):
            waterLevelSlot = WaterLevelSlot('LEVEL_' + str(count + 1))
            self._waterLevelSlots[count] = waterLevelSlot
    
    def get_water_level_slots(self):
        return self._waterLevelSlots
    
    def get_current_water_level(self):
        if self._waterLevelSlots[0].get_water_level() and self._waterLevelSlots[1].get_water_level() and self._waterLevelSlots[2].get_water_level():
            return self._waterLevelSlots[2].get_water_level_slot_name()
        if self._waterLevelSlots[0].get_water_level() and self._waterLevelSlots[1].get_water_level():
            return self._waterLevelSlots[1].get_water_level_slot_name()
        if self._waterLevelSlots[0].get_water_level():
            return self._waterLevelSlots[0].get_water_level_slot_name()
        return 'NOT APPLICABLE'       
                