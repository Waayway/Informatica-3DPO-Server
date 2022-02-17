from typing import Union
import json

class Data:
    def __init__(self) -> None:
        pass
    
    def importData(self, data: Union[str, dict]) -> None:
        if type(data) == str:
            data = json.loads(data)
        self.data = data
    
    def exportData(self, string: bool = False) -> Union[str, dict]:
        if string:
            return json.dumps(self.data)
        return self.data