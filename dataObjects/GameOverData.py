from typing import Union
from loguru import logger
from . import Data

class GameOverData(Data):
    def __init__(self) -> None:
        super().__init__()
        self.players: list = []
        self.playerNames: dict = {}
        self.hiders: bool = False
        self.playersFound: list = []
        
    # This class will import and export data that is needed for sending players from the game as soon as they are done in there to the lobby
    def importData(self, data: Union[str, dict]) -> None:
        super().importData(data)
        if "players" in self.data:
            self.players = self.data["players"]

        if "playerNames" in self.data:
            self.playerNames = self.data["playerNames"]
        
        if "playerFound" in self.data:
            if not self.data["playerFound"] in self.playersFound:
                self.playersFound.append(self.data["playerFound"])
        
        if "hiders" in self.data:
            self.hiders = self.data["hiders"]
        

    def exportData(self, string: bool = False) -> Union[str, dict]:
        self.data = {"players": self.players,"playerNames": self.playerNames, "hiders": self.hiders, "playersFound": self.playersFound}
        return super().exportData(string)
