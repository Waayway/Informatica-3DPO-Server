from datetime import datetime, timedelta
import time
from typing import Union
from loguru import logger
from . import Data

class LobbyReadyToGameData(Data):
    def __init__(self) -> None:
        super().__init__()
        self.players: list = []
        self.playerNames: dict = {}
        self.playersDoneLoading: int = 0
        self.chosenplayer: str = ""
        self.gameTimerStart: datetime = datetime.now()
        self.gameTimerTotalSeconds: int = 60*5

    # This class will import and export data that is needed for sending players from the lobby as soon as they are done in there to the actual game
    def importData(self, data: Union[str, dict]) -> None:
        super().importData(data)
        self.players = self.data["players"]
        if "playersdoneloading" in self.data:
            self.playersDoneLoading = self.data["playersdoneloading"]
        logger.debug("Got Lobby to game data: "+str(self.data))

    def exportData(self, string: bool = False) -> Union[str, dict]:
        timer = (datetime.now() - self.gameTimerStart).total_seconds()
        self.data = {"players": self.players,"playerNames": self.playerNames, "playersdoneloading": self.playersDoneLoading, "timer": timer, "totalTime": self.gameTimerTotalSeconds,"chosenplayer": self.chosenplayer}
        return super().exportData(string)
    
    def is_current_time_over_time(self):
        cur_time = datetime.now()
        return cur_time - self.gameTimerStart >= timedelta(seconds=self.gameTimerTotalSeconds)
