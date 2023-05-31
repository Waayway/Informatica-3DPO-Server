from loguru import logger
from typing import Union
import json
from . import Data


class VelocityData(Data):
    # Stores velocity and position
    vel = {
        "x": 0,
        "y": 0,
        "z": 0
    }
    pos = {
        "x": 0,
        "y": 0,
        "z": 0
    }
    rot = {
        "x": 0,
        "y": 0,
        "z": 0
    }
    anim = {
        "left_right": 0,
        "walking": False,
        "running": False
    }

    def importData(self, data: Union[str, dict]) -> None:
        super().importData(data)
        if "pos" in self.data:
            self.pos = self.data['pos']
        if "vel" in self.data:
            self.vel = self.data['vel']
        if "rot" in self.data:
            self.rot = self.data["rot"]
        if "anim" in self.data:
            self.anim = self.data["anim"]
        # logger.debug("Got velocity data: "+str(self.data))

    def exportData(self, string: bool = False) -> Union[str, dict]:
        self.data = {"vel": self.vel, "pos": self.pos,
                     "rot": self.rot, "anim": self.anim}
        logger.debug("Sending Anim_data: " + json.dumps(self.data))
        return super().exportData(string)
