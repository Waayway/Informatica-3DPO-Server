from typing import Union
from loguru import logger
from . import Data

class LobbyReadyToGameData(Data):
    def __init__(self) -> None:
        super().__init__()
        self.players: list = []
        self.playersDoneLoading: int = 0

    # This class will import and export data that is needed for sending players from the lobby as soon as they are done in there to the actual game
    def importData(self, data: Union[str, dict]) -> None:
        super().importData(data)
        self.players = self.data["players"]
        if "playersdoneloading" in self.data:
            self.playersDoneLoading = self.data["playersdoneloading"]
        logger.debug("Got Lobby to game data: "+str(self.data))

    def exportData(self, string: bool = False) -> Union[str, dict]:
        self.data = {"players": self.players, "playersdoneloading": self.playersDoneLoading}
        return super().exportData(string)