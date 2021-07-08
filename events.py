# import threading
# 

# event = threading.event()

# flag = 1 means other person can use 
# event.set()
# event.clear()

# blocks the thread if not set
# event.wait()

# event.is_set() 

import queue
import threading
import numpy as np
import time

def flag():
    time.sleep(3) #3seconds
    
    event.set()

    print('starting countdwn')

    time.sleep(20)

    print('event is cleared')

    event.clear()

def start_operations():

    event.wait() # if event is not set it will wait
    i = 0
    while event.is_set():
        print('{} starting random integer task'.format(i))
        i+=1
        x = np.random.randint(1,30)

        time.sleep(.5)

        if x == 29:
            print('true')

    print('Event has been cleared , raandom operation stops')

event = threading.Event()
t1 = threading.Thread(target=flag)
t2 = threading.Thread(target=start_operations)

t1.start()
t2.start()


