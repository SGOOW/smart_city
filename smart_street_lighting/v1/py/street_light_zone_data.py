class Area:
    def __init__(self):
        self._isOn = False
        self._isOff = False
        
    def get_area_to_light(self, green_zones_in_total_area):
       total_area_zones = [1, 2, 3, 4, 5, 6, 7, 8]
       area_1 = [1, 2, 3, 4]
       area_2 = [5, 6, 7, 8]
       red_zones_in_total_area = (list(set(total_area_zones) - set(green_zones_in_total_area)))
       
       if len(red_zones_in_total_area) == 0:
           return 'A1:OFF,A2:OFF'
       else:
           red_zones_in_area_1 = list(set(red_zones_in_total_area) & set(area_1))
           red_zones_in_area_2 = list(set(red_zones_in_total_area) & set(area_2))
           if len(red_zones_in_area_1) > 0 and len(red_zones_in_area_2) > 0:
               return 'A1:ON,A2:ON'
           else:
               if len(red_zones_in_area_1) > 0:
                   return 'A1:ON,A2:OFF'
               else:
                   if len(red_zones_in_area_2) > 0:
                       return 'A1:OFF,A2:ON'