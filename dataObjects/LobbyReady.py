from loguru import logger
from typing import Union
import json
from . import Data


class LobbyReady(Data):
    ready: bool = False
    id: str = ""

    def initialize(self, id: str, ready: bool = False):
        self.ready = ready
        self.id = id

    def setData(self,ready: bool):
        self.ready = ready
    
    def getData(self):
        return self.ready