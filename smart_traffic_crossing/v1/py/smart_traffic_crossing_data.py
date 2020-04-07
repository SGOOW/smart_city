class Area:
    def __init__(self):
        self._isOn = False
        self._isOff = False
        
    def get_vehicle_status(self, green_zones_in_total_area):
       total_pedestrian_zones = [1]
       red_zones_in_total_area = (list(set(total_pedestrian_zones) - set(green_zones_in_total_area)))
       
       if len(red_zones_in_total_area) == 0:
           return 'VEHICLE:OFF'
       else:
          return 'VEHICLE:ON'