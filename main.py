import time
import atexit

import Controller
import Train

UDP_IP = "10.0.0.1"
OWN_IP = "10.0.0.147"
UDP_PORT = 15731

if __name__ == "__main__":
    ctr = Controller.Controller(UDP_IP, OWN_IP)
    ctr.go()

    train = Train.Train((0x00,0x00,0x40,0x0a), ctr)
    atexit.register(ctr.halt)
    while(True):
        print(train.speed)
        train.changeDirection()
        train.setSpeed(400)
        time.sleep(0.2)
        print(train.speed)
        time.sleep(2)
        
        print(train.speed)
        train.setSpeed(100)
        time.sleep(2)