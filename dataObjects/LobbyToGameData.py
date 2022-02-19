from ctypes import Union
from loguru import logger
from . import Data

class LobbyReadyToGameData(Data):


    # This class will import and export data that is needed for sending players from the lobby as soon as they are done in there to the actual game
    def importData(self, data: Union[str, dict]) -> None:
        super().importData(data)
        logger.debug("Got Lobby to game data: "+str(self.data))

    def exportData(self, string: bool = False) -> Union[str, dict]:
        self.data = {"vel": self.vel, "pos": self.pos}
        return super().exportData(string)