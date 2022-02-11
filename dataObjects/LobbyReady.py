from loguru import logger
from typing import Union
import json
from . import Data


class LobbyReady(Data):
    ready: bool = False
    def setData(self,ready: bool):
        self.ready = ready
    
    def getData(self):
        return self.ready