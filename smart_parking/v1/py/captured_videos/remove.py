import os
import time
import shutil

timeElapsed = 20

try:
    while True:
        now = time.time()
        for r,d,f in os.walk(os.getcwd()):
            for dir in d:   
                timestamp = os.path.getmtime(os.path.join(r,dir))
                if now-timeElapsed > timestamp:
                    try:
                        print ("removing ",os.path.join(r,dir))
                        shutil.rmtree(os.path.join(r,dir))
                    except Exception as e:
                        print (e)
                        pass
                    else: 
                        print ("removed directory - " + dir)
except KeyboardInterrupt:
    print('the remove program has been stopped!')
