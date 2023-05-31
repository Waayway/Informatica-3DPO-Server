from ast import Global
from datetime import datetime, timedelta
import random
from tornado import httputil
from loguru import logger
from typing import Any
from dataObjects.GameOverData import GameOverData
from dataObjects.LobbyToGameData import LobbyReadyToGameData
from dataObjects.velocityData import VelocityData
from dataObjects.LobbyReady import LobbyReady
from functions import without_keys
import tornado.websocket
import json
import uuid


class GlobalData:
    # GlobalData for this file. just simple things that are handier to store here
    data = {}
    lobby_to_game_data = LobbyReadyToGameData()
    ws_connections = []
    lobbyReadyList: list = []
    isLobbyStarted: bool = False
    isLobbyReady: bool = False
    wasLobbyReady: bool = False
    numConnected: int = 0
    startedTimerMoment: datetime = datetime.now()
    LobbyLoadedList: list = []
    GameTimerStart: datetime = datetime.now()
    game_over_data: GameOverData = GameOverData()
    seeker: str = ""
    map_used: int = 0

class WebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs: Any) -> None:
        super().__init__(application, request, **kwargs)
        # Data used in this Class
        self.velData = VelocityData()
        self.numid = 0
        self.first_message = True
        self.name = ""

        self.done_loading = False
        
        self.is_found = False
        
    
    def open(self):
        if GlobalData.isLobbyStarted:
            self.close(1000,"Lobby has already started")
        # Generate an Id and log it to console
        self.id = str(uuid.uuid4())
        GlobalData.ws_connections.append(self)
        logger.debug(f"Adding {self.id} to ws_connections")
        logger.debug(GlobalData.ws_connections)
        logger.info("WebSocket opened, id: " + self.id)
        # Write the id back to the client for saving on the client
        self.write_message(self.id)
        # setNumid
        self.numid = len(GlobalData.lobbyReadyList)
        self.LobbyReady = LobbyReady(self.id)
        GlobalData.lobbyReadyList.append(self.LobbyReady)
        #send Lobby Data so the client can place current players in the lobby
        self.send_lobby_message()

    def send_lobby_message(self):
        data = {"players": {}, "map": GlobalData.map_used}
        timeDelta = datetime.now() - GlobalData.startedTimerMoment
        if timeDelta < timedelta(seconds=5):
            data["timer"] = timeDelta.total_seconds()
        for i in GlobalData.ws_connections:
            # logger.debug(f"Name of {i.id} is: {i.name}")
            data["players"][i.id] = {"lobbydata": i.LobbyReady.getData(), "name": i.name}
        logger.debug("Data To send to the clients: 0" + str(data))
        for i in GlobalData.ws_connections:
            i.write_message("0"+json.dumps(data))

    def send_player_data(self, data):
        newData = without_keys(data, [self.id])
        self.write_message("1"+json.dumps(newData))
    
    def send_lobbyloaded_data(self):
        data = {}
        data["playersdoneloading"] = len(GlobalData.LobbyLoadedList)
        logger.debug("Data to send to the clients: 3"+str(data))
        for i in GlobalData.ws_connections:
            i.write_message("3"+json.dumps(data))

    def on_message(self, message):
        if type(message) == bytes:
            message = message.decode('UTF-8')
        logger.debug("Got Data from client: "+self.id+", "+str(message))
        if self.first_message:
            data = json.loads(message)
            self.name = data["name"]
            if len(GlobalData.ws_connections) <= 1:
                GlobalData.map_used = data["prefered_map"]
            self.first_message = not self.first_message
            self.send_lobby_message()
        # checks the data the server got from client for data type, types are descriped in README.md
        if str(message).startswith("0"):
            # Get message and load into the LobbyReady Object
            message = str(message).removeprefix("0")
            data = json.loads(message)
            self.LobbyReady.setData(data[self.id])
            GlobalData.lobbyReadyList[self.numid] = data[self.id] 
            check_if_lobby_all_ready()
            self.send_lobby_message()

        elif str(message).startswith("1"):
            # Decifer data and import the data
            message = str(message).removeprefix("1")
            if message == "timer":
                check_if_lobby_all_ready()
            elif message == "gametimer":
                current_time_over_time = GlobalData.lobby_to_game_data.is_current_time_over_time()
                if current_time_over_time:
                    send_game_over(True)
        elif str(message).startswith("2"):
            message = str(message).removeprefix("2")
            if message == "true":
                self.done_loading = True
                GlobalData.LobbyLoadedList.append(self.id)
            else:
                self.done_loading = False
                GlobalData.LobbyLoadedList.remove(self.id)
            self.send_lobbyloaded_data()
        elif str(message).startswith("4"):
            self.velData.importData(message.removeprefix("4"))
            dataToSend = {}
            for i in GlobalData.ws_connections:
                if i.id == self.id: continue
                dataToSend[i.id] = i.velData.exportData()
            logger.debug("Sending data to client 4"+json.dumps(dataToSend))
            self.write_message("4"+json.dumps(dataToSend))
        elif str(message).startswith("5"):
            GlobalData.game_over_data.importData(message.removeprefix("5"))
            check_if_everybody_is_found()
            data = json.loads(message.removeprefix("5"))
            for i in GlobalData.ws_connections:
                i.write_message("6"+data["playerFound"])

    def on_close(self):
        logger.info("WebSocket closed, id: " + self.id)
        GlobalData.ws_connections.remove(self)
        if self.id in GlobalData.LobbyLoadedList:
            GlobalData.LobbyLoadedList.remove(self.id)
        if len(GlobalData.ws_connections) < 1:
            reset()
    
    def send_lobby_to_game_data():
        start_game_timer()
        data = GlobalData.lobby_to_game_data
        data.gameTimerStart = GlobalData.GameTimerStart
        data.chosenplayer = choose_seeker()
        for i in GlobalData.ws_connections:
            data.players.append(i.id)
            data.playerNames[i.id] = i.name
            data.playersDoneLoading += int(i.done_loading)
        logger.debug(f"Data to send to the clients: 2{data}")
        for i in GlobalData.ws_connections:
            i.write_message("2"+data.exportData(True))
        GlobalData.isLobbyStarted = True
    
def check_if_everybody_is_found():
    numPeopleFound = len(GlobalData.game_over_data.playersFound)
    
    if numPeopleFound+1 >= len(GlobalData.ws_connections):
        send_game_over(hiders=False)

def choose_seeker():
    return GlobalData.ws_connections[random.randrange(len(GlobalData.ws_connections))].id

def send_game_over(hiders: bool):
    GlobalData.game_over_data.hiders = hiders
    GlobalData.game_over_data.importData(GlobalData.lobby_to_game_data.exportData())
    data = GlobalData.game_over_data.exportData(True)
    GlobalData.isLobbyReady = False
    GlobalData.isLobbyStarted = False
    GlobalData.startedTimerMoment = datetime.now()
    GlobalData.GameTimerStart = datetime.now()
    for i in GlobalData.ws_connections:
        i.write_message("5"+data)
    reset()
        
def reset():
    GlobalData.data = {}
    GlobalData.lobby_to_game_data = LobbyReadyToGameData()
    GlobalData.isLobbyStarted = False
    GlobalData.isLobbyReady = False
    GlobalData.wasLobbyReady = False
    GlobalData.startedTimerMoment = datetime.now()
    GlobalData.LobbyLoadedList = []
    GlobalData.GameTimerStart = datetime.now()
    GlobalData.game_over_data = GameOverData()
    GlobalData.seeker = ""

    for i in GlobalData.lobbyReadyList:
        i = False
    for i in GlobalData.ws_connections:
        i.is_found = False
        i.done_loading = False


def start_game_timer():
    GlobalData.GameTimerStart = datetime.now()

def check_if_lobby_all_ready():
    isLobbyReady = True
    for i in GlobalData.lobbyReadyList:
        logger.debug(i)
        if not i: 
            isLobbyReady = False
            break
    if isLobbyReady == True and not GlobalData.wasLobbyReady:
        GlobalData.startedTimerMoment = datetime.now()
        GlobalData.wasLobbyReady = isLobbyReady
    elif isLobbyReady and GlobalData.wasLobbyReady:
        if datetime.now() - GlobalData.startedTimerMoment > timedelta(seconds=5) and GlobalData.wasLobbyReady:
            GlobalData.isLobbyStarted = True
            GlobalData.startedTimerMoment = datetime.now() - timedelta(hours=5)
            WebSocket.send_lobby_to_game_data()
    elif not isLobbyReady:
        GlobalData.wasLobbyReady = False

    GlobalData.isLobbyReady = isLobbyReady


