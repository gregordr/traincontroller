from multiprocessing import Event
import socket
from threading import Thread
from typing import Callable, Dict, List
import reactivex as rx
from reactivex import operators as op
import Train

class Controller():
    SPEED = 0x08
    DIRECTION = 0x0A
    SETTINGS = 0x00

    trains : Dict[Train.Train.tIDType,Train.Train] = {}
    speedCallbacks : Dict[Train.Train.tIDType, List[Callable[[int], None]]] = {}
    speedSources : Dict[Train.Train.tIDType, 'rx.Source'] = {}
    speedObservers : Dict[Train.Train.tIDType, 'rx.Observer'] = {}

    def __init__(self, stationIP:str, ownIP:str) -> None:
        self.SENDIP = stationIP
        self.LISETENIP = ownIP
        self.SENDPORT = 15731
        self.LISTENPORT = 15730

        self.socksnd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sockrcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockrcv.bind((self.LISETENIP, self.LISTENPORT))

        
        listenThread = Thread(target = self.__listen)
        listenThread.daemon = True
        listenThread.start()

    def send(self, inp):
        assert(len(inp) == 13)
        some_bytes = bytearray(inp)
        msg = bytes(some_bytes)

        self.socksnd.sendto(msg, (self.SENDIP, self.SENDPORT))

    def registerTrain(self, train : Train):
        self.trains[train.tID] = train

        self.speedSources[train.tID] = rx.create(lambda observer, _: self.speedObservers.update({train.tID: observer}))

    def __listen(self):
        print("start listen")
        while True:
            data = self.sockrcv.recvfrom(1024)
            res = data[0].hex()

            prio = res[0:1]
            command = int(res[2:4], base=16)//2*2
            isResponse = int(res[3:4], base=16)%2==1
            dlc = res[9:10]

            if(command == self.SPEED and isResponse):
                tID = (int(res[10:12], base=16), int(res[12:14], base=16), int(res[14:16], base=16), int(res[16:18], base=16))
                speed = int(res[18:22], base = 16)
                if tID in self.trains:
                    self.trains[tID].speed = speed
                if tID in self.speedObservers:
                    self.speedObservers[tID].on_next(speed)

            # print(f"Prio: {prio} \
            # Command: {hex(command)} \
            # Resp: {isResponse} \
            # DLC: {dlc} \
            # {res[10:12]} {res[12:14]} {res[14:16]} {res[16:18]} {res[18:20]} {res[20:22]} {res[22:24]} {res[24:26]}\
            # ")


    def stop(self):
        self.send(
            [0,0,0x03,self.SETTINGS,
            5,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0,0,0])

    def go(self):
        self.send(
            [0,0,0x03,self.SETTINGS,
            5,
            0x00,
            0x00,
            0x00,
            0x00,
            0x01,
            0,0,0])

    def halt(self):
        self.send(
            [0,0,0x03,self.SETTINGS,
            5,
            0x00,
            0x00,
            0x00,
            0x00,
            0x02,
            0,0,0])

    def setSpeed(self, speed, tID):
        self.send(
            [0x00,self.SPEED,0x03,0x00,
            6,
            *tID,
            speed//256,
            speed%256,0,0])

    def askForSpeed(self, tID, timeout = 0):
        assert(len(tID)==4)

        lclspeed = None

        def assign(speed):
            ev.set()
            nonlocal lclspeed
            lclspeed = speed

        ev = Event()
        if timeout != 0:
            self.speedSources[tID].pipe(op.first()).subscribe(assign)

        self.send(
            [0x00,self.SPEED,0x03,0x00,
            4,
            *tID,
            0,0,
            0,0])

        if(timeout != 0):
            success = ev.wait(timeout)
            return (success, lclspeed)

    def changeDirection(self, tID):
        self.send(
            [0x00,self.DIRECTION,0x03,0x00,
            5,
            *tID,
            0x03,
            0,0,0])
