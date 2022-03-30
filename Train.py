from typing import Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Controller import Controller

class Train():
    tIDType = Tuple[str,str, str, str]
    def __init__(self, tID:tIDType, ctr : 'Controller') -> None:
        self.tID = tID
        self.ctr = ctr
        self.speed = 0
        self.ctr.registerTrain(self)
        self.ctr.askForSpeed(tID, None)
        self.ctr.askForSpeed(tID, None)

    def setSpeed(self, speed):
        self.ctr.setSpeed(speed, self.tID)

    def changeDirection(self):
        self.ctr.changeDirection(self.tID)
