# import libraries
from vidgear.gears import CamGear
import cv2

stream = CamGear(source='https://youtu.be/CsdXxAxzWjY', y_tube =True,  time_delay=1, logging=True).start() # YouTube Video URL as input

# infinite loop
while True:

    frame = stream.read()
    # read frames

    # check if frame is None
    if frame is None:
        #if True break the infinite loop
        break

    # do something with frame here

    cv2.imshow("Output Frame", frame)
    # Show output window

    key = cv2.waitKey(1) & 0xFF
    # check for 'q' key-press
    if key == ord("q"):
        #if 'q' key-pressed break out
        break

cv2.destroyAllWindows()
# close output window

stream.stop()
# safely close video stream.